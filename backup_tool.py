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
import json
import zipfile
import gzip
from checksumdir import dirhash
import hashlib
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
    src: str
        path to source folder, None if not existing
    dst: str
        adjusted path to destination folder, None if src not existing
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

    if valid_dst is True:
        logger.debug(f"Destination already existing. Delete now")
        shutil.rmtree(dst)

    os.makedirs(dst)
    logger.debug(f"Destination created: {dst}")
    logger.debug(f"Source and Destination are valid.")
    return src, dst


def backup_folder_with_zipfile_method(src: str, dst: str):
    """
    Creates a compress folder and writes it to disc. Uses the zipfile library

    Parameters
    ----------
    src: str
        path to directory to be compressed
    dst: str
        path to directory where the zip file should be written to
    """
    if dst.endswith(".zip"):
        pass
    else:
        dst = dst + ".zip"
        logger.debug(f"Adjust dst with '.zip' ending. dst is now: {dst}")

    zip_file = zipfile.ZipFile(str(dst), mode='w')

    for root, dirs, files in os.walk(src):
        for file in files:
            zip_file.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(src, '..')),
                           compress_type=zipfile.ZIP_DEFLATED)

    zip_file.close()


def backup_items_from_src_to_dst(src: str, dst: str, items: list, compression: str = None):
    """
    Loops given items list and backup them from source to destination. Decide with compression about method.

    Parameters
    ----------
    src: str
        path where items are located
    dst: str
        path where backup should be stored
    items: list
        list of files/folders to be backuped
    compression: str
        indicator which compression method should be used
    """
    for item in items:
        print(f"Processing backup for item <{item}> from src ({src}) to dst ({dst})")
        logger.debug(f"Processing backup for item <{item}> from src ({src}) to dst ({dst})")
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)
        start_time = datetime.now()
        if os.path.isfile(src_item):
            shutil.copyfile(src_item, dst_item)
            done_time = datetime.now()
            logger.debug(f"Backup file <{item}> from src ({src}) to dst ({dst}) done. Took {done_time - start_time}")
        elif os.path.isdir(src_item):
            if compression == "ZIPFILE":
                logger.debug(f"Copy and compress with ZIP")
                backup_folder_with_zipfile_method(src=src_item, dst=dst_item)
            elif compression == "shutil.make_archive":
                logger.debug(f"Copy and compress with shutil.make_archive")
                shutil.make_archive(dst_item, "zip", src_item)
            else:
                logger.debug(f"Copy with NO compression")
                shutil.copytree(src_item, dst_item)
            done_time = datetime.now()
            logger.debug(f"Backup folder <{item}> from src ({src}) to dst ({dst}) done. Took {done_time - start_time}")
        else:
            logger.error(f"src_item ({src_item}) is not file nor folder! PROBLEM!!")
            raise Exception(f"src_item ({src_item}) is not file nor folder! PROBLEM!!")


def get_dir_size(path: str):
    """
    Walks given path and calculates the complete size of the directory or calculates size directly if path is a file

    Parameters
    ----------
    path: str
        Path to directory

    Returns
    -------
    total_size: int
        Size of given Path in bytes
    """
    total_size = 0

    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for i in filenames:
                # use join to concatenate all the components of path
                f = os.path.join(dirpath, i)

                # use getsize to generate size in bytes and add it to the total size
                total_size += os.path.getsize(f)

    elif os.path.isfile(path):
        total_size = os.path.getsize(path)
    else:
        raise Exception("Should not be reached!!")

    return total_size


def build_checksum_of_directory(dir: str, ex_files: list = [], ex_ext: list = [], hash_func: str = 'sha256'):
    """
    Builds a checksum of the given directory to check for changes. Uses https://pypi.org/project/checksumdir/

    Parameters
    ----------
    dir: str
        directory to create hash of
    ex_files: list
        list of files to be excluded of the hash creation
    ex_ext:
        list of file extensions to be excluded from the hash creation
    hash_func: str
        method of hash algorithm

    Returns
    -------
    hash: str
        hash string of given directory
    """
    allowed_hash_functions = ['md5', 'sha1', 'sha256']  # fast, but "insecure" --> slow but more secure

    if os.path.exists(dir) and hash_func in allowed_hash_functions:
        hash = dirhash(dir, hash_func, excluded_files=ex_files, excluded_extensions=ex_ext)
        return hash
    else:
        return None


