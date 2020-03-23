from distutils.core import setup

setup(
    name="aiopulse",
    packages=["aiopulse"],
    version="0.1",
    license="apache-2.0",
    description="Python module to talk to Rollease Acmeda Automate Pulse Hub roller bind using asyncio.",
    author="Alan Murray",
    author_email="pypi@atmurray.net",
    url="https://github.com/atmurray/aiopulse",
    download_url="https://github.com/atmurray/aiopulse/archive/v0.1.tar.gz",
    keywords=["automation"],
    install_requires=["asyncio", "async_timeout",],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
        "License :: OSI Approved :: Apache Software License v2.0",
        "Programming Language :: Python :: 3",
    ],
)
