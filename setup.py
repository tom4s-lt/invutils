"""Setup configuration for invutils package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from package
version = {}
with open("invutils/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="invutils",
    version=version["__version__"],
    description="Tools for cryptocurrency price data retrieval",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tom4s",
    author_email="tom4s.rr@gmail.com",
    url="https://github.com/xtom4s/invutils",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="cryptocurrency bitcoin ethereum price api coingecko defillama",
    project_urls={
        "Source": "https://github.com/xtom4s/invutils",
        "Changelog": "https://github.com/xtom4s/invutils/blob/main/CHANGELOG.md",
    },
)