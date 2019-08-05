#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name="loveisland",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "get_tweets.py = loveisland.pipeline.get_tweets.run",
            "preprocess.py = loveisland.pipeline.process_tweets.run",
            "get_topics.py = loveisland.pipeline.get_topics.run",
        ]
    },
    install_requires=[],
    author="Sam Watson",
    author_email="If you want this please just ask.",
    description="Love Island but with data.",
    url="https://github.com/watson-sam/loveisland",
)
