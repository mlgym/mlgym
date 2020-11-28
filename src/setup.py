from setuptools import find_packages, setup


setup(
    name='mlgym',
    version='0.0.1',
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
    python_requires=">=3.7"
)
