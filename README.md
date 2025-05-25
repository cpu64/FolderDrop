# FolderDrop
Enjoy common storage of files with your friends by sharing a folder on your computer!

# Run the app
1. Run the `FolderDrop.py` file
2. You will see a window popup, where you will choose the directory to share and other options
   
   ![image](https://github.com/user-attachments/assets/05746a52-35ea-4483-81de-a0f547ff256e)
3. A new window will popup, where you can copy the link to your localhost or an IP address if you want to share over the internet
4. Another person will paste the IP address in their browser and arrive to a login page if you set a password

   ![image](https://github.com/user-attachments/assets/af3fcaed-ce57-4fb2-b7df-42ef58951630)

5. Once the correct password is provided, they will arrive to a shared directory
   
    ![image](https://github.com/user-attachments/assets/7ab82be8-f470-49ed-97bf-412ea5a58cc1)

6. In the directory, a user can do many actions, like download, rename, share, delete files and folders, create new directories and also see information about the content, like space used, modification dates, number of items etc.
   
    ![image](https://github.com/user-attachments/assets/dc77cd76-92cd-4edc-a97b-20053c801950)   

# Team Members
* Marius 
* Dovydas Jonuška
* Bernardas Gustas


# Tests

| Action | Desired outcome | Actual outcome |
| ------------- | ------------- | ------------- |
| Program is launched with `--no-gui` argument | Program prints a list of links for the server with the default `./share` directory | Program prints a list of links for the server with the default `./share` directory |
| Program is launched with `--no-downloading` | Downloading is disabled; users cannot download files from the shared directory | Downloading is disabled; users cannot download files from the shared directory |
| Program is launched with `--no-uploading` | Uploading is disabled; users cannot upload files to the shared directory | Uploading is disabled; users cannot upload files to the shared directory |
| Program is launched with `--no-public` | Server is only accessible on the local network (not exposed to internet) | Server is only accessible on the local network (not exposed to internet) |
| Program is launched with `--renaming` | Users are allowed to rename files in the shared directory | Users are allowed to rename files in the shared directory |
| Program is launched with `--deleting` | Users are allowed to delete files in the shared directory | Users are allowed to delete files in the shared directory |
| Program is launched with `-P 12345` | Server runs on port 12345 instead of the default 50505 | Server runs on port 12345 instead of the default 50505 |
| Program is launched with `-d ./mydata` | Shares the `./mydata` directory instead of the default `./share` | Shares the `./mydata` directory instead of the default `./share` |
| Program is launched with `-s 1000000` | Max size of directory set to \~1MB | Max size of directory set to \~1MB |
| Program is launched with `-p mypass` | Password protection is enabled with password `mypass` | Password protection is enabled with password `mypass` |
| Program is launched with no arguments | Setup GUI appears with default parameters | Setup GUI appears with default parameters |
| `Select directory` button is pressed | Select folder window appears | Select folder window appears |
| Folder is selected and `Select folder` button is pressed | Select folder window dissapears and the path of the selected folder appears in Setup GUI | Select folder window dissapears and the path of the selected folder appears in Setup GUI |
| `Max size` field is edited | The value updates and is saved as the new maximum directory size | The value updates and is saved as the new maximum directory size |
| Unit (B, KiB, MiB, etc.) is changed in dropdown | Max size is interpreted in the selected unit | Max size is interpreted in the selected unit |
| `Require password` checkbox is toggled | Password input field appears/disappears accordingly | Password input field appears/disappears accordingly |
| Password is entered and GUI is started | Server requires password for access | Server requires password for access |
| `Allow sharing files over the internet` is checked/unchecked | Public/external link is shown/hidden in the GUI and server is/not accessible from the internet | Public/external link is shown/hidden in the GUI and server is/not accessible from the internet |
| `Allow downloading files` is checked/unchecked | Download buttons are enabled/disabled in the web UI | Download buttons are enabled/disabled in the web UI |
| `Allow uploading files` is checked/unchecked | Upload form is enabled/disabled in the web UI | Upload form is enabled/disabled in the web UI |
| `Allow renaming files` is checked/unchecked | Rename option is enabled/disabled in the web UI | Rename option is enabled/disabled in the web UI |
| `Allow deleting files` is checked/unchecked | Delete option is enabled/disabled in the web UI | Delete option is enabled/disabled in the web UI |
| `Remember settings` is checked and GUI is started | Settings are saved and pre-filled on next launch | Settings are saved and pre-filled on next launch |
| `Start FolderDrop` button is pressed | Setup window closes and main window/server starts | Setup window closes and main window/server starts |
| `Stop FolderDrop` button is pressed in main window | Server stops and application exits | Server stops and application exits |
| `Copy to clipboard` button is pressed next to a link | The corresponding link is copied to clipboard | The corresponding link is copied to clipboard |
| System tray icon is clicked | Main window is restored if hidden | Main window is restored if hidden |
| Main window is closed (X) | Window hides to system tray, server keeps running | Window hides to system tray, server keeps running |
| `Logs:` button is pressed | Log panel is shown/hidden | Log panel is shown/hidden |
| `Upload File` button is clicked | File picker dialog opens | File picker dialog opens |
| File is selected and `Submit` is clicked | File uploads and appears in the file list | File uploads and appears in the file list |
| Drag and drop a file onto the page | File uploads and appears in the file list | File uploads and appears in the file list |
| Drag and drop a folder onto the page | All files in the folder upload and appear in the file list | All files in the folder upload and appear in the file list |
| `Download Selected` is clicked with multiple files checked | A zip file containing the selected files is downloaded | A zip file containing the selected files is downloaded |
| `Delete Selected` is clicked with multiple files checked | Selected files are deleted from the list after confirmation | Selected files are deleted from the list after confirmation |
| Checkbox in table header (`select all`) is checked | All file checkboxes are checked | All file checkboxes are checked |
| Any file checkbox is unchecked | `Select all` checkbox is automatically unchecked | `Select all` checkbox is automatically unchecked |
| Right-click on a file row | Context menu appears with options | Context menu appears with options |
| `Download` in context menu is clicked on a folder | Folder is downloaded as a zip file | Folder is downloaded as a zip file |
| `Rename` in context menu is clicked | Prompt appears, file/folder is renamed after confirmation | Prompt appears, file/folder is renamed after confirmation |
| `Delete` in context menu is clicked | Confirmation dialog appears, file/folder is deleted if confirmed | Confirmation dialog appears, file/folder is deleted if confirmed |
| `Create new folder` in context menu is clicked | Prompt appears, new folder is created after confirmation | Prompt appears, new folder is created after confirmation |
| Notification appears after an action | Notification fades out after 5 seconds | Notification fades out after 5 seconds |
| Click on a file row (not a folder) | File is downloaded | File is downloaded |
| Click on a folder row | Navigates into the folder | Navigates into the folder |
| Press Backspace | Navigates to the parent folder | Navigates to the parent folder |
| Login page is loaded | Password input and submit button are visible | Password input and submit button are visible |
| Password is entered and `Submit` is clicked (correct password) | User is logged in and redirected to main page | User is logged in and redirected to main page |
| Password is entered and `Submit` is clicked (incorrect password) | Error message is shown, user stays on login page | Error message is shown, user stays on login page |
| Password field is empty and `Submit` is clicked | Browser prevents submission or shows required field warning | Browser prevents submission or shows required field warning |
| Page is refreshed after failed login | Error message is cleared | Error message is cleared |

