import setuptools

with open("README.mb", "r", encoding="utf-8") as handle:
    long_description = handle.read()

setuptools.setup(
    name="pipeline",
    version="2.0.0",
    description="A program meant to manage production files.",
    long_description=long_description,
    license="MIT",
    author="lennybldl",
    packages=setuptools.find_packages(),
    install_requires=["python_core"],
)
