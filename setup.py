from setuptools import setup, find_packages

setup(
    name="premiumFinance",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "scipy", "requests", "matplotlib", "openpyxl"],
    extras_require={"dev": ["pylint", "black"]},
)