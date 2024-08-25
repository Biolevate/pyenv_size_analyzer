# pyenv-size-analyzer

`pyenv-size-analyzer` is a Python tool designed to analyze the size distribution of installed packages in a Python environment. It provides insights into the space usage of packages, including dependencies, allowing developers to optimize and manage their Python environments more efficiently.

## Installation

To install `pyenv-size-analyzer`, you need to have Python 3.10+.

You can install PyEnv Size Analyzer using pip:

```bash
pip install git+ssh://git@github.com/Biolevate/pyenv_size_analyzer.git
```

or using Poetry:

```bash
poetry add poetry add git+ssh://git@github.com/Biolevate/pyenv_size_analyzer.git
```

## Usage

After installation, you can use the tool directly from the command line:

```bash
pyenv-size-analyze
```
or using Poetry :

```bash
poetry run pyenv-size-analyze
```

Output
The tool provides three main sections in its output:

- **Package Sizes**: Lists all packages and their sizes.
- **Root Package Total Impact**: Shows the total impact of root packages, including their dependencies.
- **Unmatched Directories**: Lists directories that could not be matched to any known package.
- **Summary**: Provides a summary of the total, matched, and unmatched sizes.

#### Example Output

```plaintext
    Package Sizes:
    Name                           Size            Percentage
    -------------------------------------------------------
    numpy                          50.00 MB        20.00%
    pandas                         40.00 MB        16.00%
    scipy                          35.00 MB        14.00%
    Others                         75.00 MB        30.00%

    Root Package Total Impact (including dependencies) -  WARNING it might overlap with other packages:
    Name                           Size            Percentage
    -------------------------------------------------------
    numpy                          70.00 MB        28.00%
    pandas                         60.00 MB        24.00%
    scipy                          50.00 MB        20.00%
    Others                         45.00 MB        18.00%

    Unmatched Directories:
    Name                           Size            Percentage
    -------------------------------------------------------
    _others                        10.00 MB        4.00%

    Summary:
    Total Size:                    250.00 MB
    Matched Size:                  240.00 MB (96.00%)
    Unmatched Size:                10.00 MB (4.00%)
```


Customization
You can customize the output by modifying the exclude_packages and top_n parameters:

exclude_packages: A list of package names to exclude from the analysis.
top_n: The number of top packages to display in each section.


### License

This project is licensed under the MIT License.


