from setuptools import setup, find_packages

version = "2021.1.3"

setup(
    author="Mattia Soldani",
    author_email="mattiasoldani93@gmail.com",
    name="succolib",
    version=version,
    url="https://github.com/mattiasoldani/succolib",
    download_url = "https://github.com/mattiasoldani/succolib/archive/v"+version+".tar.gz",
    description="A set of handy, Python-based tools for the INSULAb detectors data analysis",
    long_description="This is **succolib**, a library of handy Python functions for High-Energy Physics beamtests data analysis. In particular, it has been developed with a focus on the event-by-event analysis of the data collected with the INSULAb detectors &mdash; see, for example, the experimental configurations described [here](http://cds.cern.ch/record/2672249), [here](http://hdl.handle.net/10277/857) and [here](http://cds.cern.ch/record/1353904). Details can be found in the [succolib GitHub page](https://github.com/mattiasoldani/succolib).",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">3.0",
    install_requires=[
        "numpy",
        "pandas",
        "tqdm",
        "uproot>=4.0",
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research",
    ],
)
