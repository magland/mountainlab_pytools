"""
Setup Module to setup mltools package
"""
import setuptools

setuptools.setup(
    name='mountainlab_pytools',
    version='0.1.0',
    description='Tools for using MountainLab with python',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests'
    ]
)
