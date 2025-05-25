from setuptools import setup, find_packages

setup(
    name="conch-sage",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'conch-sage=chatcli.main:main',
        ]
    },
    include_package_data=True,
    python_requires=">=3.8",
)