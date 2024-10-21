from os import path
from glob import glob
from langchain_community.document_loaders import PyPDFLoader

dir_path_name = "Data"

# Clear screen leaving just current session on display
print("\033c")

def get_training_files(dr,ext):
   training_files = glob(path.join(dr,"*.{}".format(ext)))
   training_set=[]
   for i in training_files:
      training_set.append(i.replace(f'{dir_path_name}\\',''))
   return training_set

# Load PDF
def get_pdf(dr):
    file_path= (f"Data\\{dr}")
    loader = PyPDFLoader(
        file_path = file_path,
        extract_images = True
        )
    return loader.load()

try:
    docs = []
    ts = get_training_files(dir_path_name,"pdf")
    previousTS = ts
    for i in ts:
        docs.append(get_pdf(i))
        print(docs)
    while True:
        currentTS = get_training_files(dir_path_name,"pdf")
        for i in currentTS:
            if i in previousTS:
                pass
            else:
                newPDF = i
                print(newPDF)
                docs.append(get_pdf(newPDF))
        previousTS = currentTS
  
except KeyboardInterrupt:
   print("Me fui")
