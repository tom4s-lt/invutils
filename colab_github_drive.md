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

Since we are now in the project_folder we created earlier in the google drive, we can clone our GitHub repository inside this folder. For that, type in the following and run the cell.

```python
! git clone link/to/your/repo
```

**Note** Since we were working with datasets for the example (it's nice info to have just in case):
Finally, you have to upload the datasets to the drive first. It is fairly simple as all what you have to do is, to upload the dataset file inside the the ‘datasets’ folder under the clone repository. (There is no rule dictating that you should upload it to a folder inside the cloned repo. You can upload it anywhere inside the project_folder as long it is easily referenced and acceesible)


### Step 4: Running repo code
If you have an executable python file inside the cloned repo, you can run it using the following command after accessing the directory with that executable file.
```python
! python <executable_file.py>
```

Or else you can execute code directly from the colab cells. But first, you will have to import the functions from your git repo that are required for the execution. For example, let’s assume that you want to access a datset and the relavent functions are saved in a python file called file_handling.py under the subfolder ‘utilities’ in the cloned repo. To import these functions you can use the following code.
```python
from utilities.file_handling import *
```


# References/Bibliography
Simpler - https://medium.com/@ashwindesilva/how-to-use-google-colaboratory-to-clone-a-github-repository-e07cf8d3d22b

More extensive - https://medium.com/analytics-vidhya/how-to-use-google-colab-with-github-via-google-drive-68efb23a42d
- It creates a git repository on Drive

More Extensive - https://towardsdatascience.com/google-drive-google-colab-github-dont-just-read-do-it-5554d5824228
