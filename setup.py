from setuptools import setup, find_packages

setup(
    name="drawscape",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'drawscape=drawscape.main:main',
        ],
    },
)