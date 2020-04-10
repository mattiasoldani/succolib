from setuptools import setup, find_packages

setup(
    author="Mattia Soldani",
    author_email="mattiasoldani93@gmail.com",
    name="succolib",
    version="2020.04.01",
    url="https://github.com/mattiasoldani/succolib",
    description="A set of handy tools for the INSULAb detectors data analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research",
    ],
)
