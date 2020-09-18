import setuptools
from kivyredux import __version__

with open('README.md','r') as readme_file:
    DOCUMENTATION = readme_file.read()

setuptools.setup(
    name='kivyredux',
    version=__version__,
    author='VickySuraj',
    author_email='vigneshwaranjheyaraman@gmail.com',
    description='kivyredux - Redux for Kivy',
    long_description=DOCUMENTATION,
    long_description_content_type="text/markdown",
    url="https://github.com/VigneshwaranJheyaraman/kivy-redux",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3',
    keywords=['python','kivy','redux','pip'],
    install_requires=['Kivy>=1.1.0']
)