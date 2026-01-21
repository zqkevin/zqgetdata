# -*- coding: utf-8 -*-
import os
import sys
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback
from datetime import datetime
import json
from app.common.req_sporttery_api import SportteryAPI
from app.database import localdb
from app.database.digital_lottery_models import DigitalLotteryDraw, DigitalLotteryPrize
from app.common.logger import log


class LotterySpider:
    """
    彩票数据爬虫类
    用于获取三种彩票（大乐透、排列3、七星彩）的开奖信息并记录到数据库
    """
    
    def __init__(self):
        self.api_client = SportteryAPI()
        self.now_time = datetime.now()
        # 彩种映射表，包含彩票代码
        self.lottery_mapping = {
            'dlt': {
                'model': DigitalLotteryDraw,
                'lottery_name': '超级大乐透',
                'code': '85'
            },
            'pl3': {
                'model': DigitalLotteryDraw,
                'lottery_name': '排列3',
                'code': '35'
            },
            'pl5': {
                'model': DigitalLotteryDraw,
                'lottery_name': '排列5',
                'code': '350133'
            },
            'qxc': {
                'model': DigitalLotteryDraw,
                'lottery_name': '七星彩',
                'code': '04'
            }
        }
    
    def _check_existing_data(self, lottery_type, draw_num):
        """
        检查数据库中是否已存在该期数据
        
        Args:
            lottery_type: 彩种类型
            draw_num: 期号
            
        Returns:
            bool: 是否已存在
        """
        try:
            model_class = self.lottery_mapping[lottery_type]['model']
            existing = localdb.query(model_class).filter(
                model_class.draw_num == draw_num,
                model_class.lottery_code == self.lottery_mapping[lottery_type]['code']
            ).first()
            return existing is not None
        except Exception as e:
            log.error(f"检查{lottery_type}数据库记录时出错: {str(e)}")
            return False
    
    def _convert_datetime(self, datetime_str):
        """
        将字符串转换为datetime对象
        
        Args:
            datetime_str: 日期时间字符串
            
        Returns:
            datetime对象或None
        """
        if not datetime_str:
            return None
        
        try:
            # 尝试不同的日期格式
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
            
            log.warning(f"无法解析日期格式: {datetime_str}")
            return None
        except Exception as e:
            log.error(f"日期转换错误: {str(e)}")
            return None
    
    def _save_prize_levels(self, draw_id, prize_levels):
        """
        保存奖级信息
        
        Args:
            draw_id: 开奖记录ID
            prize_levels: 奖级列表
        """
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
            log.error(f"保存奖级信息时出错: {str(e)}")
            raise
    
    def _save_lottery_data(self, lottery_type, data):
        """
        保存彩种数据到数据库
        
        Args:
            lottery_type: 彩种类型
            data: 彩种数据
        """
        try:
            # 获取对应的模型类和彩票名称
            model_info = self.lottery_mapping.get(lottery_type)
            if not model_info:
                log.error(f"未知的彩种类型: {lottery_type}")
                return False
            
            model_class = model_info['model']
            lottery_name = model_info['lottery_name']
            
            # 创建模型实例
            draw = model_class(
                lottery_code=model_info['code'],
                lottery_name=lottery_name,
                draw_num=data.get('lotteryDrawNum'),
                draw_time=self._convert_datetime(data.get('lotteryDrawTime')),
                draw_result=data.get('lotteryDrawResult'),
                unsorted_draw_result=data.get('lotteryUnsortDrawresult'),
                pool_balance_after_draw=data.get('poolBalanceAfterdraw'),
                sale_begin_time=self._convert_datetime(data.get('lotterySaleBeginTime')),
                sale_end_time=self._convert_datetime(data.get('lotterySaleEndtime')),
                draw_pdf_url=data.get('drawPdfUrl'),
                is_verified=data.get('verify'),
                rule_type=data.get('ruleType'),
                equipment_count=data.get('lotteryEquipmentCount'),
                notice_flag=data.get('lotteryNotice'),
                notice_show_flag=data.get('lotteryNoticeShowFlag'),
                created_at=self.now_time,
                updated_at=self.now_time
            )
            
            # 保存开奖信息
            localdb.add(draw, close=False)
            log.info(f"成功保存{lottery_type} {data.get('lottery_draw_num')}期数据")
            
            # 保存奖级信息
            prize_levels = data.get('prizeLevelList', [])
            if prize_levels:
                self._save_prize_levels(draw.id, prize_levels)
            
            return True
        except Exception as e:
            log.error(f"保存{lottery_type}数据时出错: {str(e)}")
            return False
    
    def _initialize_database(self):
        """
        初始化数据库，确保连接正常
        """
        try:
            # 检查数据库连接
            if not localdb:
                log.error("数据库连接失败")
                return False
            
            log.info("数据库连接验证成功")
            return True
        except Exception as e:
            log.error(f"数据库初始化错误: {str(e)}")
            return False
    
    def fetch_lottery_data_with_retry(self, lottery_types, max_retries=3):
        """
        带重试机制的彩票数据获取
        
        Args:
            lottery_types: 彩种类型列表
            max_retries: 最大重试次数
            
        Returns:
            dict: 彩种数据字典
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                log.info(f"尝试获取彩种数据（第{retry_count + 1}次）...")
                lottery_data = self.api_client.get_multi_lottery_data(lottery_types)
                
                # 检查是否所有彩种都获取失败
                all_failed = all('error' in data for data in lottery_data.values())
                if not all_failed:
                    return lottery_data
                
                retry_count += 1
                if retry_count < max_retries:
                    log.warning(f"所有彩种数据获取失败，将在1秒后重试...")
                    import time
                    time.sleep(1)
            except Exception as e:
                retry_count += 1
                log.error(f"获取彩种数据异常: {str(e)}")
                if retry_count < max_retries:
                    log.warning(f"将在1秒后重试...")
                    import time
                    time.sleep(1)
        
        log.error(f"达到最大重试次数({max_retries})，放弃获取")
        return {}
    
    def fetch_and_save_lottery_data(self):
        """
        获取并保存彩票数据
        1. 初始化数据库
        2. 带重试机制获取三种彩种数据
        3. 检查数据库中是否已存在
        4. 保存新数据到数据库
        """
        try:
            log.info("开始获取彩票数据...")
            
            # 初始化数据库
            if not self._initialize_database():
                log.error("数据库初始化失败，无法继续")
                return 0
            
            # 批量获取四种彩种数据（带重试机制）
            lottery_types = ['dlt', 'pl3', 'pl5', 'qxc']
            lottery_data = self.fetch_lottery_data_with_retry(lottery_types)
            
            if not lottery_data:
                log.error("未能获取到任何彩票数据")
                return 0
            
            saved_count = 0
            for lottery_type, data in lottery_data.items():
                if 'error' in data:
                    log.error(f"获取{lottery_type}数据失败: {data['error']}")
                    continue
                
                # 处理API返回的数据结构（每个彩种可能包含多个彩种的数据）
                actual_data = data.get(lottery_type, {})
                if not actual_data:
                    log.warning(f"{lottery_type}数据中未找到实际数据")
                    continue
                
                # 获取期号
                draw_num = actual_data.get('lotteryDrawNum')
                if not draw_num:
                    log.warning(f"{lottery_type}数据中未找到期号")
                    continue
                
                # 检查是否已存在
                if self._check_existing_data(lottery_type, draw_num):
                    log.info(f"{lottery_type} {draw_num}期数据已存在，跳过保存")
                    continue
                
                # 保存数据
                if self._save_lottery_data(lottery_type, actual_data):
                    saved_count += 1
            
            log.info(f"彩票数据获取与保存完成，共保存{saved_count}条新记录")
            return saved_count
            
        except Exception as e:
            log.error(f"获取和保存彩票数据时出错: {str(e)}")
            log.error(traceback.format_exc())
            return 0
        finally:
            # 关闭API客户端
            self.api_client.close()
    
    def update_latest_lottery_data(self):
        """
        更新最新的彩票数据
        用于定期执行的数据更新
        """
        log.info("开始更新最新彩票数据...")
        start_time = datetime.now()
        
        try:
            saved_count = self.fetch_and_save_lottery_data()
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            log.info(f"彩票数据更新完成，耗时{elapsed_time:.2f}秒，保存{saved_count}条新记录")
            
            return saved_count
        except Exception as e:
            log.error(f"更新彩票数据时发生异常: {str(e)}")
            log.error(traceback.format_exc())
            return 0


if __name__ == "__main__":
    try:
        # 初始化爬虫
        spider = LotterySpider()
        
        # 更新最新彩票数据
        saved_count = spider.update_latest_lottery_data()
        
        print(f"彩票数据更新完成，保存了{saved_count}条新记录")
        
    except Exception as e:
        print(f"执行出错: {str(e)}")
        traceback.print_exc()