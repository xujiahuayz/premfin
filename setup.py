from setuptools import setup, find_packages

setup(
    name="premiumFinance",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "matplotlib"],
    extras_require={"dev": ["pylint", "black"]},
)