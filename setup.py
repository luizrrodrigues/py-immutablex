'''
    Setup file for the py-immutablex package.
'''
from setuptools import setup, find_packages

setup(
    name="py-immutablex",
    version="0.1.0",
    description="A Python library for interacting with the Immutable X API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Luiz Ricardo Rodrigues",
    author_email="trinix@luizrrodrigues.com.br",
    url="https://github.com/luizrrodrigues/py-immutablex",
    packages=find_packages(where="."),
    install_requires=[
        "bip32==4.0",
        "cairo-lang==0.13.3",
    ],
    extras_require={
        "test": ['pytest==8.3.4', 'requests-mock-1.12.1']
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="immutablex blockchain starknet ethereum python",
    license="MIT",
    include_package_data=True,
)
