#!/usr/bin/env python

from setuptools import find_packages, setup

tests_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-flake8',
    'pytest-isort',
]

setup(
    name="bobslide",
    version="0.1.dev0",
    description="Create and store reveal.js-based slideshows in the cloud",
    author="Kozea",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-WeasyPrint',
    ],
    setup_requires=['pytest-runner'],
    tests_require=tests_requirements,
    extras_require={'test': tests_requirements}
)
