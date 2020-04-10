from setuptools import setup, find_packages

setuptools.setup(
    author="Mattia Soldani",
    author_email="mattiasoldani93@gmail.com",
    name="succolib",
    version="2020.04.01",
    url="https://github.com/mattiasoldani/succolib",
    description="A set of handy tools for the INSULAb detectors data analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
