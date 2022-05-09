import logging
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

file_name = '20-apr-2022.csv'

from augment import run_process

run_process(file_name)