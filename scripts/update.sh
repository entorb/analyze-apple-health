#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

# exit upon error
set -e

# remove all dependencies
uv remove defusedxml numpy pandas
uv remove --dev pytest pytest-cov ruff

uv lock --upgrade
uv sync --upgrade

# to update uv on macos:
# brew update && brew upgrade uv

uv python upgrade

# re-add all dependencies
uv add defusedxml numpy pandas
uv add --dev pytest pytest-cov ruff

uv lock --upgrade
uv sync --upgrade

# ruff
uv run ruff format
uv run ruff check --fix

# pre-commit
prek autoupdate
prek run --all-files

echo DONE
