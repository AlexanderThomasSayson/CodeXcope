import os


# function to create folder for each file.
# this takes two parameters: base path and the folder name.
def create_folder(based_path, folder_name):
    folder_path = os.path.join(based_path, folder_name)
    # check if folder exists, if not create a directory folder.
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return folder_path
