from setuptools import setup, find_packages
import re

VERSIONFILE = 'ytmusicapi/_version.py'

version_line = open(VERSIONFILE).read()
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(version_re, version_line, re.M)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '%s'" % VERSIONFILE)

setup(name='ytmusicapi',
      version=version,
      description='Unofficial API for YouTube Music',
      long_description=(open('README.rst').read()),
      url='https://github.com/sigma67/ytmusicapi',
      author='sigma67',
      author_email='',
      license='MIT',
      packages=find_packages(),
      install_requires=['requests >= 2.22'],
      extras_require={
          'dev': ['pre-commit', 'flake8', 'yapf', 'coverage', 'sphinx', 'sphinx-rtd-theme']
      },
      python_requires=">=3.5",
      include_package_data=True,
      zip_safe=False)
