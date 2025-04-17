from setuptools import setup, find_packages

setup(
    name='RichRDF',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    author='Hao Liang',
    description='A simple package to enhance your ROOT Data Frame, e.g., for reading edm4hepr.root',
    package_data={
        'richrdf': ['include/**/*.h'], 
    },
)

