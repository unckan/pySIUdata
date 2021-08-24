from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='''siu-data''',
    version='0.3.7',
    description='''SIU data''',
    long_description=long_description,
    long_description_content_type='text/markdown', 
    url='https://github.com/unckan/pySIUdata',
    author='''Andres Vazquez''',
    author_email='''andres@data99.com.ar''',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='''SIU''',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'pyexcel>=-0.5.15',
        'pyexcel-xls>=0.5.8',
        'pyexcel-xlsx>=0.5.8',
        'python-slugify>=1.2.6',
    ],
    include_package_data=True,
)
