import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controls.req_sporttery_api import SportteryAPI

def test_basketball_matchid():
    """测试篮球比赛记录中的matchId值"""
    try:
        # 初始化API客户端
        api = SportteryAPI()
        
        # 获取篮球比赛计算器信息
        print("获取篮球比赛计算器信息...")
        calculator_data = api.get_basketball_match_calculator(['hilo', 'spf', 'rfsf', 'sfc'])
        
        if 'matchInfoList' in calculator_data:
            match_info_list = calculator_data['matchInfoList']
            print(f"\nmatchInfoList的长度:", len(match_info_list))
            
            # 检查所有比赛记录的matchId
            print("\n所有比赛记录的matchId情况:")
            for i, match_info in enumerate(match_info_list):
                match_id = match_info.get('matchId')
                match_id_type = type(match_id)
                match_id_falsy = not match_id
                
                print(f"  记录{i+1}: matchId={match_id}, type={match_id_type}, falsy={match_id_falsy}")
                
                # 如果matchId是falsy值，打印更多信息
                if match_id_falsy:
                    print(f"    比赛信息键: {list(match_info.keys())}")
                    if 'matchNum' in match_info:
                        print(f"    matchNum: {match_info['matchNum']}")
                    if 'matchNumStr' in match_info:
                        print(f"    matchNumStr: {match_info['matchNumStr']}")
                        
        # 测试比赛列表接口
        print("\n\n测试比赛列表接口:")
        match_list = api.get_basketball_match_list()
        print(f"比赛列表的长度:", len(match_list))
        
        if not match_list.empty:
            print("\n比赛列表的列:", list(match_list.columns))
            print("\n比赛列表的matchId:")
            for i, row in match_list.iterrows():
                match_id = row.get('matchId')
                print(f"  记录{i+1}: matchId={match_id}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'api' in locals():
            api.close()

if __name__ == "__main__":
    test_basketball_matchid()