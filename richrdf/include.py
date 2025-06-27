"""
richrdf.include
===============

Display the C++ include path used by the richrdf package.

This module provides a command-line interface to print the internal C++ include
directory used by richrdf. It is primarily useful for configuring external tools
(such as compilers or editors) that require the include path for building or
intellisense support.

Usage
-----

After installation, you can run:

    python -m richrdf.include

If you haven't installed the package, you can achieve the same result by running:

    python richrdf/include.py
"""

from . import get_include_path

if __name__ == "__main__":
    print(get_include_path())