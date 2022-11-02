# How to use Google Colab with GitHub via Google Drive

Tutorial for using **Google Colab** can be used with **GitHub** and also use Google Drive as a cloud **Data Storage**.
https://medium.com/analytics-vidhya/how-to-use-google-colab-with-github-via-google-drive-68efb23a42d

1. Colaboratory, or **Colab** for short, is a product from Google Research. It allows anybody to write and execute arbitrary python code through the browser, and is especially well suited to machine learning, data analysis and education.
2. **GitHub** is a code hosting platform for version control and Collaboration. It lets you and others work together on projects from anywhere. Thus allowing seamless collaboration without compromising the integrity of the original project.
3. **Google Drive** provides file storage and synchronization service, which allows users to store files on their servers, synchronize files across devices, and share files. It offers 15 GB of free storage to users.

![image](https://user-images.githubusercontent.com/71655945/199617740-382b3c25-3ae2-4236-9ad6-ba581abe9138.png)

### Step 1: Use colab notebook as a shell

After you have pushed the project folder (without the dataset files) to the GitHub repo, you can go to your google drive and create a new folder (let’s call it the **project_folder**) to include your project related folders and files.
Access the project_folder. Right click on the background and select ‘colaboratory’ from the ‘more’ option in the dropdown menu that appears with the right click.

This starts a Colab notebook that will be used as a shell to run things in the directory chosen.

### Step 2: Mount Google Drive to Colab
Since we plan to store our project realted files in the **project_folder** we created earlier, we have to mount our google drive in to this runtime. In order to do that, type in the following in the first cell of your colab and run the cell.

- Run the below script to mount your Google Drive
``` python
from google.colab import drive  
drive.mount('/content/drive')
```
- Click the link to authenticate user Google account
- Select the respective Google Drive account on which you want to mount and click on sign in
- Copy and Paste the authentication code into the input cell
- Congrats! Your Google Drive is mounted

You have to confirm the linking - as with other google-accessing needs.

You can check the contents of the current folder in the runtime by typing the following and running the cell.
```python
! ls
```

If the drive is mounted correcly, you would see that the current folder has a directory called ‘gdrive’. This is where you can find your googlde drive contents. Now, to access the project_folder we created earlier, type in the following and run the cell.

### Step 3: Change present working directory

Below shell command will set the present working directory to `/content/drive/MyDrive/Github`
```python
%cd /content/drive/MyDrive/Github/
```
**Note:** Your Google Drive’s Home directory is at, `/content/drive/MyDrive/`

