from os import path
from glob import glob

# Directory where training files are stored
data_directory = "Data"

# Function to retrieve files of a specific extension from a directory
def get_files_by_extension(directory, extension):
    files = glob(path.join(directory, f"*.{extension}"))
    return files

print(get_files_by_extension(data_directory, "pdf"))

# Function to remove directory prefix from file paths in the training set
def strip_directory_prefix():
    training_files = get_files_by_extension(data_directory, "pdf")
    file_names = [path.basename(file) for file in training_files]
    return file_names

print(strip_directory_prefix())

# Monitor for newly added PDF files in the directory
try:
    previous_file_set = get_files_by_extension(data_directory, "pdf")
    while True:
        current_file_set = get_files_by_extension(data_directory, "pdf")
        for file_path in current_file_set:
            if file_path not in previous_file_set:
                new_pdf_file = file_path
                print(new_pdf_file)
        previous_file_set = current_file_set

except KeyboardInterrupt:
    print("Process interrupted by user")
