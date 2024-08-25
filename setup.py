# setup.py

from setuptools import setup, find_packages

setup(
    name='pyenv_size_analyzer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pip',  # Required for pip freeze and pip show
    ],
    entry_points={
        'console_scripts': [
            'pyenv-size-analyze=pyenv_size_analyzer.main:generate_report',
        ],
    },
    description="A tool to analyze the size of installed Python packages in a virtual environment.",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/pyenv_size_analyzer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)

