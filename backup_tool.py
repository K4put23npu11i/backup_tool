"""
Created on Tue Aug 17 20:00:00 2021

@author: K4put23npu11i

Script to perform backups of directories.
"""

import os
import shutil
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()

# create file handler which logs even debug messages
filename = datetime.now().strftime(f'%Y%m%d_%H%M%S_{os.getlogin()}.log')
basepath = "./logs_backup_tool"
if not os.path.exists(basepath):
    os.makedirs(basepath)
fh = logging.FileHandler(f'{basepath}/{filename}', mode='w')
fh.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s [%(module)s]: %(message)s', "%Y-%m-%d %H:%M:%S")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)


instructions_filename = "backup_instruction.csv"
instructions_foldername = "data"


def read_backup_instructions(path: str, file: str):
    """
    Return Pandas DataFrame with instructions for backups from given path to csv file
    Parameters
    ----------
    path: str
        folder path to csv file
    file: str
        name of csv file to read in

    Returns
    -------
    instructions_pd: pandas.core.frame.DataFrame
        Pandas DataFrame with read in csv data
    """
    file_path = os.path.join(path, file)
    logger.debug(f"Read file: {file_path}")
    if os.path.exists(file_path) and os.path.isfile(file_path):
        instructions_pd = pd.read_csv(file_path, sep=";", encoding="utf-8")
        logger.debug(f"Content is: {instructions_pd}")
        return instructions_pd

    else:
        logger.warning(f"file could not be found! ({file_path})")
        print(f"file could not be found! ({file_path})")
        return None


def main():
    backup_instr_pd = read_backup_instructions(path=instructions_foldername, file=instructions_filename)
    print(backup_instr_pd)


if __name__ == "__main__":
    main()
