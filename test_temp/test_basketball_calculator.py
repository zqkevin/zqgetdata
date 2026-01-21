import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controls.req_sporttery_api import SportteryAPI

def test_basketball_calculator():
    """测试篮球比赛计算器接口返回的数据结构"""
    try:
        # 初始化API客户端
        api = SportteryAPI()
        
        # 获取篮球比赛计算器信息
        print("获取篮球比赛计算器信息...")
        calculator_data = api.get_basketball_match_calculator(['hilo', 'spf', 'rfsf', 'sfc'])
        
        print("\n返回数据的类型:", type(calculator_data))
        print("\n返回数据的键:", list(calculator_data.keys()))
        
        if 'matchInfoList' in calculator_data:
            match_info_list = calculator_data['matchInfoList']
            print(f"\nmatchInfoList的长度:", len(match_info_list))
            
            if match_info_list:
                # 检查所有比赛记录的matchId情况
                print("\n所有比赛记录的matchId情况:")
                for i, match_info in enumerate(match_info_list):
                    has_match_id = 'matchId' in match_info
                    match_id_value = match_info.get('matchId') if has_match_id else 'N/A'
                    print(f"  记录{i+1}: matchId存在={has_match_id}, 值={match_id_value}")
                    
                # 打印第一条比赛信息
                print("\n\n第一条比赛信息(完整):")
                print(match_info_list[0])
                
                # 检查oddsList和poolList
                if 'oddsList' in match_info_list[0]:
                    print(f"\n\noddsList的长度:", len(match_info_list[0]['oddsList']))
                    if match_info_list[0]['oddsList']:
                        print("\n第一条赔率信息:")
                        print(match_info_list[0]['oddsList'][0])
                            
                if 'poolList' in match_info_list[0]:
                    print(f"\n\npoolList的长度:", len(match_info_list[0]['poolList']))
                    if match_info_list[0]['poolList']:
                        print("\n第一条玩法信息:")
                        print(match_info_list[0]['poolList'][0])
                            
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'api' in locals():
            api.close()

if __name__ == "__main__":
    test_basketball_calculator()