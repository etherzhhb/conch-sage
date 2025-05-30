from setuptools import setup, find_packages

setup(
    name="conch-sage",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "faiss-cpu",
        "prompt_toolkit",
        "typer",
        "pyyaml",
        "langchain",
        "langchain-ollama",
        "jinja2",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "sentence-transformers",
            "torch"
        ]
    },
    entry_points={
        'console_scripts': [
            'conch-sage=chatcli.main:main',
        ]
    },
    include_package_data=True,
    python_requires=">=3.8",
)
