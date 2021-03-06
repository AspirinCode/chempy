#!/bin/bash -xeu
PKG_NAME=${1:-${CI_REPO##*/}}
if [[ "$CI_BRANCH" =~ ^v[0-9]+.[0-9]?* ]]; then
    eval export ${PKG_NAME^^}_RELEASE_VERSION=\$CI_BRANCH
    echo ${CI_BRANCH} | tail -c +2 > __conda_version__.txt
fi

git archive -o /tmp/$PKG_NAME.zip HEAD  # test pip installable zip (symlinks break)
python3 -m pip install --user /tmp/$PKG_NAME.zip
python3 setup.py sdist  # test pip installable sdist (checks MANIFEST.in)
(cd dist/; python3 -m pip install --user --force-reinstall --no-deps $PKG_NAME-$(python3 ../setup.py --version).tar.gz)
(cd /; python3 -m pytest --pyargs $PKG_NAME)
python3 -m pip install --user --upgrade --upgrade-strategy only-if-needed .[all]
./scripts/run_tests.sh --cov $PKG_NAME --cov-report html
./scripts/coverage_badge.py htmlcov/ htmlcov/coverage.svg

# Test package without any 3rd party libraries (only python stdlib):
python3 -m virtualenv venv
set +u
(source ./venv/bin/activate; python3 -m pip install pytest; python3 -m pytest $PKG_NAME)

./scripts/render_notebooks.sh
./scripts/generate_docs.sh
(cd examples/; for f in bokeh_*.py; do python3 -m bokeh html $f; done)
