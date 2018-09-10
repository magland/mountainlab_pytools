#!/bin/bash

set -e

conda build -c conda-forge -c flatiron devel/conda.recipe
