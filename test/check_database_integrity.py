# -*- coding: utf-8 -*-
"""
数据库记录完整性检查脚本
检查各个爬虫已存入数据库的数据完整性
"""
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.database import localdb, DigitalLotteryDraw, DigitalLotteryPrize, FootballMatch, MatchResult, SpfOdds, ScoreOdds, TotalGoalOdds, TcbkMatch, TcbkResult, TcbkSpf, TcbkDxf, TcbkRfsf
from app.common.logger import log


class DatabaseChecker:
    """数据库完整性检查器"""
    
    def __init__(self):
        self.results = {
            'total_checks': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
    
    def check_digitallottery_database(self):
        """检查数字彩数据库"""
        print("\n" + "="*60)
        print("🎰 数字彩数据库检查")
        print("="*60)
        
        # 1. 检查总记录数
        total_draws = localdb.query(DigitalLotteryDraw).count()
        print(f"\n📊 总开奖记录数：{total_draws}")
        
        if total_draws == 0:
            print("⚠️  警告：数据库中没有开奖记录")
            self.results['warnings'] += 1
            return
        
        # 2. 按彩种统计
        print("\n📋 各彩种记录统计:")
        lottery_types = localdb.query(DigitalLotteryDraw.lottery_code, 
                                     DigitalLotteryDraw.lottery_name).distinct().all()
        
        for lt in lottery_types:
            count = localdb.query(DigitalLotteryDraw).filter_by(lottery_code=lt.lottery_code).count()
            print(f"   - {lt.lottery_name} ({lt.lottery_code}): {count}期")
        
        # 3. 检查数据完整性
        print("\n🔍 数据完整性检查:")
        recent_draws = localdb.query(DigitalLotteryDraw).order_by(
            DigitalLotteryDraw.draw_time.desc()
        ).limit(20).all()
        
        issues = []
        for draw in recent_draws:
            # 检查开奖号码
            if not draw.draw_result or draw.draw_result == 'N/A':
                issues.append(f"{draw.lottery_name}第{draw.draw_num}期：开奖结果缺失")
            
            # 检查奖级信息
            prize_count = len(draw.prize_levels) if hasattr(draw, 'prize_levels') and draw.prize_levels else 0
            if prize_count == 0:
                issues.append(f"{draw.lottery_name}第{draw.draw_num}期：缺少奖级信息")
            
            # 检查时间字段
            if not draw.draw_time:
                issues.append(f"{draw.lottery_name}第{draw.draw_num}期：开奖时间缺失")
        
        if issues:
            print(f"\n❌ 发现{len(issues)}个问题:")
            for issue in issues[:5]:  # 只显示前 5 个
                print(f"   - {issue}")
            self.results['failed'] += len(issues)
        else:
            print("✅ 最近 20 期数据完整，无问题")
            self.results['passed'] += 1
        
        self.results['total_checks'] += 1
        
        # 4. 检查期号连续性
        print("\n📈 期号连续性检查:")
        for lottery_code, lottery_name in localdb.query(DigitalLotteryDraw.lottery_code, 
                                                        DigitalLotteryDraw.lottery_name).distinct().all():
            draws = localdb.query(DigitalLotteryDraw).filter_by(lottery_code=lottery_code)\
                    .order_by(DigitalLotteryDraw.draw_num.desc()).limit(10).all()
            
            if len(draws) < 2:
                continue
            
            print(f"\n   {lottery_name}:")
            prev_num = None
            gaps = []
            
            for draw in draws:
                try:
                    current_num = int(draw.draw_num)
                    if prev_num and current_num != prev_num - 1:
                        gap = prev_num - current_num - 1
                        if gap > 0:
                            gaps.append(f"缺少第{current_num+1}期到第{prev_num-1}期")
                    prev_num = current_num
                except (ValueError, TypeError):
                    pass
            
            if gaps:
                print(f"      ⚠️  发现期号不连续:")
                for gap in gaps[:3]:
                    print(f"         - {gap}")
                self.results['warnings'] += len(gaps)
            else:
                print(f"      ✅ 期号连续")
        
        # 5. 检查奖级数据质量
        print("\n💰 奖级数据质量检查:")
        sample_prizes = localdb.query(DigitalLotteryPrize).limit(10).all()
        
        if sample_prizes:
            prize_issues = []
            for prize in sample_prizes:
                if not prize.prize_level:
                    prize_issues.append(f"奖级名称缺失 (ID:{prize.id})")
                if not prize.stake_count:
                    prize_issues.append(f"中奖注数缺失 (ID:{prize.id})")
                if not prize.stake_amount:
                    prize_issues.append(f"单注奖金缺失 (ID:{prize.id})")
            
            if prize_issues:
                print(f"\n❌ 发现{len(prize_issues)}个奖级数据问题:")
                for issue in prize_issues[:5]:
                    print(f"   - {issue}")
                self.results['failed'] += len(prize_issues)
            else:
                print("✅ 奖级数据格式正确")
                self.results['passed'] += 1
        else:
            print("⚠️  数据库中没有奖级记录")
            self.results['warnings'] += 1
    
    def check_football_database(self):
        """检查足球数据库"""
        print("\n" + "="*60)
        print("⚽ 足球数据库检查")
        print("="*60)
        
        # 1. 检查比赛总数
        total_matches = localdb.query(FootballMatch).count()
        print(f"\n📊 总比赛记录数：{total_matches}")
        
        if total_matches == 0:
            print("⚠️  警告：数据库中没有足球比赛记录")
            self.results['warnings'] += 1
            return
        
        # 2. 按类型统计
        print("\n📋 各类型比赛统计:")
        from app.database import MatchTypeEnum
        for match_type in [MatchTypeEnum.TCZQ, MatchTypeEnum.BJDC]:
            count = localdb.query(FootballMatch).filter_by(match_type=match_type).count()
            type_name = "传统足球" if match_type == MatchTypeEnum.TCZQ else "北京单场"
            print(f"   - {type_name}: {count}场")
        
        # 3. 检查比赛数据完整性
        print("\n🔍 比赛数据完整性检查:")
        recent_matches = localdb.query(FootballMatch).order_by(
            FootballMatch.match_time.desc()
        ).limit(20).all()
        
        issues = []
        for match in recent_matches:
            if not match.match_id:
                issues.append(f"比赛 ID 缺失：{match.match_week} {match.match_num_str}")
            if not match.home_team_id or not match.away_team_id:
                issues.append(f"球队 ID 缺失：{match.match_week} {match.match_num_str}")
            if not match.match_time:
                issues.append(f"比赛时间缺失：{match.match_week} {match.match_num_str}")
        
        if issues:
            print(f"\n❌ 发现{len(issues)}个问题:")
            for issue in issues[:5]:
                print(f"   - {issue}")
            self.results['failed'] += len(issues)
        else:
            print("✅ 最近 20 场比赛数据完整")
            self.results['passed'] += 1
        
        self.results['total_checks'] += 1
        
        # 4. 检查赔率数据
        print("\n💰 赔率数据检查:")
        spf_count = localdb.query(SpfOdds).count()
        score_count = localdb.query(ScoreOdds).count()
        goal_count = localdb.query(TotalGoalOdds).count()
        
        print(f"   - 胜平负赔率：{spf_count}条")
        print(f"   - 比分赔率：{score_count}条")
        print(f"   - 总进球赔率：{goal_count}条")
        
        # 5. 检查结果记录
        print("\n📝 比赛结果记录检查:")
        result_count = localdb.query(MatchResult).count()
        print(f"   赛果记录数：{result_count}")
        
        if result_count > 0:
            # 检查赛果数据完整性
            recent_results = localdb.query(MatchResult).order_by(
                MatchResult.match_end_time.desc()
            ).limit(10).all()
            
            result_issues = []
            for result in recent_results:
                if result.home_team_goals is None or result.away_team_goals is None:
                    result_issues.append(f"比分缺失 (比赛 ID:{result.match_id})")
            
            if result_issues:
                print(f"\n❌ 发现{len(result_issues)}个赛果问题")
                self.results['failed'] += len(result_issues)
            else:
                print("✅ 赛果数据完整")
                self.results['passed'] += 1
        else:
            print("⚠️  没有赛果记录")
            self.results['warnings'] += 1
    
    def check_basketball_database(self):
        """检查篮球数据库"""
        print("\n" + "="*60)
        print("🏀 篮球数据库检查")
        print("="*60)
        
        # 1. 检查比赛总数
        total_matches = localdb.query(TcbkMatch).count()
        print(f"\n📊 总比赛记录数：{total_matches}")
        
        if total_matches == 0:
            print("⚠️  警告：数据库中没有篮球比赛记录")
            self.results['warnings'] += 1
            return
        
        # 2. 检查数据完整性
        print("\n🔍 比赛数据完整性检查:")
        recent_matches = localdb.query(TcbkMatch).order_by(
            TcbkMatch.match_time.desc()
        ).limit(20).all()
        
        issues = []
        for match in recent_matches:
            if not match.match_id:
                issues.append(f"比赛 ID 缺失：{match.match_week} {match.match_num_str}")
            if not match.home_team_id or not match.away_team_id:
                issues.append(f"球队 ID 缺失：{match.match_week} {match.match_num_str}")
        
        if issues:
            print(f"\n❌ 发现{len(issues)}个问题:")
            for issue in issues[:5]:
                print(f"   - {issue}")
            self.results['failed'] += len(issues)
        else:
            print("✅ 最近 20 场比赛数据完整")
            self.results['passed'] += 1
        
        self.results['total_checks'] += 1
        
        # 3. 检查赔率数据
        print("\n💰 赔率数据检查:")
        spf_count = localdb.query(TcbkSpf).count()
        dxf_count = localdb.query(TcbkDxf).count()
        rfsf_count = localdb.query(TcbkRfsf).count()
        
        print(f"   - 胜负赔率：{spf_count}条")
        print(f"   - 大小分赔率：{dxf_count}条")
        print(f"   - 让分胜负赔率：{rfsf_count}条")
        
        # 4. 检查赛果记录
        print("\n📝 赛果记录检查:")
        result_count = localdb.query(TcbkResult).count()
        print(f"   赛果记录数：{result_count}")
        
        if result_count > 0:
            print("✅ 有赛果记录")
            self.results['passed'] += 1
        else:
            print("⚠️  没有赛果记录")
            self.results['warnings'] += 1
    
    def print_summary(self):
        """打印摘要"""
        print("\n" + "="*60)
        print("📊 数据库检查摘要")
        print("="*60)
        print(f"总检查项：{self.results['total_checks']}")
        print(f"✅ 通过：{self.results['passed']}")
        print(f"❌ 失败：{self.results['failed']}")
        print(f"⚠️  警告：{self.results['warnings']}")
        
        if self.results['total_checks'] > 0:
            pass_rate = self.results['passed'] / self.results['total_checks'] * 100
            print(f"通过率：{pass_rate:.2f}%")
        
        print("="*60)


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔍 开始数据库完整性检查")
    print("="*60)
    print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checker = DatabaseChecker()
    
    # 检查各个数据库
    checker.check_digitallottery_database()
    checker.check_football_database()
    checker.check_basketball_database()
    
    # 打印摘要
    checker.print_summary()
    
    print("\n✅ 数据库检查完成!")


if __name__ == "__main__":
    main()
