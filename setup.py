from setuptools import setup, find_packages

setup(
    name="teeny",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "teeny = teeny.__main__:main",
        ],
    },
    python_requires=">=3.8",
)
