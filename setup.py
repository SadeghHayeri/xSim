from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='xsim',
    version='1.0.0',
    description='Manage MTN / MCI account from the terminal',
    long_description_content_type="text/markdown",
    long_description=README,
    license='GPL-3.0',
    packages=find_packages(),
    author='Sadegh Hayeri',
    author_email='hayerisadegh@gmail.com',
    keywords=['Irancell', 'MTN', 'MCI', 'simcart'],
    url='https://github.com/SadeghHayeri/xSim',
    download_url='https://pypi.org/project/xsim'
)

install_requires = [
    'beautifulsoup4==4.9.0',
    'bs4==0.0.1',
    'certifi==2020.4.5.1',
    'chardet==3.0.4',
    'confuse==1.1.0',
    'idna==2.9',
    'PyYAML==5.3.1',
    'requests==2.23.0',
    'soupsieve==2.0',
    'urllib3==1.25.8',
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)