import shutil
from invoke import task

# When a fn is marked as task, 
# context is injected by invoke and hence context.run() executes shell commands

# Check if pip is available on PATH, otherwise use `python -m pip`
_pip = "pip" if shutil.which("pip") else "python -m pip"

@task
def build(context):
    """Builds a distributable .whl into build/dist/"""
    shutil.rmtree("build/dist", ignore_errors=True)
    context.run(f"{_pip} wheel --no-deps . --wheel-dir build/dist/")
    shutil.rmtree("build/lib", ignore_errors=True)
    print("Library built -> build/dist/")


@task
def test_unit(context):
    """Run unit tests."""
    html = "--html=build/report.html --self-contained-html"
    context.run(f"pytest test/unit-tests -v {html}")


@task
def test_integration(context):
    """Run integration tests."""
    html = "--html=build/report.html --self-contained-html"
    context.run(f"pytest test/integration-tests -v {html}")


@task
def test(context):
    """Run all tests (unit + integration)"""
    html = "--html=build/report.html --self-contained-html"
    context.run(f"pytest test/unit-tests test/integration-tests -v {html}")


@task
def clean(context):
    """Remove build output."""
    shutil.rmtree("build", ignore_errors=True)
    print("Cleaned build/")
