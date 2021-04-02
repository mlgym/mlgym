from setuptools import find_packages, setup

with open("../README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mlgym',
    version='0.0.27',
    author='Max Luebbering, Rajkumar Ramamurthy',
    description="MLgym, a python framework for distributed machine learning model training in research.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        "pytest",
        "pytest-cov",
        "torch",
        "h5py",
        "tqdm",
        "pyyaml",
        "datastack",
        "scipy",
        "dashifyML",
        "scikit-learn"
    ],
    python_requires=">=3.7",
    url="https://github.com/le1nux/mlgym"
)
