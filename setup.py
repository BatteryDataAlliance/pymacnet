import os
import setuptools
from pip._internal.req import parse_requirements
from pip._internal.network.session import PipSession

this_dir = os.path.dirname(os.path.abspath(__file__))
pip_requirements = parse_requirements(
    os.path.join(this_dir, "requirements.txt"), PipSession())
reqs = [pii.requirement for pii in pip_requirements]
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymacnet",
    version="0.0.2",
    author="Zander Nevitt",
    author_email="zandern@battgenie.life",
    description="A class based python interface for communication and control of Maccor cyclers over Macnet.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BattGenie/pymacnet.git",
    packages=setuptools.find_packages(),
    install_requires=reqs,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license='MIT',
)
