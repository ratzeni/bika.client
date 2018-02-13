import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'VERSION')) as f:
    __version__ = f.read().strip()

extra_files = [os.path.join(here, 'VERSION')]

AuthorInfo = (
    ("Atzeni Rossano", "ratzeni@crs4.it"),
)

setup(name="bikaclient",
      version=__version__,
      description="client package for bika lims",
      author=",".join(a[0] for a in AuthorInfo),
      author_email=",".join("<%s>" % a[1] for a in AuthorInfo),
      install_requires=['requests'],
      packages=['bikaclient'],
      include_package_data=True,
      package_data={'': extra_files},
      license='MIT',
      platforms="Posix; MacOS X; Windows",
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Topic :: Software Development"
                   "Topic :: Scientific/Engineering :: Bio-Informatics",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6"],
      )
