import os
from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "numpy",
    "pandas",
    "requests",
    # Pin streamlit because 0.52.0 contains a pop-up bug.
    "streamlit==0.51.0",
    "tensorflow",
    "transformers",
]

extra_requirements = {
    "dev": [
        "black",
        "bump2version",
        "coverage",
        "twine",
        "pre-commit",
        "pylint",
        "pytest",
    ]
}

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest", "pytest-cov", "pytest-nunit"]

BUILD_ID = os.environ.get("BUILD_BUILDID", "0")

setup(
    author="Rens Dimmendaal & Henk Griffioen",
    author_email="rensdimmendaal@godatadriven.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
    description="Generate text",
    install_requires=requirements,
    extras_require=extra_requirements,
    long_description=readme,
    include_package_data=True,
    keywords="rhyme",
    name="rhyme_with_ai",
    packages=find_packages(include=["src"]),
    package_dir={"": "src"},
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    version="0.1" + "." + BUILD_ID,
    zip_safe=False,
)
