import setuptools

setuptools.setup(
    name="mountainlab_pytools",
    version="0.2.5",
    author="Jeremy Magland",
    author_email="jmagland@flatironinstitute.org",
    description="Tools for using MountainLab with python",
    url="https://github.com/magland/mountainlab_pytools",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'numpy',
        'numpydoc'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)
