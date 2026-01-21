import random
import time
import os
from app.bjdc.spider_data import get_bjdc_data
from app.crawler.spider_tczq import TczqSpider
from app.crawler.spider_jcbk import get_jcbk_data
from app.crawler.spider_lottery import LotterySpider
from app.common.logger import log
from sqlalchemy import create_engine


count = 0
def job():
    global count
    count += 1
    log.info(f'开始第{count}次任务执行')
    
    try:
        # 更新北京单场足球比赛结果
        bjdcdata = get_bjdc_data()
        bjdcdata.result_match()
        # 更新北京单场足球比赛数据和赔率
        bjdcdata.get_gamedata()
    except Exception as e:
        log.error(f'北京单场数据爬取失败: {str(e)}')
    
    try:
        # 更新足球比赛数据和赔率
        log.info('开始更新足球比赛数据')
        tczq_spider = TczqSpider()
        tczq_spider.get_current_matches()
    except Exception as e:
        log.error(f'足球数据爬取失败: {str(e)}')
    
    try:
        # 更新篮球比赛数据和赔率
        log.info('开始更新篮球比赛数据')
        jcbk_data = get_jcbk_data()
        jcbk_data.get_gamedata()
    except Exception as e:
        log.error(f'篮球数据爬取失败: {str(e)}')
    
    try:
        # 更新数字彩数据
        log.info('开始更新数字彩数据')
        lottery_spider = LotterySpider()
        lottery_spider.update_latest_lottery_data()
    except Exception as e:
        log.error(f'数字彩数据爬取失败: {str(e)}')

def init_db():
    """
    初始化所有数据库表结构和数据
    使用init_db.py中的init_all_databases函数
    """
    import sys
    import subprocess
    
    try:
        # 调用init_db.py脚本初始化所有数据库
        log.info('开始初始化所有数据库表结构和数据')
        result = subprocess.run([sys.executable, 'init_db.py'], 
                             capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # 输出执行结果
        if result.stdout:
            log.info(f'数据库初始化输出: {result.stdout}')
        if result.stderr:
            log.error(f'数据库初始化错误: {result.stderr}')
        
        if result.returncode == 0:
            log.info('Database created successfully')
            return True
        else:
            log.error('Database initialization failed')
            return False
    except Exception as e:
        log.error(f'数据库初始化异常: {str(e)}')
        return False


def up_db():
    """
    更新数据库表结构
    使用init_db.py中的功能更新所有表结构
    """
    import sys
    import subprocess
    
    try:
        # 由于init_db.py没有单独的更新函数，我们使用初始化函数但不删除现有表
        # 实际上，SQLAlchemy的create_all会自动创建不存在的表，不会删除现有表
        log.info('开始更新数据库表结构')
        
        # 我们可以通过调用每个模块的create_all来实现更新
        from config import config
        from sqlalchemy import create_engine
        from app.database.digital_lottery_models import Base as DigitalBase
        from app.database.tcbk_models import Base as TcbkBase
        from app.database.tczq_models import Base as TczqBase
        from app.database.bjdc_models import Base as BjdcBase
        
        db_config = config['local']
        engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        # 创建所有表（如果不存在）
        DigitalBase.metadata.create_all(engine)
        TcbkBase.metadata.create_all(engine)
        TczqBase.metadata.create_all(engine)
        BjdcBase.metadata.create_all(engine)
        
        log.info('Database updated successfully')
        print('Database updated')
        return True
    except Exception as e:
        log.error(f'数据库更新异常: {str(e)}')
        return False

def chuck_data():
    from app.database import localdb
    from app.database.tczq_models import TczqMatch

    localdb_done = False
    try:
        football = localdb.query(TczqMatch).first()
        if football is not None:
            localdb_done = True
        return localdb_done
    except Exception as e:
        log.error(e)
        return localdb_done

if __name__ == '__main__':
    localdone = chuck_data()
    if not localdone:
        init_db()

    log.info('开始任务')
    while True:
        job()
        delay = random.randint(10, 20)
        log.info(f'第{count}次任务执行完成,下一次在{delay}分钟后执行')
        delay = delay * 60
        time.sleep(delay)