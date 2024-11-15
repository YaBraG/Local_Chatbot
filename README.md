**How to Run**
- download Ollama: https://ollama.com/

**On the Windows Powershell**
- ollama run llama3.2:1b (The least resource consuming model)
- ollama serve (if error stating port already in use, then proceed with next command, as ollama is already running)
- ollama pull llama3 

**On terminal or VSCode**
Run program for specific pupose
- setup.py to install requieremnts and ensure everything is in order
- filesConversion.py for combine all PDFs in data folder (run this if new PDFs are addded)
- CUDAcheck.py for checking that CUDA and PyTorch aer woking correctly (Linux)
- llm.py for testing llm
- server.py for using a Flask server and access Flaskllm.py 

**Additional PDF Upload**
- If additional PDFs are required for upload, add PDFs to Data folder, before running main.py.

