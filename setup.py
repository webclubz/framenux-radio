#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="framenux-radio",
    version="1.0.0",
    description="Internet Radio Player",
    author="Framenux",
    packages=find_packages(),
    package_data={"assets": ["*.png"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "framenux-radio=src.ui.app:main",
        ],
    },
    install_requires=[
        # Add your dependencies here, for example:
        # "requests>=2.25.0",
        # "pygame>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
)