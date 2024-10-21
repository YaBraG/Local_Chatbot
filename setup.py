import os
import subprocess
import sys

# Check if pip is installed
try:
    import pip
except ImportError:
    print("Pip is not installed. Please install pip before proceeding.")
    sys.exit(1)

# Install the requirements
def install_requirements():
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All required packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing packages: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()
