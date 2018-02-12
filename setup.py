from setuptools import setup

AuthorInfo = (
    ("Atzeni Rossano", "ratzeni@crs4.it"),
)

setup(name="bikaclient",
      version='0.4',
      description="client package for bika lims",
      author=",".join(a[0] for a in AuthorInfo),
      author_email=",".join("<%s>" % a[1] for a in AuthorInfo),
      install_requires=['six'],
      packages=['bikaclient'],
      license='MIT',
      platforms="Posix; MacOS X; Windows",
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Topic :: Internet",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.5"],
      )
