from os import path
from glob import glob

dir_path_name = "Data"
# Iterate over all items in the directory and create a list of pathlib.PosixPath entries each detailing a path to a .txt training file
#.txt files are expected to be numered
def get_training_files(dr,ext):
   training_files = glob(path.join(dr,"*.{}".format(ext)))
   return training_files

print ("\033c")

def killYourself():
   training_set = get_training_files(dir_path_name,"pdf")
   training_set2=[]
   for i in training_set:
      training_set2.append(i.replace(f'{dir_path_name}\\',''))
   return training_set2

print ( killYourself())

try:
   previousTS = killYourself()
   while True:
      currentTS = killYourself()
      for i in currentTS:
         if i in previousTS:
            pass
         else:
            newPDF = i
            print(newPDF)
      previousTS = currentTS
            
except KeyboardInterrupt:
   print("Me fui")