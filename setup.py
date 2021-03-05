import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wlogger_fayefv", # Replace with your own username
    version="0.0.1",
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
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
