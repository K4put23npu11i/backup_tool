# Backup Tool

|   |   |
|---|---|
| Titel | Backup Tool |
| Short Description | Tool for creating backups of directories |
| Start Date | 17.08.2021 |
| Working Time | 7,5 hours |
| Link to Git | [Link to Git](https://github.com/K4put23npu11i/backup_tool.git "Repo Link") |

# Detailed Description of project and its goals
The script will do backups of given directories. Therefore a matching list of source and destination directories is needed. 
The script will then copy and compress the whole directory from source to destination.

# Ordered list of action items
## MVP
- [x] Create test folder with directory and csv for src and dst
- [x] Load csv with backup instructions and loop over it
- [x] check if src exists else break
- [x] check if dst exists else create
- [x] create specific folder in dst with current date
- [x] setup function to copy directory
- [x] include compression in copy function

## Full Solution
- [x] include ordering from small files/folder to big files/folders
- [x] add information file with time, src, dst
- [x] delete "old" backups automatically
- [x] make sure, script is working with windows and linux
- [ ] include sth. to do the backup of multiple folders in parallel
- [x] create hash of src directory (or its folders); include in info file or create own
- [x] include possibility to shutdown PC after backup is finished

## Planned process
1. Check backup instructions. If not valid exit script
2. Loop existing instructions
3. Analyse existing backups. 
If x backups available, delete the oldest. 
Load latest info_dict from latest backup if available.
4. Analyse current source folder.
Split up in files and folders
create info_dict from source and use latest info_dict for backup decision
5. Perform actual backup.
Create new backup if changes since last time or no previous backup available. 
(Decision in previous analyse)
Start with files than folders.
6. Copy existing backup to new folder if no changes happened

# Collection of ideas
- only partial backup (compare hashes and only backup the directories that changed)
- create gui with tkinter
- create standalone exe
- include in autostart of PC for partial backup only
- include some kind of timing or progress bars



# Documentation
Nothing to document so far...


# Sources & additional Links
- Own ideas and interpretation of sources
- https://www.geeksforgeeks.org/copy-a-directory-recursively-using-python-with-examples/
- https://www.geeksforgeeks.org/python-shutil-copytree-method/
- https://codereview.stackexchange.com/questions/101616/simple-backup-script-in-python
- https://nitratine.net/blog/post/python-file-backup-script/
- https://gist.github.com/tompaton/1208368