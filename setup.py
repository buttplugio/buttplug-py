from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="buttplug",
      version="0.0.2",
      author="Nonpolynomial",
      author_email="kyle@nonpolynomial.com",
      description="Python implementation of the Buttplug Intimate Hardware Control Protocol.",
      long_description=long_description,
      long_description_content_type='text/markdown',
      url="https://github.com/buttplugio/buttplug-py",
      classifiers=[
          "Programming Language :: Python :: 3",
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
      ],
      install_requires=['websockets>=7.0', ],
      packages=find_packages(exclude=["docs", "*.tests", "*.tests.*",
                                      "tests.*", "tests"]))
