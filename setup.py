"""Pip setup file for aiopulse library."""
from distutils.core import setup

setup(
    name="aiopulse",
    packages=["aiopulse"],
    version="0.3.3",
    license="apache-2.0",
    description="Python module for Rollease Acmeda Automate integration.",
    author="Alan Murray",
    author_email="pypi@atmurray.net",
    url="https://github.com/atmurray/aiopulse",
    download_url="https://github.com/atmurray/aiopulse/archive/v0.3.3.tar.gz",
    keywords=["automation"],
    install_requires=["asyncio", "async_timeout"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
)