def build_hash_of_file(filepath: str, hash_func: str = 'sha256'):
    """
    Returns a hash string of given file with hashlib

    Parameters
    ----------
    filepath: str
        path to file to be hashed
    hash_func: str
        indicator for hash function to be used. one of ['md5', 'sha1', 'sha256']

    Returns
    -------
    hash: str
        hexdigest of created file hash as string
    """
    allowed_hash_functions = ['md5', 'sha1', 'sha256']  # fast, but "insecure" --> slow but more secure
    buf_size = 65536

    if os.path.exists(filepath) and os.path.isfile(filepath) and hash_func in allowed_hash_functions:
        hash = eval("hashlib." + hash_func + "()")
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()
    else:
        return None


def update_info_dict_with_items(inf_dict: dict, src: str, items: list, prefix: str):
    """
    Loops given list of items located in src. Collects some property information and writes everything to a info dict

    Parameters
    ----------
    inf_dict: dict
        collection of information about backup process
    src: str
        path to directory where items are located
    items: list
        list of files/folders located in src
    prefix: str
        indicator for files or folder

    Returns
    -------
    inf_dict: dict
        adjusted collection of information about backup process
    """
    items_info = []
    for item in items:
        logger.debug(f"Append info_dict for {prefix} <{item}>")
        if prefix == "file":
            hash = build_hash_of_file(filepath=os.path.join(src, item), hash_func="md5")
        elif prefix == "folder":
            hash = build_checksum_of_directory(dir=os.path.join(src, item), hash_func='md5')
        else:
            hash = None

        item_info = {
            f"{prefix}_name": item,
            f"{prefix}_size": get_dir_size(path=os.path.join(src, item)),
            f"{prefix}_hash": hash
            }
        items_info.append(item_info)

    inf_dict[f"found_{prefix}s"] = items_info
    return inf_dict


def perform_backup(src: str, dst: str):
    """
    Performs a backup from src directory to destination directory. Collection of function calls

    Parameters
    ----------
    src: str
        path to source directory of backup
    dst: str
        path to destination directory of backup
    """
    dir_content = os.listdir(src)
    files, folders = [], []
    info_dict = {
        "start_time": datetime.now().strftime('%Y%m%d_%H%M%S'),
        "end_time": "",
        "source_path": src,
        "destination_path": dst
    }

    for content in dir_content:
        if os.path.isfile(os.path.join(src, content)):
            files.append(content)
        if os.path.isdir(os.path.join(src, content)):
            folders.append(content)
    logger.debug(f"Found {len(files)} files in total in src: {files}")
    logger.debug(f"Found {len(folders)} folders in total in src: {folders}")

    if len(files) > 0:
        logger.debug("Start building info_dict for files and then backup them")
        files.sort(key=lambda f: get_dir_size(path=os.path.join(src, f)), reverse=False)  # sort from small to big
        info_dict = update_info_dict_with_items(inf_dict=info_dict, src=src, items=files, prefix="file")

        backup_items_from_src_to_dst(src=src, dst=dst, items=files)

    if len(folders) > 0:
        logger.debug("Start building info_dict for folders and then backup them")
        folders.sort(key=lambda f: get_dir_size(path=os.path.join(src, f)), reverse=False)  # sort from small to big
        info_dict = update_info_dict_with_items(inf_dict=info_dict, src=src, items=folders, prefix="folder")

        # backup_items_from_src_to_dst(src=src, dst=dst, items=folders, compression="ZIPFILE")
        backup_items_from_src_to_dst(src=src, dst=dst, items=folders, compression="shutil.make_archive")

    # write information to dst folder
    logger.debug("Start writing backup info_dict to disk")
    info_dict["end_time"] = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_content_txt = json.dumps(info_dict, indent=4)
    file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_backup_information.txt"
    with open(os.path.join(dst, file_name), "w") as file:
        file.write(file_content_txt)
    logger.debug(f"Backup info_dict written to {file_name}")


