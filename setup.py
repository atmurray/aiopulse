"""Pip setup file for aiopulse library."""

from setuptools import setup

setup(
    name="aiopulse",
    packages=["aiopulse"],
    version="0.5.2",
    license="apache-2.0",
    description="Python module for Rollease Acmeda Automate integration.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Alan Murray",
    author_email="pypi@atmurray.net",
    url="https://github.com/atmurray/aiopulse",
    download_url="https://github.com/atmurray/aiopulse/archive/v0.5.2.tar.gz",
    keywords=["automation"],
    python_requires=">=3.12",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
)
