from setuptools import setup, find_packages

setup(name='ytmusicapi',
      version='0.1',
      description='Unofficial YTMusic API',
      long_description=(open('README.md').read()),
      url='https://github.com/sigma67/ytmusicapi',
      author='sigma67',
      author_email='',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False
)
