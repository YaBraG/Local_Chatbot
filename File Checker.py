import requests
from pathlib import Path
import re
import nltk
import json
import numpy as np
import time
from datetime import datetime

# Iterate over all items in the directory and create a list of pathlib.PosixPath entries each detailing a path to a .txt training file
#.txt files are expected to be numered
def get_training_files(path):

   directory = Path(path)
   training_files = []

   for file in directory.iterdir():
      training_files.append(file)

   # Sort the list of pathlib.PosixPath entries based on numeric part of the .txt file
   """""
   1) files.sort(: This starts the sorting operation on the files list. The sort() method sorts the elements of the list in place.
   
   2) key=lambda x:: This is a key function used to customize the sorting order. Here, lambda x: defines an anonymous function that takes one argument x.
   
   3) re.search(r'\d+', x.stem): This part uses the re.search() function from the re module to search for a pattern in the file name.
      \d+ is a regular expression pattern that matches one or more digits. x.stem gives the base name of the file without the extension.

   4) .group(): This method returns the matched part of the string. In this case, it returns the matched digits as a string.
   
   5) int(...): This converts the matched string of digits to an integer. This is necessary because we want to sort the files numerically,
      not lexicographically.

   Putting it all together, this line sorts the list of files (files) based on the numeric part extracted from each file's name.
   The lambda function extracts this numeric part using a regular expression and converts it to an integer, which is then used as the sorting key.
"""""
   training_files.sort(key=lambda x: int(re.search(r'\d+', x.stem).group()))

   return training_files

training_set = get_training_files(r"C:\Users\elicona\OneDrive - Miami Dade College\Documents\GitHub\Local_Chatbot\Chinga tu madre")

print (training_set)