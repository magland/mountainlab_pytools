import setuptools

pkg_name="mountainlab_pytools"

setuptools.setup(
    name=pkg_name,
    version="0.7.5",
    author="Jeremy Magland",
    author_email="jmagland@flatironinstitute.org",
    description="Tools for using MountainLab with python",
    url="https://github.com/magland/mountainlab_pytools",
    packages=setuptools.find_packages(),
    package_data={
        '': ['mlproc/*.js']
    },
    install_requires=[
        'requests',
        'numpy',
        'numpydoc',
        'ipython',
        'vdom',
        'ipywidgets',
        'jp_proxy_widget'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)
