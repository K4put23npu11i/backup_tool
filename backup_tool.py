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
import zipfile
import gzip
import restore_test_data_to_original_state

# Configure logging
logger = logging.getLogger()

# create file handler which logs even debug messages
filename = datetime.now().strftime(f'%Y%m%d_%H%M%S_{os.getlogin()}.log')
basepath = "./logs_backup_tool"
if not os.path.exists(basepath):
    os.makedirs(basepath)
fh = logging.FileHandler(f'{basepath}/{filename}', mode='w')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
fh.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)s [%(module)s - %(funcName)s()]: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
fh.setFormatter(formatter)
logger.addHandler(fh)
sh.setFormatter(formatter)
# logger.addHandler(sh)
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


def check_and_setup_directories(index: int, src: str, dst: str):
    """
    Checks if directories exists, create dir for destination if not already exists.

    Parameters
    ----------
    index: int
        index of backup instruction file
    src: str
        path to source folder
    dst: str
        path to destination folder

    Returns
    -------
    valid_src: bool
        Indicator if source path is valid and available
    valid_dst: bool
        Indicator if destination path is valid and available
    """
    valid_src, valid_dst = None, None
    # check src directory
    valid_src = os.path.exists(src)

    if valid_src is False:
        logger.error(f"Source directory does not exists! ({src})")
        print(f"Given source does not exist. No backup possible. ({src})")
        return valid_src, valid_dst

    # adapt dst path and check / create it
    today_str = datetime.now().strftime(f'%Y_%m_%d_backup_idx_{str(index)}')
    dst = os.path.join(dst, today_str)
    valid_dst = os.path.exists(dst)

    if valid_dst is False:
        os.makedirs(dst)
        logger.debug(f"Destination created: {dst}")
    valid_src, valid_dst = src, dst
    logger.debug(f"Source and Destination are valid.")
    return valid_src, valid_dst


def backup_folder_with_zipfile_method(src: str, dst: str):
    """

    Parameters
    ----------
    src
    dst

    Returns
    -------

    """
    dst = dst + ".zip"
    print(dst)
    zip_file = zipfile.ZipFile(str(dst), mode='w')

    for root, dirs, files in os.walk(src):
        for file in files:
            zip_file.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(src, '..')),
                           compress_type=zipfile.ZIP_DEFLATED)

    zip_file.close()


def backup_items_from_src_to_dst(src: str, dst: str, items: list, compression: str = None):
    for item in items:
        print(f"Processing item <{item}> from src ({src}) to dst ({dst})")
        logger.debug(f"Processing item {item} from src ({src}) to dst ({dst})")
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)
        start_time = datetime.now()
        if os.path.isfile(src_item):
            shutil.copyfile(src_item, dst_item)
            done_time = datetime.now()
            logger.debug(f"Backup file {item} from src ({src}) to dst ({dst}) done. Took {done_time - start_time}")
        elif os.path.isdir(src_item):
            if compression == "ZIPFILE":
                logger.debug(f"Copy and compress with ZIP")
                backup_folder_with_zipfile_method(src=src_item, dst=dst_item)
            elif compression == "shutil.make_archive":
                logger.debug(f"Copy and compress with shutil.make_archive")
                shutil.make_archive(dst_item, "zip", src_item)
            else:
                logger.debug(f"Copy and with NO compression")
                shutil.copytree(src_item, dst_item)
            done_time = datetime.now()
            logger.debug(f"Backup folder {item} from src ({src}) to dst ({dst}) done. Took {done_time - start_time}")
        else:
            logger.error(f"src_item ({src_item}) is not file nor folder! PROBLEM!!")


def perform_backup(src: str, dst: str):
    dir_content = os.listdir(src)
    files, folders = [], []

    for content in dir_content:
        logger.debug(f"Looping content of dir. Current content is: {content}")
        if os.path.isfile(os.path.join(src, content)):
            files.append(content)
        if os.path.isdir(os.path.join(src, content)):
            folders.append(content)
    logger.debug(f"Found {len(files)} files in total in src: {files}")
    logger.debug(f"Found {len(folders)} folders in total in src: {folders}")

    if len(files) > 0:
        backup_items_from_src_to_dst(src=src, dst=dst, items=files)

    if len(folders) > 0:
        # backup_items_from_src_to_dst(src=src, dst=dst, items=folders, compression="ZIPFILE")
        # backup_items_from_src_to_dst(src=src, dst=dst, items=folders, compression="TAR")
        backup_items_from_src_to_dst(src=src, dst=dst, items=folders, compression="shutil.make_archive")


def main():
    backup_instr_pd = read_backup_instructions(path=instructions_foldername, file=instructions_filename)

    if backup_instr_pd is None:
        return None
    else:
        for idx, row in backup_instr_pd.iterrows():
            logger.debug(f"Processing idx: {idx} with values: {row}")
            source, destination = check_and_setup_directories(index=idx, src=row["source"], dst=row["destination"])

            if source is None or destination is None:
                continue
            else:
                perform_backup(src=source, dst=destination)


if __name__ == "__main__":
    restore_test_data_to_original_state.main()  # Only for testing purposes
    main()
