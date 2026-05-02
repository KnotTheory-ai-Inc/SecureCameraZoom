import os
import shutil
from invoke import task

# When a fn is marked as task,
# context is injected by invoke and hence context.run() executes shell commands

# Absolute path to the Implementation/ directory — ensures build output and test
# paths resolve correctly regardless of the working directory inv is called from.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


@task
def build(context):
    """Builds a distributable .whl into build/dist/"""
    import setuptools.build_meta as _meta

    dist_dir = os.path.join(CURRENT_DIR, "build", "dist")
    shutil.rmtree(dist_dir, ignore_errors=True)
    os.makedirs(dist_dir, exist_ok=True)
    # Build wheel in-process via PEP 517
    _meta.build_wheel(wheel_directory=dist_dir)
    shutil.rmtree(os.path.join(CURRENT_DIR, "build", "lib"), ignore_errors=True)
    print(f"Library built -> {dist_dir}")


@task
def test_unit(context):
    """Run unit tests."""
    html = f"--html={CURRENT_DIR}/build/report.html --self-contained-html"
    context.run(f"pytest {CURRENT_DIR}/test/unit-tests -v {html}")


@task
def test_integration(context):
    """Run integration tests."""
    html = f"--html={CURRENT_DIR}/build/report.html --self-contained-html"
    context.run(f"pytest {CURRENT_DIR}/test/integration-tests -v {html}")


@task
def test_sw(context):
    """Run sw (system/workflow) tests."""
    html = f"--html={CURRENT_DIR}/build/report.html --self-contained-html"
    context.run(f"pytest {CURRENT_DIR}/test/sw-tests -v {html}")


@task
def test(context):
    """Run all tests (unit + integration + sw)"""
    html = f"--html={CURRENT_DIR}/build/report.html --self-contained-html"
    context.run(f"pytest {CURRENT_DIR}/test/unit-tests {CURRENT_DIR}/test/integration-tests {CURRENT_DIR}/test/sw-tests -v {html}")


@task
def clean(context):
    """Remove build output."""
    shutil.rmtree(os.path.join(CURRENT_DIR, "build"), ignore_errors=True)
    print("Cleaned build/")
