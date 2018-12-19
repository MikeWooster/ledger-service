import os

from invoke import task, run


PYTHON = run("which python").stdout.strip()
ROOT_DIR = os.path.dirname(__file__)
LOCAL_WORKSPACE = os.path.join(ROOT_DIR, ".devenv")
PROD_DEPS_ENV = os.path.join(LOCAL_WORKSPACE, "frozen-requirements-prod")
PROD_REQUIREMENTS_PATH = os.path.join(ROOT_DIR, "requirements.txt")
EXTRA_INDEX_URL = "https://pypi.fury.io/27gXAcex9eXiMgf3dZeC/growthstreet/"


@task
def requirements(c):
    pip = os.path.join(PROD_DEPS_ENV, "bin/pip")
    c.run(f"virtualenv {PROD_DEPS_ENV} --clear -p {PYTHON}")
    c.run(f"{pip} install --upgrade pip setuptools wheel")
    c.run(f"{pip} install --extra-index-url={EXTRA_INDEX_URL} .[production]")
    c.run(f"{pip} freeze > {PROD_REQUIREMENTS_PATH}")
