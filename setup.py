import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymacnet",
    version="0.0.1",
    author="Zander Nevitt",
    author_email="zandern@battgenie.life",
    description="A class based python interface for communication and control of Maccor cyclers over Macnet.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BattGenie/pymacnet.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6',
)