import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymacnet",
    version="0.0.3",
    author="Zander Nevitt",
    author_email="zandern@battgenie.life",
    description="A class based python interface for communication and control of Maccor cyclers over Macnet.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BattGenie/pymacnet.git",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license='MIT',
)
