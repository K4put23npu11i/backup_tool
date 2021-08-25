"""
Created on Tue Aug 23 20:00:00 2021

@author: K4put23npu11i

Script to delete test backup folder and recreate it. For testing purposes only
"""

import os
import shutil


def main():
    cwd = os.getcwd()

    backup_folder_path = os.path.join(cwd, "data", "backup")

    if os.path.exists(backup_folder_path):
        shutil.rmtree(backup_folder_path)

    os.mkdir(backup_folder_path)

    print("Restore done.")


if __name__ == "__main__":
    main()
