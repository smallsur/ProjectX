import logging
import logging.config
import yaml

from .path import is_exist_file


class Log:
    _StreamLogger = None

    @staticmethod
    def init_log(file_: str):
        if is_exist_file(file_):
            with open(file_) as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config['logging'])

    @staticmethod
    def get_log(name: str):
        return logging(name)

    @staticmethod
    def shutdown():
        logging.disable(logging.INFO)

    @classmethod
    def logInfo(cls, level: int, message: str):
        if cls._StreamLogger is None:
            cls._StreamLogger = logging.getLogger('StreamLogger')

        cls._StreamLogger.info("  " * level + message)



