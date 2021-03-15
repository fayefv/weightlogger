import setuptools
import pathlib
import re


requirements = []
pathtoreq = pathlib.Path(__file__).parent / "requirements.txt"
with open(pathtoreq, "r") as rf:
    for line in rf:
        requirements.append(re.split(r'[<>=]', line)[0])

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="wlg_fayefv", # Replace with your own username
    version="0.3.0",
    install_requires=requirements,
    author="Faye Fong",
    author_email="fong.faye@gmail.com",
    description="A simple weightlogging app to track personal fitness.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fayefv/weightlogger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
