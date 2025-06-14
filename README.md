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

# Inner workings
The idea behind FolderDrop application is to enable file sharing through Universal Plug and Play – Internet Gateway Device protocol, which enables the app to automatically open ports on the router, making a local service available for access from the internet. This is achieved by using `igd` library in python. Below you can see a scheme of the how the protocol works.

   ![schem](https://github.com/user-attachments/assets/da32dbf7-5418-4345-b240-94135f6b682a)
