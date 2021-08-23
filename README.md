# Backup Tool

|   |   |
|---|---|
| Titel | Backup Tool |
| Short Description | Tool for creating backups of directories |
| Start Date | 17.08.2021 |
| Working Time | 5hours |
| Link to Git | [Link to Git](https://github.com/K4put23npu11i/backup_tool.git "Repo Link") |

# Detailed Description of project and its goals
The script will do backups of given directories. Therefore a matching list of source and destination directories is needed. 
The script will then copy and compress the whole directory from source to destination.

# Ordered list of action items
## MVP
- [ ] Create test folder with directory and csv for src and dst
- [ ] Load csv with backup instructions and loop over it
- [ ] check if src exists else break
- [ ] check if dst exists else create
- [ ] create specific folder in dst with current date
- [ ] setup function to copy directory
- [ ] include compression in copy function
- [ ] search src directory to check what needs to be copied
- [ ] setup loop for csv and its directories

## Full Solution
- [ ] make sure, script is working with windows and linux
- [ ] add information file with time, src, dst
- [ ] include sth. to do the backup of multiple folders in parallel
- [ ] create hash of src directory (or its folders); include in info file or create own
- [ ] include possibility to shutdown PC after backup is finished

# Collection of ideas
- only partial backup (compare hashes and only backup the directories that changed)
- create gui with tkinter
- create standalone exe
- include in autostart of PC for partial backup only


# Documentation
Nothing to document so far...


# Sources & additional Links
- Own ideas and interpretation of sources
- https://www.geeksforgeeks.org/copy-a-directory-recursively-using-python-with-examples/
- https://www.geeksforgeeks.org/python-shutil-copytree-method/
- https://codereview.stackexchange.com/questions/101616/simple-backup-script-in-python
- https://nitratine.net/blog/post/python-file-backup-script/
- https://gist.github.com/tompaton/1208368