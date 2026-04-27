# -*- coding: utf-8 -*-
"""
API 功能测试脚本
测试所有主要接口是否正常工作
"""
import requests
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"

# 测试结果统计
test_results = {
    "passed": 0,
    "failed": 0,
    "total": 0
}


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(name, success, detail=""):
    """打印测试结果"""
    test_results["total"] += 1
    if success:
        test_results["passed"] += 1
        status = "✅ PASS"
    else:
        test_results["failed"] += 1
        status = "❌ FAIL"
    
    print(f"{status} - {name}")
    if detail:
        print(f"       {detail}")


def test_health_check():
    """测试健康检查接口"""
    print_section("1. 健康检查测试")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        success = response.status_code == 200 and data.get("status") == "healthy"
        print_test("健康检查接口", success, f"状态: {data.get('status')}")
        
    except Exception as e:
        print_test("健康检查接口", False, str(e))


def test_login():
    """测试登录接口"""
    print_section("2. 认证测试 - 登录")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            token_type = data.get("token_type")
            
            success = token is not None and token_type == "bearer"
            print_test("管理员登录", success, f"Token 类型: {token_type}")
            
            return token
        else:
            print_test("管理员登录", False, f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_test("管理员登录", False, str(e))
        return None


def test_register():
    """测试注册接口"""
    print_section("3. 认证测试 - 注册")
    
    try:
        # 尝试注册新用户
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": "test_user",
                "password": "test123"
            }
        )
        
        if response.status_code == 200:
            print_test("用户注册", True, "成功创建测试用户")
        elif response.status_code == 400:
            # 用户已存在也算正常
            print_test("用户注册", True, "用户已存在（预期行为）")
        else:
            print_test("用户注册", False, f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_test("用户注册", False, str(e))


def test_tczq_matches(token):
    """测试体彩足球比赛列表"""
    print_section("4. 体彩足球测试 - 比赛列表")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/tczq/matches",
            headers=headers,
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("data", [])
            
            success = len(matches) > 0
            print_test("查询比赛列表", success, f"返回 {len(matches)} 条记录")
            
            if matches:
                match = matches[0]
                print(f"       示例: {match.get('match_num_str')} - {match.get('match_time')}")
        else:
            print_test("查询比赛列表", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("查询比赛列表", False, str(e))


def test_tczq_match_detail(token):
    """测试体彩足球比赛详情"""
    print_section("5. 体彩足球测试 - 比赛详情")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先获取一个比赛ID
        response = requests.get(
            f"{BASE_URL}/api/tczq/matches",
            headers=headers,
            params={"limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("data", [])
            
            if matches:
                match_id = matches[0]["match_id"]
                
                # 查询详情
                response = requests.get(
                    f"{BASE_URL}/api/tczq/match/{match_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    detail = response.json()
                    success = detail.get("code") == 200
                    print_test("查询比赛详情", success, f"比赛ID: {match_id}")
                else:
                    print_test("查询比赛详情", False, f"HTTP {response.status_code}")
            else:
                print_test("查询比赛详情", False, "没有可用的比赛ID")
        else:
            print_test("查询比赛详情", False, "无法获取比赛列表")
            
    except Exception as e:
        print_test("查询比赛详情", False, str(e))


def test_bjdc_matches(token):
    """测试北京单场比赛列表"""
    print_section("6. 北京单场测试 - 比赛列表")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/bjdc/matches",
            headers=headers,
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("data", [])
            
            success = len(matches) >= 0  # 允许为空
            print_test("查询比赛列表", success, f"返回 {len(matches)} 条记录")
        else:
            print_test("查询比赛列表", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("查询比赛列表", False, str(e))


def test_base_leagues(token):
    """测试联赛列表"""
    print_section("7. 基础数据测试 - 联赛列表")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/base/leagues",
            headers=headers,
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            leagues = data.get("data", [])
            
            success = len(leagues) > 0
            print_test("查询联赛列表", success, f"返回 {len(leagues)} 条记录")
            
            if leagues:
                league = leagues[0]
                print(f"       示例: {league.get('league_name')} ({league.get('league_name_abbr')})")
        else:
            print_test("查询联赛列表", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("查询联赛列表", False, str(e))


def test_base_teams(token):
    """测试球队列表"""
    print_section("8. 基础数据测试 - 球队列表")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/base/teams",
            headers=headers,
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get("data", [])
            
            success = len(teams) > 0
            print_test("查询球队列表", success, f"返回 {len(teams)} 条记录")
            
            if teams:
                team = teams[0]
                print(f"       示例: {team.get('team_full_name')} ({team.get('team_short_name')})")
        else:
            print_test("查询球队列表", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("查询球队列表", False, str(e))


def test_unauthorized_access():
    """测试未授权访问"""
    print_section("9. 安全测试 - 未授权访问")
    
    try:
        # 不带 Token 访问受保护接口
        response = requests.get(f"{BASE_URL}/api/tczq/matches")
        
        # 应该返回 401
        success = response.status_code == 401
        print_test("未授权访问拦截", success, f"HTTP {response.status_code} (预期 401)")
        
    except Exception as e:
        print_test("未授权访问拦截", False, str(e))


def test_invalid_token():
    """测试无效 Token"""
    print_section("10. 安全测试 - 无效 Token")
    
    try:
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = requests.get(
            f"{BASE_URL}/api/tczq/matches",
            headers=headers
        )
        
        # 应该返回 401
        success = response.status_code == 401
        print_test("无效 Token 拦截", success, f"HTTP {response.status_code} (预期 401)")
        
    except Exception as e:
        print_test("无效 Token 拦截", False, str(e))


def test_user_profile(token):
    """测试用户资料接口"""
    print_section("11. 用户中心测试 - 个人资料")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            profile = data.get("data", {})
            success = profile.get("username") is not None
            print_test("获取用户资料", success, f"用户名: {profile.get('username')}, 等级: {profile.get('level')}")
        else:
            print_test("获取用户资料", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("获取用户资料", False, str(e))


def test_user_balance(token):
    """测试用户余额接口"""
    print_section("12. 用户中心测试 - 余额查询")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/user/balance", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            balance_data = data.get("data", {})
            success = balance_data.get("balance") is not None
            print_test("查询余额", success, f"余额: {balance_data.get('balance')}")
        else:
            print_test("查询余额", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("查询余额", False, str(e))


def test_user_level(token):
    """测试用户等级接口"""
    print_section("13. 用户中心测试 - 等级信息")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/user/level/info", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            level_info = data.get("data", {})
            success = level_info.get("current_level") is not None
            print_test("查询等级信息", success, f"等级: {level_info.get('level_name')}, 经验: {level_info.get('experience')}")
        else:
            print_test("查询等级信息", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("查询等级信息", False, str(e))


def test_bet_records(token):
    """测试投注记录接口"""
    print_section("14. 投注测试 - 投注记录")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/bet/records",
            headers=headers,
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            records = data.get("data", [])
            success = True  # 允许为空
            print_test("查询投注记录", success, f"返回 {len(records)} 条记录")
        else:
            print_test("查询投注记录", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("查询投注记录", False, str(e))


def test_favorites(token):
    """测试收藏接口"""
    print_section("15. 收藏测试 - 收藏列表")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/favorite/list",
            headers=headers,
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            favorites = data.get("data", [])
            success = True  # 允许为空
            print_test("查询收藏列表", success, f"返回 {len(favorites)} 条记录")
        else:
            print_test("查询收藏列表", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_test("查询收藏列表", False, str(e))
def print_summary():
    """打印测试总结"""
    print_section("测试总结")
    
    total = test_results["total"]
    passed = test_results["passed"]
    failed = test_results["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n总测试数: {total}")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")
    print(f"通过率: {pass_rate:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查上述错误信息")
    
    print("\n" + "=" * 70)


def main():
    """主测试流程"""
    print("\n" + "=" * 70)
    print("  Soccer Data API - 功能测试")
    print("=" * 70)
    print(f"\n测试目标: {BASE_URL}")
    print(f"开始时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 健康检查
    test_health_check()
    
    # 2. 登录获取 Token
    token = test_login()
    
    if not token:
        print("\n❌ 登录失败，无法继续测试需要认证的接口")
        print_summary()
        return False
    
    # 3. 注册测试
    test_register()
    
    # 4-8. 数据查询测试
    test_tczq_matches(token)
    test_tczq_match_detail(token)
    test_bjdc_matches(token)
    test_base_leagues(token)
    test_base_teams(token)
    
    # 9-10. 安全测试
    test_unauthorized_access()
    test_invalid_token()
    
    # 11-15. 新功能测试
    test_user_profile(token)
    test_user_balance(token)
    test_user_level(token)
    test_bet_records(token)
    test_favorites(token)
    
    # 打印总结
    print_summary()
    
    # 返回测试结果
    return test_results["failed"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
