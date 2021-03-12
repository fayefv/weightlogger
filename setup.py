import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# with open("requirements.txt", "r") as rf:
#     requirements = rf.read().splitlines()
# causes pip to abort if it cannot find everything it needs
# so keep requirements separate

setuptools.setup(
    name="wlg_fayefv", # Replace with your own username
    version="0.1.5",
    author="Faye Fong",
    author_email="fong.faye@gmail.com",
    description="A simple weightlogging app to track personal fitness.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fayefv/weightlogger/tree/prettyGUI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
