# -*- coding: utf-8 -*-
"""
赛事状态编码定义
统一管理所有赛事类型的状态码

状态编码说明：
- 0: 待开赛
- 1: 进行中
- 2: 已完成（正常完场）
- 3: 延期/取消
- 4: 腰斩
- 5: 中断
- 8: 已获取赛果（完成状态标识）
- 9: 异常（超过4天无结果且无延期标识）
"""

# 状态编码 -> 中文描述字典
STATUS_DESC = {
    0: '待开赛',
    1: '进行中',
    2: '已完成',
    3: '延期',
    4: '腰斩',
    5: '中断',
    8: '已获取赛果',
    9: '异常',
}


def get_status_desc(status_code: int) -> str:
    """
    根据状态编码获取中文描述
    
    Args:
        status_code: 状态编码
        
    Returns:
        str: 中文描述，未知状态返回 '未知(xxx)'
    """
    return STATUS_DESC.get(status_code, f'未知({status_code})')


def map_to_internal_status(source_type: str, source_status) -> int:
    """
    将不同数据源的状态值映射为内部统一的状态编码
    
    Args:
        source_type: 数据源类型 ('bjdc', 'tczq', 'jcbk')
        source_status: 原始状态值（可能是字符串或数字）
        
    Returns:
        int: 内部状态编码
        
    Examples:
        >>> map_to_internal_status('bjdc', '完')
        8
        >>> map_to_internal_status('bjdc', '取消')
        3
        >>> map_to_internal_status('tczq', '2')  # matchResultStatus
        8
        >>> map_to_internal_status('jcbk', 2)    # status
        8
        >>> map_to_internal_status('jcbk', 1)    # status
        1
    """
    if source_type == 'bjdc':
        # BJDC网页状态文本映射
        bjdc_map = {
            '完': 8,        # 完场 -> 已获取赛果
            '取消': 3,      # 取消 -> 延期/取消
            '延期': 3,      # 延期 -> 延期/取消
            '腰斩': 4,      # 腰斩 -> 腰斩
            '中断': 5,      # 中断 -> 中断
        }
        return bjdc_map.get(str(source_status), 8)  # 默认已完成
    
    elif source_type == 'tczq':
        # TCZQ足球API状态映射 (matchResultStatus字段)
        tczq_map = {
            '2': 8,   # 已完成
            '3': 9,   # 异常
        }
        return tczq_map.get(str(source_status), 8)  # 默认已完成
    
    elif source_type == 'jcbk':
        # JCBK篮球API状态映射 (status字段)
        jcbk_map = {
            1: 1,   # 进行中
            2: 8,   # 已完成
        }
        return jcbk_map.get(source_status, 8)  # 默认已完成
    
    else:
        # 未知数据源，默认返回已完成
        return 8


def is_completed(status_code: int) -> bool:
    """判断是否已完成（已获取赛果）"""
    return status_code == 8


def should_skip_update(status_code: int) -> bool:
    """判断是否应该跳过更新（已完成或异常的比赛）"""
    return status_code in [8, 9]


def should_skip_result_fetch(status_code: int) -> bool:
    """判断是否应该跳过赛果获取（已获取赛果的比赛）"""
    return status_code == 8
