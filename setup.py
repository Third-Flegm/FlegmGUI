from setuptools import setup, find_packages

setup(
    name="flegmgui",
    version="0.1.0",
    # Tells setuptools that the actual packages are inside the "src" directory
    package_dir={"": "src"},
    # Automatically finds "flegmgui" inside the "src" directory
    packages=find_packages(where="src"), 
)
