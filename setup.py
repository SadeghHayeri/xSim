from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup(
    name='xsim',
    version='1.0.3',
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
    install_requires=[
        'beautifulsoup4==4.9.0',
        'bs4==0.0.1',
        'certifi==2020.4.5.1',
        'chardet==3.0.4',
        'click==7.1.1',
        'confuse==1.1.0',
        'idna==2.9',
        'jdatetime==3.6.2',
        'PyYAML==5.3.1',
        'requests==2.23.0',
        'soupsieve==2.0',
        'terminaltables==3.1.0',
        'Unidecode==1.1.1',
        'urllib3==1.25.9',
        'yaspin==0.16.0',
        'lxml==4.5.0',
    ]
)
