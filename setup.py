#!/usr/bin/env python

from distutils.core import setup


application_dependencies = [
    'flask',
    'flask-sqlalchemy',
    'psycopg2',
    'flask-migrate',
]
prod_dependencies = []
test_dependencies = [
    'tox',
    'pytest-cov',
    'pytest-env',
    'pytest-flask-sqlalchemy',
]
lint_dependencies = [
    'flake8',
    'flake8-docstrings',
    'black',
]
docs_dependencies = []
dev_dependencies = test_dependencies + lint_dependencies + docs_dependencies + [
    'python-dotenv',
    'ipdb',
]


setup(
    name='ledger',
    version='0.1',
    description='A simple ledger as a service.',
    author='Mike Wooster',
    author_email='',
    url='',
    packages=[
        'ledger',
    ],
    install_requires=application_dependencies,
    extras_require={
        'production': prod_dependencies,
        'test': test_dependencies,
        'lint': lint_dependencies,
        'docs': dev_dependencies,
        'dev': dev_dependencies,
    },
    include_package_data=True,
    zip_safe=False,
)
