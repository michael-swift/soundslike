from setuptools import setup, find_packages

setup(
    name="soundslike",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "pippi",
        "seaborn",
    ],
    author="Michael Swift",
    author_email="swiftmichael26@gmail.com",
    description="A library for sonifying probability distributions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/michael-swift/soundslike",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
) 