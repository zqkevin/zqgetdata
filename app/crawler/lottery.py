# -*- coding: utf-8 -*-
"""
数字彩票数据采集器
实现获取数字彩票开奖信息并记录到数据库的功能
"""
import os
import sys
from datetime import datetime
from typing import Dict, List

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.common.req_sporttery_api import SportteryAPI
from app.log import lottery_log as log
from app.database import localdb, DigitalLotteryDraw, DigitalLotteryPrize


class LotteryDataCollector:
    """
    数字彩票数据采集器
    用于获取三种彩票（大乐透、排列 3、七星彩）的开奖信息并记录到数据库
    """
    
    def __init__(self):
        self.api_client = SportteryAPI()
        # 彩种映射表，包含彩票代码
        self.lottery_mapping = {
            'dlt': {
                'lottery_name': '超级大乐透',
                'code': '85'
            },
            'pl3': {
                'lottery_name': '排列 3',
                'code': '35'
            },
            'pl5': {
                'lottery_name': '排列 5',
                'code': '350133'
            },
            'qxc': {
                'lottery_name': '七星彩',
                'code': '04'
            }
        }
    
    def _convert_datetime(self, datetime_str):
        """将字符串转换为 datetime 对象"""
        if not datetime_str:
            return None
        
        try:
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%d',
                '%Y/%m/%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            log.warning(f"无法解析日期格式：{datetime_str}")
            return None
        except Exception as e:
            log.error(f"日期转换错误：{str(e)}")
            return None
    
    def _save_prize_levels(self, draw_id, prize_levels):
        """保存奖级信息"""
        try:
            for prize_data in prize_levels:
                prize = DigitalLotteryPrize(
                    draw_id=draw_id,
                    prize_level=prize_data.get('prizeLevel'),
                    award_type=prize_data.get('awardType'),
                    group=prize_data.get('group'),
                    lottery_condition=prize_data.get('lotteryCondition'),
                    stake_count=prize_data.get('stakeCount'),
                    stake_amount=prize_data.get('stakeAmount'),
                    stake_amount_format=prize_data.get('stakeAmountFormat'),
                    total_prize_amount=prize_data.get('totalPrizeamount'),
                    sort=prize_data.get('sort')
                )
                
                localdb.add(prize, close=False)
            
            log.info(f"成功保存{len(prize_levels)}条奖级信息")
        except Exception as e:
            log.error(f"保存奖级信息时出错：{str(e)}")
            raise
    
    def _save_lottery_data(self, lottery_type, data):
        """保存彩种数据到数据库"""
        try:
            # 检查是否是错误响应
            if isinstance(data, dict) and 'error' in data:
                log.warning(f"{lottery_type} API返回错误: {data['error']}")
                return False
            
            # 验证必要字段是否存在
            draw_num = data.get('lotteryDrawNum')
            if not draw_num:
                log.warning(f"{lottery_type} API返回数据缺少期号，原始数据: {data}")
                return False
            
            model_info = self.lottery_mapping.get(lottery_type)
            if not model_info:
                log.error(f"未知的彩种类型：{lottery_type}")
                return False
            
            lottery_name = model_info['lottery_name']
            lottery_code = model_info['code']
            
            # 检查是否已存在
            existing = localdb.query(DigitalLotteryDraw).filter(
                DigitalLotteryDraw.lottery_code == lottery_code,
                DigitalLotteryDraw.draw_num == draw_num
            ).first()
            
            if existing:
                log.info(f"{lottery_name}第{draw_num}期已存在，跳过")
                return False
            
            # 创建新记录 - 使用已验证的 draw_num
            draw = DigitalLotteryDraw(
                lottery_code=lottery_code,
                lottery_name=lottery_name,
                draw_num=draw_num,
                draw_time=self._convert_datetime(data.get('lotteryDrawTime')),
                draw_result=data.get('lotteryDrawResult'),
                unsorted_draw_result=data.get('unsortedLotteryDrawResult'),
                pool_balance_after_draw=data.get('poolBalanceAfterdraw'),
                sale_begin_time=self._convert_datetime(data.get('saleBeginTime')),
                sale_end_time=self._convert_datetime(data.get('saleEndTime')),
                draw_pdf_url=data.get('drawPdfUrl'),
                is_verified=data.get('isVerified', 0),
                rule_type=data.get('ruleType'),
                equipment_count=data.get('equipmentCount'),
                notice_flag=data.get('noticeFlag'),
                notice_show_flag=data.get('noticeShowFlag')
            )
            
            localdb.add(draw, close=False)
            localdb.commit()
            
            # 保存奖级信息
            prize_levels = data.get('prizeLevelList', [])
            if prize_levels:
                self._save_prize_levels(draw.id, prize_levels)
                localdb.commit()
            
            log.info(f"成功保存{lottery_name}第{draw_num}期数据")
            return True
            
        except Exception as e:
            log.error(f"保存彩种数据时出错：{str(e)}")
            localdb.rollback()
            return False
    
    def fetch_and_save_lottery_data(self, lottery_types=None) -> int:
        """
        获取并保存彩票数据
        
        Args:
            lottery_types: 要获取的彩种列表，如果为 None 则获取所有彩种
            
        Returns:
            int: 成功保存的记录数
        """
        if lottery_types is None:
            lottery_types = list(self.lottery_mapping.keys())
        
        saved_count = 0
        
        try:
            # 使用 get_multi_lottery_data 批量获取所有彩种数据
            log.info(f'开始获取 {len(lottery_types)} 个彩种数据...')
            data = self.api_client.get_multi_lottery_data(lottery_types)
            
            if not data:
                log.warning('API返回数据为空')
                return 0
            
            # 遍历每个彩种的数据
            for lottery_type in lottery_types:
                if lottery_type not in data or not data[lottery_type]:
                    log.warning(f'获取{lottery_type}数据失败或为空')
                    continue
                
                lottery_data = data[lottery_type]
                
                # 调试日志：打印API返回的数据结构（前100个字符）
                log.debug(f'{lottery_type} API返回数据类型: {type(lottery_data)}, 内容预览: {str(lottery_data)[:200]}')
                
                # 保存数据
                if self._save_lottery_data(lottery_type, lottery_data):
                    saved_count += 1
                    log.info(f'{self.lottery_mapping[lottery_type]["lottery_name"]}数据保存成功')
                else:
                    log.debug(f'{self.lottery_mapping[lottery_type]["lottery_name"]}数据已存在或无效，跳过')
                    
        except Exception as e:
            log.error(f'获取彩票数据异常：{e}')
            import traceback
            log.error(traceback.format_exc())
        
        return saved_count
    
    def update_latest_lottery_data(self) -> int:
        """
        更新最新的彩票数据（只获取昨天的数据）
        
        Returns:
            int: 成功保存的记录数
        """
        log.info('开始更新最新彩票数据...')
        
        lottery_types_to_fetch = []
        
        # 检查哪些彩种需要获取
        for lottery_type, info in self.lottery_mapping.items():
            latest_draw = localdb.query(DigitalLotteryDraw).filter(
                DigitalLotteryDraw.lottery_code == info['code']
            ).order_by(DigitalLotteryDraw.draw_time.desc()).first()
            
            if not latest_draw:
                lottery_types_to_fetch.append(lottery_type)
                log.info(f"{info['lottery_name']} 数据库中无记录，需要获取")
                continue
            
            from datetime import timedelta
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # 只有当最新一期早于昨天时，才尝试获取
            if latest_draw.draw_time and latest_draw.draw_time.date() < yesterday:
                lottery_types_to_fetch.append(lottery_type)
                log.info(f"{info['lottery_name']} 最新一期为{latest_draw.draw_num}期（{latest_draw.draw_time.date()}），早于昨天（{yesterday}），尝试获取")
            elif latest_draw.draw_time and latest_draw.draw_time.date() == yesterday:
                log.info(f"{info['lottery_name']} 最新一期为{latest_draw.draw_num}期（{latest_draw.draw_time.date()}），已是昨天数据，无需获取")
            else:
                log.info(f"{info['lottery_name']} 最新一期为{latest_draw.draw_num}期（{latest_draw.draw_time.date()}），已是今天数据，无需获取")
        
        if not lottery_types_to_fetch:
            log.info('所有彩种今日数据已存在，无需获取')
            return 0
        
        # 获取并保存数据
        log.info(f'开始获取 {len(lottery_types_to_fetch)} 个彩种数据')
        saved_count = self.fetch_and_save_lottery_data(lottery_types_to_fetch)
        log.info(f'彩票数据更新完成，成功保存 {saved_count} 条记录')
        return saved_count
