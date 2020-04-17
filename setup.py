from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup(
    name='xsim',
    version='1.0.1',
    description='A command-line interface to manage MTN / MCI account',
    long_description_content_type="text/markdown",
    long_description=README,
    license='GPL 3.0',
    packages=find_packages(),
    author='Sadegh Hayeri',
    author_email='hayerisadegh@gmail.com',
    keywords=['Irancell', 'MTN', 'MCI', 'simcart'],
    url='https://github.com/SadeghHayeri/xSim',
    download_url='https://pypi.org/project/xsim',
    include_package_data=True,
    entry_points={
        "console_scripts": ['xsim = src.cli.cli:main']
    },
)
