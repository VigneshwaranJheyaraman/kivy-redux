import setuptools

with open('README.md','r') as readme_file:
    DOCUMENTATION = readme_file.read()

setuptools.setup(
    name='kivyredux',
    version='1.0',
    author='VickySuraj',
    author_email='vigneshwaranjheyaraman@gmail.com',
    description='kivyredux - Redux for Kivy',
    long_description=DOCUMENTATION,
    long_description_content_type="text/markdown",
    url="https://github.com/VigneshwaranJheyaraman/kivy-redux",
    classifiers=[
        "Programming Language :: Python :: 3 or above",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3'
)