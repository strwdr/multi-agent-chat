import PyInstaller.__main__
import os
import shutil

def build_executable():
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # PyInstaller configuration
    PyInstaller.__main__.run([
        'main.py',
        '--name=Multi-Agent-Chat',
        '--onefile',
        '--windowed',
        '--icon=NONE',  # You can add an .ico file later
        '--add-data=LICENSE:.',
        '--add-data=README.md:.',
        '--clean',
        '--noconfirm'
    ])

    print("Build completed! Executable can be found in the 'dist' directory.")

if __name__ == "__main__":
    build_executable()
