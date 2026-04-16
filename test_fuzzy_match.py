# -*- coding: utf-8 -*-
"""
测试模糊匹配功能
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.crawler.bjdc_result import BjdcResultCollector

collector = BjdcResultCollector()

print("=" * 80)
print("测试队名标准化")
print("=" * 80)

test_cases = [
    "曼彻斯特联",
    "曼联",
    "拜仁慕尼黑",
    "拜仁",
    "皇家马德里",
    "皇马",
    "巴黎圣日耳曼",
    "巴黎",
]

for name in test_cases:
    normalized = collector._normalize_team_name(name)
    print(f"  {name:15s} -> {normalized}")

print("\n" + "=" * 80)
print("测试队名相似度")
print("=" * 80)

similarity_tests = [
    ("曼彻斯特联", "曼联"),
    ("拜仁慕尼黑", "拜仁"),
    ("皇家马德里", "皇马"),
    ("巴黎圣日耳曼", "巴黎"),
    ("吉波", "通德拉"),  # 应该不匹配
    ("MP米凯利", "吉维森特"),  # 应该不匹配
]

for name1, name2 in similarity_tests:
    similar = collector._is_team_name_similar(name1, name2)
    status = "✅ 相似" if similar else "❌ 不相似"
    print(f"  {name1:15s} vs {name2:15s} -> {status}")

print("\n" + "=" * 80)
print("结论")
print("=" * 80)
print("模糊匹配可以处理:")
print("  ✅ 全称和简称 (曼彻斯特联 vs 曼联)")
print("  ✅ 包含关系 (拜仁慕尼黑 vs 拜仁)")
print("  ❌ 完全不同的队名 (吉波 vs 通德拉)")
print("\n注意: BJDC 和 TCZQ 的队名如果完全不同，仍无法匹配")
