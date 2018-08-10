import setuptools

setuptools.setup(
    name="mountainlab_pytools",
    version="0.6.2",
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
            "python -m pip install vdom jp_proxy_widget",
            "python -m pip install --no-deps --ignore-installed .",
            "CMD=\"ln -sf $SP_DIR/"+pkg_name+" `CONDA_PREFIX=$PREFIX ml-config package_directory`/"+pkg_name+"\"",
            "echo $CMD",
            "$CMD"
        ],
        "test_commands":[
        ],
        "test_imports":[
            "mountainlab_pytools",
            "mountainlab_pytools.mlproc",
            "mountainlab_pytools.mdaio",
            "mountainlab_pytools.processormanager"
        ],
        "requirements":[
            "python",
            "pip",
            "requests",
            "numpy",
            "numpydoc",
            "ipython",
            "ipywidgets"
        ]
    }
)
