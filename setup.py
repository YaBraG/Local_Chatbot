import os
import subprocess
import sys
import urllib.request
import ensurepip
import platform
import shutil

# Install pip if not already installed
def ensure_pip():
    try:
        import pip
        print("Pip Found!")
    except ImportError:
        print("Pip not found. Attempting to install pip...")
        try:
            # Try to use ensurepip (built-in in Python 3.4+)
            ensurepip.bootstrap()
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            print("Pip installed successfully!")
        except (ImportError, subprocess.CalledProcessError):
            # Fallback: Download and install pip manually if ensurepip fails
            try:
                pipurl = "get-pip.py"
                url = "https://bootstrap.pypa.io/get-pip.py"
                print(f"Downloading get-pip.py from {url}...")
                urllib.request.urlretrieve(url, pipurl)
                subprocess.check_call([sys.executable, pipurl])
                os.remove(pipurl)
                print("Pip installed successfully!")
            except Exception as e:
                print(f"Failed to install pip: {e}")
                sys.exit(1)

# Ensure Ollama is in PATH
def ensure_ollama_in_path():
    # Check if ollama is already in PATH
    if not shutil.which("ollama"):
        print("Ollama is not found in PATH. Attempting to add it...")
        current_os = platform.system()

        # Common installation paths for Ollama
        if current_os == "Windows":
            ollama_path = "C:\\Program Files\\Ollama"
        elif current_os == "Darwin":  # macOS
            ollama_path = "/Applications/Ollama.app/Contents/MacOS"
        else:  # Linux or other
            ollama_path = "/usr/local/bin"

        # Add Ollama to PATH if it exists in the standard path
        if os.path.isdir(ollama_path):
            add_directory_to_path(ollama_path)
            print(f"Added Ollama to PATH from {ollama_path}")
        else:
            print(f"Ollama not found in the default installation path ({ollama_path}). Please install Ollama or add it to PATH manually.")
            sys.exit(1)
    else:
        print("Ollama found in PATH.")

# Adds a directory to the system PATH if not already present.
def add_directory_to_path(directory):
    if directory not in os.environ['PATH']:
        os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']

# Setup environment based on the operating system
def setup_environment():
    python_dir = os.path.dirname(sys.executable)
    current_os = platform.system()

    # Add necessary directories to PATH for Windows or Linux/macOS
    if current_os == 'Windows':
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'Scripts'))
    elif current_os in ['Linux', 'Darwin']:
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'bin'))

    # Ensure Ollama is accessible in PATH
    ensure_ollama_in_path()

# Install the requirements
def install_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if not os.path.isfile(requirements_file):
        print("requirements.txt not found. Please ensure it's in the same directory as this script.")
        sys.exit(1)

    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("All required packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing packages: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ensure_pip()  # Ensure pip is installed before proceeding
    setup_environment()  # Setup environment and ensure Ollama in PATH
    install_requirements()  # Install required packages
