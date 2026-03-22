from setuptools import setup, find_packages

setup(
    name="money-manage",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pdfplumber>=0.9.0",
        "PyMuPDF>=1.23.0",
        "openpyxl>=3.1.0",
        "tabulate>=0.9.0",
    ],
    entry_points={"console_scripts": ["finance-cli=cli.main:main"]},
)
