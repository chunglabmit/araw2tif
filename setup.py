from setuptools import setup

version = "1.0.0"
with open("./README.md") as fd:
    long_description = fd.read()

setup(
    name="araw2tif",
    version=version,
    description="Utility for copying .raw files to .tiff",
    long_description=long_description,
    install_requires=[
        "tifffile",
        "tsv",
        "tqdm"
    ],
    author="Kwanghun Chung Lab",
    packages=["araw2tif"],
    entry_points=dict(
        console_scripts="araw2tif=araw2tif.main:main"
    ),
    url="https://github.com/chunglabmit/araw2tiff",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Topic :: System :: Archiving :: Backup"
    ]
)