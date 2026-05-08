"""
百度翻译API工具
用于翻译球队、联赛等足球数据的英文名称为中文
"""
import requests
import hashlib
import random
import json
import time
from pathlib import Path

# 百度翻译API配置
BAIDU_APP_ID = "20260505002607377"
BAIDU_SECRET_KEY = "ShEF9X6XLHGVYj4R350T"
BAIDU_API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

# 语言代码映射
LANG_CODES = {
    'zh': 'zh',      # 中文
    'en': 'en',      # 英文
    'jp': 'jp',      # 日文
    'kor': 'kor',    # 韩文
    'fra': 'fra',    # 法语
    'spa': 'spa',    # 西班牙语
    'de': 'de',      # 德语
    'it': 'it',      # 意大利语
}


def make_sign(query, salt, app_id, secret_key):
    """
    生成签名
    sign = MD5(appid + q + salt + key)
    """
    sign_str = app_id + query + salt + secret_key
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    return sign


def translate_text(text, from_lang='en', to_lang='zh'):
    """
    翻译单个文本
    
    Args:
        text: 要翻译的文本
        from_lang: 源语言代码
        to_lang: 目标语言代码
    
    Returns:
        翻译后的文本，失败返回None
    """
    if not text or text.strip() == '':
        return text
    
    # 生成随机盐值
    salt = str(random.randint(32768, 65536))
    
    # 生成签名
    sign = make_sign(text, salt, BAIDU_APP_ID, BAIDU_SECRET_KEY)
    
    # 构建请求参数
    params = {
        'q': text,
        'from': from_lang,
        'to': to_lang,
        'appid': BAIDU_APP_ID,
        'salt': salt,
        'sign': sign
    }
    
    try:
        response = requests.get(BAIDU_API_URL, params=params, timeout=10)
        result = response.json()
        
        # 检查是否有错误
        if 'error_code' in result:
            print(f"  ❌ 翻译错误 [{result['error_code']}]: {result.get('error_msg', '未知错误')}")
            return None
        
        # 返回翻译结果
        translated = result['trans_result'][0]['dst']
        return translated
    
    except Exception as e:
        print(f"  ❌ 请求异常: {str(e)}")
        return None


def batch_translate(texts, from_lang='en', to_lang='zh', delay=1.2):
    """
    批量翻译文本列表（控制QPS）
    
    Args:
        texts: 文本列表
        from_lang: 源语言
        to_lang: 目标语言
        delay: 每次请求间隔秒数（百度标准版QPS=1，建议1.2秒）
    
    Returns:
        翻译结果字典 {原文: 译文}
    """
    results = {}
    total = len(texts)
    
    print(f"\n📝 开始批量翻译 ({total}条)")
    print(f"   从 {from_lang} → {to_lang}")
    print(f"   预计耗时: {total * delay:.0f}秒\n")
    
    for i, text in enumerate(texts, 1):
        print(f"[{i}/{total}] 翻译: {text[:50]}...")
        
        # 调用翻译API
        translated = translate_text(text, from_lang, to_lang)
        
        if translated:
            results[text] = translated
            print(f"   ✅ {translated}")
        else:
            results[text] = None
            print(f"   ⚠️  翻译失败，保留原文")
        
        # 控制请求频率（避免超过QPS限制）
        if i < total:
            time.sleep(delay)
    
    return results


def load_translation_cache(cache_file='translations_cache.json'):
    """
    加载翻译缓存
    
    Args:
        cache_file: 缓存文件路径
    
    Returns:
        缓存字典
    """
    cache_path = Path(cache_file)
    if cache_path.exists():
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_translation_cache(cache, cache_file='translations_cache.json'):
    """
    保存翻译缓存
    
    Args:
        cache: 缓存字典
        cache_file: 缓存文件路径
    """
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"\n💾 缓存已保存到: {cache_file}")


def translate_teams(teams_data, cache_file='translations_cache.json'):
    """
    翻译球队名称
    
    Args:
        teams_data: 球队数据列表（包含name字段）
        cache_file: 缓存文件路径
    
    Returns:
        翻译映射字典 {英文名: 中文名}
    """
    # 加载缓存
    cache = load_translation_cache(cache_file)
    
    # 提取需要翻译的球队名称
    team_names = list(set([team['name'] for team in teams_data if 'name' in team]))
    
    # 过滤掉已经翻译过的
    need_translate = [name for name in team_names if name not in cache]
    
    print(f"\n🏆 球队翻译任务")
    print(f"   总球队数: {len(team_names)}")
    print(f"   已有缓存: {len(team_names) - len(need_translate)}")
    print(f"   需要翻译: {len(need_translate)}")
    
    if need_translate:
        # 批量翻译
        new_translations = batch_translate(need_translate, 'en', 'zh')
        
        # 合并到缓存
        cache.update(new_translations)
        
        # 保存缓存
        save_translation_cache(cache, cache_file)
    
    # 构建完整映射
    translation_map = {name: cache.get(name, name) for name in team_names}
    
    return translation_map


def translate_leagues(leagues_data, cache_file='translations_cache.json'):
    """
    翻译联赛名称
    
    Args:
        leagues_data: 联赛数据列表（包含name字段）
        cache_file: 缓存文件路径
    
    Returns:
        翻译映射字典 {英文名: 中文名}
    """
    # 加载缓存
    cache = load_translation_cache(cache_file)
    
    # 提取需要翻译的联赛名称
    league_names = list(set([league['name'] for league in leagues_data if 'name' in league]))
    
    # 过滤掉已经翻译过的
    need_translate = [name for name in league_names if name not in cache]
    
    print(f"\n⚽ 联赛翻译任务")
    print(f"   总联赛数: {len(league_names)}")
    print(f"   已有缓存: {len(league_names) - len(need_translate)}")
    print(f"   需要翻译: {len(need_translate)}")
    
    if need_translate:
        # 批量翻译
        new_translations = batch_translate(need_translate, 'en', 'zh')
        
        # 合并到缓存
        cache.update(new_translations)
        
        # 保存缓存
        save_translation_cache(cache, cache_file)
    
    # 构建完整映射
    translation_map = {name: cache.get(name, name) for name in league_names}
    
    return translation_map


if __name__ == '__main__':
    # 测试翻译
    print("=" * 60)
    print("百度翻译API测试")
    print("=" * 60)
    
    test_texts = [
        "Beijing Guoan",
        "Chinese Super League",
        "Manchester United",
        "Premier League"
    ]
    
    print("\n🧪 测试翻译:")
    for text in test_texts:
        result = translate_text(text, 'en', 'zh')
        if result:
            print(f"   {text} → {result}")
        time.sleep(1.2)
    
    print("\n✅ 测试完成！")
