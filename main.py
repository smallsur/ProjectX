import logging

from database import create_or_update_district, create_or_update_district_include_rel
from database import getdistrict_by_name
from utils import get_log_format
import config

logfile = getattr(config.cfg, 'logfile')

logging.basicConfig(level=logging.DEBUG, format=get_log_format(thread_info=True, process_info=True), filename=logfile, filemode='w')

if __name__ == "__main__":
    