from setuptools import find_packages, setup

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name='mlgym',
    version='0.0.63',
    author='Max Luebbering',
    description="MLgym, a python framework for distributeda and reproducible machine learning model training in research.",
    long_description="long_description",
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
        "scikit-learn",
        "python-socketio",
        "fastapi",
        "uvicorn",
        "requests",
        "python-multipart",
        "flask",
        "Flask-SocketIO",
        "eventlet"
    ],
    python_requires=">=3.7",
    package_dir={'ml_board': 'ml_board'},
    package_data={
        'ml_board': ['frontend/dashboard/build/**/*'],
    },
    scripts=['ml_board/backend/starter_scripts/ml_board', 'ml_board/backend/starter_scripts/ml_board_ws_endpoint', 'ml_board/backend/starter_scripts/ml_board_rest_endpoint'],
    url="https://github.com/mlgym/mlgym"
)
