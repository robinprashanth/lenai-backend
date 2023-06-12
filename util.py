import os
import shutil
import datetime
import mimetypes

def move_files(source_folder, destination_folder):
    file_list = os.listdir(source_folder)
    for file_name in file_list:
        source = os.path.join(source_folder, file_name)
        destination = os.path.join(destination_folder, file_name)
        shutil.move(source, destination)


def readFiles(dirpath):
    file_data = []

    for root, _, files in os.walk(dirpath):
        for filename in files:
            filepath = os.path.join(root, filename)
            if not os.path.isdir(filepath):  # Exclude directories
                file_stats = os.stat(filepath)
                file_size = file_stats.st_size
                file_created = datetime.datetime.fromtimestamp(file_stats.st_ctime)
                file_modified = datetime.datetime.fromtimestamp(file_stats.st_mtime)
                file_type = filename.split(".")[-1].upper()
                 # Get the MIME type of the file
                file_mime_type, _ = mimetypes.guess_type(filepath)
                file_mime_type = file_mime_type or "unknown"

                file_info = {
                    "filename": filename,
                    "path": filepath,
                    "createdBy": "Brian Hughes",
                    "createdAt": file_created.strftime("%B %d, %Y"),
                    "modifiedAt": file_modified.strftime("%B %d, %Y"),
                    "size": f"{file_size / (1024 * 1024):.2f} MB",
                    "type": file_type,
                    "mime": file_mime_type
                }
                file_data.append(file_info)
    return file_data

def readAllFiles(dirpath):
    file_data = []
    for root, _, files in os.walk(dirpath):
        for filename in files:
            filepath = os.path.join(root, filename)
            if not os.path.isdir(filepath):  # Exclude directories
                file_stats = os.stat(filepath)
                file_size = file_stats.st_size
                file_created = datetime.datetime.fromtimestamp(file_stats.st_ctime)
                file_modified = datetime.datetime.fromtimestamp(file_stats.st_mtime)
                file_type = filename.split(".")[-1].upper()

                # Get the MIME type of the file
                file_mime_type, _ = mimetypes.guess_type(filepath)
                file_mime_type = file_mime_type or "unknown"

                file_info = {
                    "filename": filename,
                    "path": filepath,
                    "createdBy": "Brian Hughes",
                    "createdAt": file_created.strftime("%B %d, %Y"),
                    "modifiedAt": file_modified.strftime("%B %d, %Y"),
                    "size": f"{file_size / (1024 * 1024):.2f} MB",
                    "type": file_type,
                    "mime": file_mime_type
                }
                file_data.append(file_info)
        return file_data