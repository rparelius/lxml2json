import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lxml2json",
    version="0.2.0",
    author="Robert Parelius",
    author_email="rparelius@gmail.com",
    description="converts XML elements into their JSON equivalent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rparelius/lxml2json",
    packages=setuptools.find_packages(),
    install_requires=['lxml'],    
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
