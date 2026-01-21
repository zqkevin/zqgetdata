# 使用示例
import logging
import sys


class CustomLogger:
    def __init__(self, log_file_name='app.log', level=logging.INFO):
        self.logger = logging.getLogger('CustomLogger')
        self.logger.setLevel(level)

        # 创建一个handler，用于写入日志文件
        file_handler = logging.FileHandler(log_file_name)
        file_handler.setLevel(level)

        # 创建一个handler，用于写入控制台
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)

        # 创建一个formatter，用于设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)


log = CustomLogger('zqdata_log_file.log')
