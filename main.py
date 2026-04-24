import random
import time
import os
from config import config
from sqlalchemy import create_engine

# 全局数据库配置（根据 config['db_type'] 自动选择环境）
db_type = config.get('db_type', 'local')
db_config = config[db_type]
DB_URL = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

from app.crawler import (
    TczqDataCollector, TczqResultCollector,
    JcbkDataCollector, JcbkResultCollector,
    BjdcDataCollector, BjdcResultCollector,
    LotteryDataCollector
)
from app.log.logger import tczq_log, bjdc_log, jcbk_log, lottery_log

# 默认使用体彩足球日志（向后兼容）
log = tczq_log

count = 0
def job():
    global count
    count += 1
    log.info(f'开始第{count}次任务执行')
    
    try:
        # 更新竞彩足球比赛信息和赛果
        tczq_log.info('开始更新竞彩足球比赛数据')
        tczq_collector = TczqDataCollector()
        tczq_collector.get_current_matches()
        
        tczq_log.info('开始更新竞彩足球比赛结果')
        tczq_result = TczqResultCollector()
        tczq_result.get_and_save_results()
    except Exception as e:
        tczq_log.error(f'足球数据爬取失败：{str(e)}')
        
    try:
        # 更新竞彩篮球比赛信息和赛果
        jcbk_log.info('开始更新篮球比赛数据')
        jcbk_collector = JcbkDataCollector()
        jcbk_collector.get_matches_with_odds()
        
        jcbk_log.info('开始更新篮球比赛结果')
        jcbk_result = JcbkResultCollector()
        jcbk_result.get_and_save_results()
    except Exception as e:
        jcbk_log.error(f'篮球数据爬取失败：{str(e)}')
    
    try:
        # 更新数字彩数据
        lottery_log.info('开始更新数字彩数据')
        lottery_collector = LotteryDataCollector()
        lottery_collector.update_latest_lottery_data()
    except Exception as e:
        lottery_log.error(f'数字彩数据爬取失败：{str(e)}')
        
    try:
        # 更新北京单场足球比赛信息和赛果
        bjdc_log.info('开始更新北京单场足球比赛信息')
        bjdc_collector = BjdcDataCollector()
        bjdc_collector.collect_matches()
        
        bjdc_log.info('开始更新北京单场足球比赛结果')
        bjdc_result = BjdcResultCollector()
        bjdc_result.get_and_save_results()
    except Exception as e:
        bjdc_log.error(f'北京单场数据爬取失败：{str(e)}')

def init_db(rebuild=False):
    """
    初始化所有数据库表结构和数据
    
    Args:
        rebuild: 是否重建数据库（删除所有表后重新创建）
                 - False: 仅创建不存在的表，保留现有数据
                 - True: 删除所有表并重新创建，清空所有数据
    
    Returns:
        bool: 初始化成功返回True，否则返回False
    """
    try:
        # 先关闭localdb的会话，避免事务冲突
        from app.database import localdb
        localdb.close()
        
        if rebuild:
            # 使用 app/common/init_db.py 进行完整重建
            log.info('开始完全重建数据库（将删除所有表并重新创建）')
            from app.common.init_db import init_all_databases
            result = init_all_databases()
            
            if result:
                log.info('数据库完全重建完成（包括表结构、联赛数据）')
                return True
            else:
                log.error('数据库重建失败')
                return False
        else:
            # 使用 app/common/init_restructured_db.py 进行增量更新（只创建不存在的表）
            log.info('开始初始化/更新数据库表结构（保留现有数据）')
            from app.common.init_restructured_db import init_restructured_database
            result = init_restructured_database()
            
            if result:
                log.info('数据库表结构初始化/更新完成')
                return True
            else:
                log.error('数据库初始化失败')
                return False
                
    except Exception as e:
        log.error(f'数据库初始化异常: {str(e)}')
        import traceback
        log.error(traceback.format_exc())
        return False


def up_db():
    """
    更新数据库表结构
    使用 SQLAlchemy 的 create_all 自动创建不存在的表，不会删除现有表
    """
    try:
        log.info('开始更新数据库表结构')
        
        # 导入各个模块的模型和 Base 类
        from app.database.digital_lottery_models import Base as DigitalBase
        from app.database.tcbk_models import Base as TcbkBase
        from app.database.base_models import Base as FbBase
        from app.database.tczq_models import Base as TczqBase
        from app.database.bjdc_models import Base as BjdcBase
        
        # 使用全局 DB_URL
        engine = create_engine(DB_URL)
        
        # 创建所有表（如果不存在）
        DigitalBase.metadata.create_all(engine)
        TcbkBase.metadata.create_all(engine)
        FbBase.metadata.create_all(engine)
        TczqBase.metadata.create_all(engine)
        BjdcBase.metadata.create_all(engine)
        
        log.info('Database updated successfully')
        print('Database updated')
        return True
    except Exception as e:
        log.error(f'数据库更新异常: {str(e)}')
        import traceback
        log.error(traceback.format_exc())
        return False

def chuck_data():
    """
    检查数据库中表是否已存在
    Returns:
        bool: 如果表已存在返回True，否则返回False
    """
    from app.database import localdb
    from sqlalchemy import inspect
    
    try:
        # 检查关键表是否存在（league, team, tczq_match, bjdc_match）
        inspector = inspect(localdb.engine)
        existing_tables = inspector.get_table_names()
        
        required_tables = ['league', 'team', 'tczq_match', 'bjdc_match']
        all_exist = all(table in existing_tables for table in required_tables)
        
        if all_exist:
            log.info(f'数据库表已存在，共 {len(existing_tables)} 个表')
            return True
        else:
            missing = [t for t in required_tables if t not in existing_tables]
            log.warning(f'缺少表: {missing}')
            return False
    except Exception as e:
        log.error(f'检查数据库异常: {str(e)}')
        return False

if __name__ == '__main__':
    import sys
    import logging
    
    # 设置标准输出编码为 UTF-8（解决 Windows 中文乱码问题）
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 配置根日志记录器，启用控制台输出
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除已有的 handler
    root_logger.handlers.clear()
    
    # 添加控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    print('\n' + '='*60)
    print('体育彩票数据采集系统启动')
    print('='*60 + '\n')
    
    # 检查是否需要重建数据库
    rebuild_db = '--rebuild' in sys.argv or '-r' in sys.argv
    
    if rebuild_db:
        log.info('检测到重建参数，将完全重建数据库')
        print('\n⚠️  警告：即将完全重建数据库，所有现有数据将被删除！')
        print('如果确认继续，请输入 "yes"：')
        confirm = input('> ').strip().lower()
        if confirm != 'yes':
            print('操作已取消')
            sys.exit(0)
    
    # 稳健的数据库初始化：无论什么情况都确保表结构存在
    log.info('检查数据库表结构...')
    try:
        localdone = chuck_data()
        if not localdone or rebuild_db:
            log.info('数据库表不完整或需要重建，开始初始化...')
            init_result = init_db(rebuild=rebuild_db)
            if not init_result:
                log.error('数据库初始化失败，但将继续尝试运行（可能部分功能不可用）')
        else:
            log.info('数据库表结构完整')
    except Exception as e:
        log.error(f'数据库检查/初始化异常: {str(e)}')
        log.warning('尝试继续运行，但可能会遇到数据库错误')
        import traceback
        log.error(traceback.format_exc())

    log.info('开始任务')
    
    # 使用 while True 循环，先执行任务再等待
    while True:
        job()
        delay = random.randint(10, 20)
        log.info(f'第{count}次任务执行完成,下一次在{delay}分钟后执行')
        delay = delay * 60
        time.sleep(delay)