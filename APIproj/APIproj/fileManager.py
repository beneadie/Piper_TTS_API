import os

def delete_file(file_path):
     # errors are handled in the api call
     os.remove(file_path)

def returnFileNames(userID, pathToUserFoler=None):
     if pathToUserFoler == None:
          folder_path = f"./outputs/{userID}"
     else:
          folder_path = pathToUserFoler
     # List all files in the directory
     files = os.listdir(folder_path)
     #errors are handled in the api call
     return files
