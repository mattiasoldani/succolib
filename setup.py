from setuptools import setup, find_packages

version = "2020.6.4"

setup(
    author="Mattia Soldani",
    author_email="mattiasoldani93@gmail.com",
    name="succolib",
    version=version,
    url="https://github.com/mattiasoldani/succolib",
    download_url = "https://github.com/mattiasoldani/succolib/archive/v"+version+".tar.gz",
    description="A set of handy, Python-based tools for the INSULAb detectors data analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">3.0",
    install_requires=[
        "numpy",
        "pandas",
        "tqdm",
        "uproot",
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research",
    ],
)
