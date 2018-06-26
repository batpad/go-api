import logging
import sys
import os
from azure_storage_logging.handlers import QueueStorageHandler

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)

logger = logging.getLogger('api')
logger.setLevel('DEBUG')
logger.addHandler(screen_handler)

if (os.environ.get('AZURE_STORAGE_ACCOUNT') is not None and
        os.environ.get('AZURE_STORAGE_KEY') is not None):
    handler = QueueStorageHandler(account_name=os.environ.get('AZURE_STORAGE_ACCOUNT'),
                                  account_key=os.environ.get('AZURE_STORAGE_KEY'),
                                  queue='api',
                                  )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
