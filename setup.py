from setuptools import setup, find_packages

setup(
    name="tester",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "edalize>=0.4.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-click>=1.1.0",
            "black>=23.0.0",  # Added Black as a dev dependency
        ],
    },
    entry_points={
        "console_scripts": [
            "tester=cli:cli",
        ],
    },
    python_requires=">=3.6",
    description="A flexible Python tool for automating UVM testbench execution",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/tester",
)
