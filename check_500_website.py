# -*- coding: utf-8 -*-
"""
检查 500.com 网站上这场比赛的实际比分
"""
import requests
from bs4 import BeautifulSoup


def check_500_website():
    """检查 500.com 网站上的比赛信息"""
    
    url = "https://live.500.com/zqdc.php"
    
    print("=" * 80)
    print(f"检查 500.com 网站: {url}")
    print("=" * 80)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'  # 500.com 使用 GBK 编码
        
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含"曼谷联"或"大阪钢巴"的内容
        text = soup.get_text()
        
        # 简单搜索
        if '曼谷联' in text and '大阪钢巴' in text:
            print("\n✅ 在页面上找到了这场比赛")
            
            # 尝试找到表格行
            rows = soup.find_all('tr')
            for row in rows:
                row_text = row.get_text()
                if '曼谷联' in row_text or '大阪钢巴' in row_text:
                    print("\n找到的相关行:")
                    print(row_text[:500])  # 打印前500字符
                    break
        else:
            print("\n❌ 未在页面上找到这场比赛")
            
        # 显示页面标题和一些基本信息
        title = soup.title.string if soup.title else '无标题'
        print(f"\n页面标题: {title}")
        
    except Exception as e:
        print(f"\n❌ 访问失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    check_500_website()
