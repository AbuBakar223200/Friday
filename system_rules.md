# F.R.I.D.A.Y. System Rules

This file documents core restrictions and guidelines for F.R.I.D.A.Y. and any AI agents working on this project.

## CORE RESTRICTION: C:\ Drive Access Forbidden
**NO ACCESS TO THE C:\ DRIVE.** 
F.R.I.D.A.Y. and any agent modifying this project are strictly forbidden from searching, modifying, or accessing files in the `C:\` drive unless explicitly targeting the project workspace. 
When executing local OS file queries (e.g. searching for movies, folders, documents), ONLY search the `E:\` and `D:\` drives. 
**Do not under any circumstances write code that exposes or modifies the C:\ drive.**

### EXCEPTION: Read-Only Start Menu Access
To dynamically map installed software, F.R.I.D.A.Y. is granted **STRICTLY READ-ONLY** access to the following directories:
- `C:\ProgramData\Microsoft\Windows\Start Menu\Programs`
- `%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs`
Under no circumstances may files in these directories be modified, deleted, or written to.
