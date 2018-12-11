import setuptools

pkg_name="mountainlab_pytools"

setuptools.setup(
    name=pkg_name,
    version="0.7.4",
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
    conda={
        "build_number":0,
        "build_script":[
            "python -m pip install --no-deps --ignore-installed vdom jp_proxy_widget",
            "python -m pip install --no-deps --ignore-installed .",
            "echo $CMD",
            "$CMD"
        ],
        "test_commands":[
        ],
        "test_imports":[
            "mountainlab_pytools",
            "mountainlab_pytools.mlproc",
            "mountainlab_pytools.mdaio",
            "mountainlab_pytools.processormanager",
            "vdom",
            "jp_proxy_widget"
        ],
        "requirements":[
            "mountainlab",
            "python",
            "pip",
            "requests",
            "numpy",
            "numpydoc",
            "ipython",
            "ipywidgets>=7.0.0",
            "jsonschema"
        ]
    }
)
