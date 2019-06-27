#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name="loveisland",
    version="0.1.0",  # Defined in version.txt
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "get_tweets.py = loveisland.twitter.att1.run",
        ]
    },
    install_requires=[],
    # metadata for upload to PyPI
    author="Sam Watson",
    author_email="quadquants@gmail.com",
    description="Just me doing bits",
    url="http://www.soundcloud.com/quadras_music",
)
