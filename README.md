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