def load_info_dict_from_backup_folder(folder_path: str):
    """
    Returns loaded dict file with constant file name from given path

    Parameters
    ----------
    folder_path: str
        Path to backup folder

    Returns
    -------
    dict: dict
        loaded dictionary from folder path
    """

    folder_cont = os.listdir(folder_path)
    backup_file_name = ""
    logger.debug(f"Loop path content to find backup_information file.")
    for entry in folder_cont:
        entry_path = os.path.join(folder_path, entry)
        if os.path.isfile(entry_path) and "backup_information" in entry:
            backup_file_name = entry

    if backup_file_name == "":
        logger.error("File could not be found. Return None")
        return None

    # Load file
    with open(os.path.join(folder_path, backup_file_name), 'r', encoding='utf-8') as f:
        dict = json.load(f)
    logger.debug(f"Content of latest backup info file: {dict}")

    return dict


def analyze_existing_backups(backup_path: str, max_num_backups: int = 3):
    """
    Analyzes the given path for backups and delete existing backups if more than given number exists and loads the
    information dictionary about the latest backup.

    Parameters
    ----------
    backup_path: str
        path to folder where backups get stored
    max_num_backups: int
        Limit of existing backups

    Returns
    -------
    latest_backup_dict: dict

    """
    latest_backup_dict = None

    if os.path.exists(backup_path) and os.path.isdir(backup_path):
        folder_content = os.listdir(backup_path)
        if len(folder_content) > 0:
            backup_folders = []
            for f in folder_content:
                f_path = os.path.join(backup_path, f)
                logger.debug(f"Checking file/folder {f}")
                if os.path.isdir(f_path) and "backup" in f:
                    backup_folders.append(f)

            sorted_backup_folders = sorted(backup_folders, reverse=True)
            logger.debug(f"Found {len(sorted_backup_folders)} folders.")
            logger.debug(f"backup_folders: {sorted_backup_folders}")

            # delete backups if too many exist
            while len(sorted_backup_folders) >= max_num_backups:
                folder_to_delete = sorted_backup_folders.pop()
                logger.debug(f"folder_to_delete: {folder_to_delete}")
                shutil.rmtree(os.path.join(backup_path, folder_to_delete))

            # load latest info dict
            if len(sorted_backup_folders) > 0:
                still_existing_backups = sorted(sorted_backup_folders, reverse=True)
                backup_folder_path = os.path.join(backup_path, still_existing_backups[0])
                logger.debug(f"Latest backup folder path: {backup_folder_path}")
                latest_backup_dict = load_info_dict_from_backup_folder(folder_path=backup_folder_path)

    else:
        print("Could not load info about latest backup. Either no backup exists or given path is invalid.")
        logger.debug(f"Either no backup exists or given path is invalid. ({backup_path})")

    return latest_backup_dict


def main():
    main_start_time = datetime.now()
    logger.debug("Start of main function of backup script")
    backup_instr_pd = read_backup_instructions(path=instructions_foldername, file=instructions_filename)

    if backup_instr_pd is None:
        return None
    else:
        for idx, row in backup_instr_pd.iterrows():
            # logger.debug(f"Processing idx: {idx} with values: {row}")
            for header in list(backup_instr_pd.columns):
                logger.debug(f"Processing idx: {idx} with values: Header: {header}; Value: {row[header]}")

            latest_info_dict = analyze_existing_backups(backup_path=row["destination"], max_num_backups=3)

            source, destination = check_and_setup_directories(index=idx, src=row["source"], dst=row["destination"])

            if source is None or destination is None:
                continue
            else:
                perform_backup(src=source, dst=destination)

    end_time = datetime.now()
    logger.debug(f"Backup script is finished. Took {end_time - main_start_time}")

if __name__ == "__main__":
    main()
