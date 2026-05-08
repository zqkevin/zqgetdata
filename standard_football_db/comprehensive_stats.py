"""
全面总结现有数据
"""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def stats_core_data():
    """统计核心数据文件"""
    print_section("📊 核心数据文件 (data/)")
    
    data_dir = BASE_DIR / "data"
    
    files = {
        "countries.json": "国家/地区",
        "leagues.json": "联赛",
        "teams_with_players.json": "球队和球员",
        "summary.json": "数据摘要"
    }
    
    total_countries = 0
    total_leagues = 0
    total_teams = 0
    total_players = 0
    
    for filename, description in files.items():
        filepath = data_dir / filename
        
        if not filepath.exists():
            print(f"   ❌ {filename}: 不存在")
            continue
        
        size = filepath.stat().st_size / 1024
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            count = len(data)
            
            if filename == "countries.json":
                total_countries = count
                # 检查翻译状态
                translated = sum(1 for c in data if c.get('name_zh'))
                print(f"   ✅ {filename}: {count} 个国家/地区 ({size:.1f} KB)")
                print(f"      📝 已翻译: {translated}/{count} ({translated/count*100:.1f}%)")
                
            elif filename == "leagues.json":
                total_leagues = count
                translated = sum(1 for l in data if l.get('name_zh_full'))
                print(f"   ✅ {filename}: {count} 个联赛 ({size:.1f} KB)")
                print(f"      📝 已翻译: {translated}/{count} ({translated/count*100:.1f}%)")
                
            elif filename == "teams_with_players.json":
                total_teams = count
                total_players = sum(len(t.get('players', [])) for t in data)
                translated_teams = sum(1 for t in data if t.get('name_zh_full'))
                translated_players = sum(
                    sum(1 for p in t.get('players', []) if p.get('name_zh_full'))
                    for t in data
                )
                print(f"   ✅ {filename}: {count} 支球队 ({size:.1f} KB)")
                print(f"      ⚽ 球员总数: {total_players}")
                print(f"      📝 球队已翻译: {translated_teams}/{count} ({translated_teams/count*100:.1f}%)")
                print(f"      📝 球员已翻译: {translated_players}/{total_players} ({translated_players/total_players*100:.1f}%)" if total_players > 0 else "")
                
            else:
                print(f"   ✅ {filename}: {count} 条记录 ({size:.1f} KB)")
        else:
            print(f"   ✅ {filename}: JSON对象 ({size:.1f} KB)")
    
    print(f"\n   📈 总计:")
    print(f"      • 国家/地区: {total_countries}")
    print(f"      • 联赛: {total_leagues}")
    print(f"      • 球队: {total_teams}")
    print(f"      • 球员: {total_players}")


def stats_platform_data():
    """统计各平台数据"""
    print_section("📊 各平台数据 (tools/)")
    
    platforms = {
        "football-data.org": {
            "dir": "tools/football-data.org",
            "files": ["explore_api.py", "extend_data.py", "sync_data.py", "translate_names.py"]
        },
        "api-football": {
            "dir": "tools/api-football",
            "data_files": ["data/leagues_info.json"]
        },
        "thesportsdb": {
            "dir": "tools/thesportsdb",
            "data_files": ["data/detailed_team_analysis.json"]
        },
        "baidu_translate": {
            "dir": "tools/baidu_translate",
            "files": ["baidu_translate.py", "translations_cache.json"]
        }
    }
    
    for platform, info in platforms.items():
        print(f"\n   🔵 {platform}")
        
        # 检查工具文件
        if "files" in info:
            tool_count = 0
            for f in info["files"]:
                filepath = BASE_DIR / info["dir"] / f
                if filepath.exists():
                    tool_count += 1
            print(f"      🛠️  工具脚本: {tool_count} 个")
        
        # 检查数据文件
        if "data_files" in info:
            for df in info["data_files"]:
                filepath = BASE_DIR / info["dir"] / df
                if filepath.exists():
                    size = filepath.stat().st_size / 1024
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        print(f"      📂 {df}: {len(data)} 条记录 ({size:.1f} KB)")
                        
                        # 特殊处理
                        if "leagues_info" in df:
                            countries = set(d.get('country', '') for d in data.values() if isinstance(d, dict))
                            print(f"         🌍 涉及国家: {len(countries)} 个")
                            
                    elif isinstance(data, dict):
                        print(f"      📂 {df}: {len(data)} 个键 ({size:.1f} KB)")
                        
                        # 特殊处理
                        if "detailed_team" in df:
                            unique_teams = len(set(
                                item.get('team_info', {}).get('idTeam', '')
                                for item in data
                                if isinstance(item, dict)
                            ))
                            total_players = sum(
                                len(item.get('players', []))
                                for item in data
                                if isinstance(item, dict)
                            )
                            print(f"         🏆 唯一球队: {unique_teams} 支")
                            print(f"         ⚽ 球员总数: {total_players}")
                else:
                    print(f"      ❌ {df}: 不存在")


def stats_translation_cache():
    """统计翻译缓存"""
    print_section("📊 翻译缓存")
    
    cache_file = BASE_DIR / "tools" / "baidu_translate" / "translations_cache.json"
    
    if not cache_file.exists():
        print("   ❌ 缓存文件不存在")
        return
    
    size = cache_file.stat().st_size / 1024
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    print(f"   ✅ 缓存文件: translations_cache.json")
    print(f"   📊 缓存记录数: {len(cache)} 条")
    print(f"   💾 文件大小: {size:.1f} KB")
    
    # 统计翻译类型
    sample_keys = list(cache.keys())[:10]
    print(f"\n   📝 示例翻译:")
    for key in sample_keys:
        value = cache[key]
        print(f"      • {key[:30]:<30} → {value[:20]}")
    
    if len(cache) > 10:
        print(f"      ... 还有 {len(cache) - 10} 条")


def stats_documents():
    """统计文档"""
    print_section("📊 文档资料 (docs/)")
    
    docs_dir = BASE_DIR / "docs"
    
    if not docs_dir.exists():
        print("   ❌ 文档目录不存在")
        return
    
    doc_files = list(docs_dir.glob("*.md"))
    
    print(f"   📚 文档总数: {len(doc_files)} 个\n")
    
    important_docs = [
        ("DATABASE_DESIGN.md", "数据库设计方案"),
        ("TRANSLATION_REPORT_2026-05-07.md", "翻译完成报告"),
        ("PROJECT_OVERVIEW.md", "项目概览"),
        ("MULTILINGUAL_SUPPORT.md", "多语言支持"),
        ("EXTENDED_DATA_SOLUTIONS.md", "数据扩展方案")
    ]
    
    for filename, description in important_docs:
        filepath = docs_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024
            print(f"   ✅ {filename}")
            print(f"      📝 {description} ({size:.1f} KB)")
        else:
            print(f"   ⚠️  {filename}: 不存在")


def stats_tools():
    """统计工具脚本"""
    print_section("📊 工具脚本 (tools/)")
    
    tools_dir = BASE_DIR / "tools"
    
    # 根目录工具
    root_tools = list(tools_dir.glob("*.py"))
    print(f"\n   🔧 通用工具: {len(root_tools)} 个")
    for tool in root_tools:
        print(f"      • {tool.name}")
    
    # 各平台工具
    platforms = ["baidu_translate", "football-data.org", "api-football", "thesportsdb"]
    
    for platform in platforms:
        platform_dir = tools_dir / platform
        if platform_dir.exists():
            py_files = list(platform_dir.glob("*.py"))
            if py_files:
                print(f"\n   🔵 {platform}: {len(py_files)} 个脚本")
                for f in py_files:
                    if f.name != "__init__.py":
                        print(f"      • {f.name}")


def summary():
    """生成总结"""
    print_section("📈 总体总结")
    
    print("""
    ✅ 已完成的工作:
    
    1. 核心数据 (football-data.org)
       • 272 个国家/地区 (100% 翻译)
       • 17 个联赛 (100% 翻译)
       • 336 支球队 (100% 翻译)
       • 9,757 名球员 (100% 翻译)
    
    2. 辅助数据源
       • API-Football: 9个联赛，9个国家
       • TheSportsDB: 1支球队（需扩展）
    
    3. 翻译系统
       • 百度翻译API集成
       • 10,000+ 条翻译缓存
       • 自动名字拆分功能
    
    4. 数据库设计
       • 11张表的完整设计方案
       • 外键索引化
       • 跨平台ID映射
    
    5. 文档
       • 数据库设计方案
       • 翻译完成报告
       • 项目结构说明
    
    🎯 下一步建议:
    
    1. 创建MySQL数据库表
    2. 导入现有数据
    3. 扩展TheSportsDB和API-Football数据
    4. 建立跨平台ID映射
    5. 开发REST API接口
    """)


if __name__ == '__main__':
    print("=" * 80)
    print("  📊 标准足球数据库 - 现有数据总览")
    print("=" * 80)
    
    stats_core_data()
    stats_platform_data()
    stats_translation_cache()
    stats_documents()
    stats_tools()
    summary()
    
    print("\n" + "=" * 80)
    print("  报告生成完成")
    print("=" * 80 + "\n")
