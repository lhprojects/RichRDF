"""
Generate a `.vscode/c_cpp_properties.json` configuration file for C++ IntelliSense in VSCode.

This utility simplifies setting up Visual Studio Code for C++ development by generating
a `c_cpp_properties.json` file using the specified Key4HEP CVMFS toolchain version.

IntelliSense in VSCode relies on this JSON file to properly locate system headers,
toolchain includes, and C++ standard configuration.

Usage (after package installation):
Run the module from the command line:
 
>>> python -m richrdf.experimental.generate_cpp_config_json <cvmfsversion>


Alternatively, if the package is not installed, you can execute the script directly:
 
>>> python richrdf/experimental/generate_cpp_config_json.py <cvmfsversion>


Parameters
----------
<cvmfsversion> : str
    Key4HEP CVMFS toolchain version. Example:
    `"2024-10-03/x86_64-almalinux9-gcc14.2.0-opt"`

Notes
-----
- If the specified output file already exists, the function skips overwriting.
- If the file doesn't take effect, try moving it manually to the root of your workspace.
"""

import json
import glob
import os
from richrdf.include import get_include_path


def generate_cpp_config_json(cvmfsversion: str, output_path: str):

    base_path = f"/cvmfs/sw.hsf.org/key4hep/releases/{cvmfsversion}"
    
    # Extract toolchain part: e.g., "x86_64-almalinux9-gcc14.2.0-opt"
    toolchain = cvmfsversion.split("/")[-1][:len("x86_64-al")]
    
    # Search for the g++ compiler path
    compiler_glob = glob.glob(f"/cvmfs/sw.hsf.org/contrib/{toolchain}*/gcc/*/bin/g++")
    compiler_path = compiler_glob[0] if compiler_glob else "/usr/bin/g++"

    include_patterns = [
        "/usr/include",
        "/usr/include/c++/11",
        f"{base_path}/edm4hep/*/include",
        f"{base_path}/podio/*/include",
        f"{base_path}/root/*/include/root",
        f"{base_path}/vdt/*/include",
        f"{get_include_path()}",
    ]

    expanded_include_paths = []
    for pattern in include_patterns:
        matched = glob.glob(pattern)
        expanded_include_paths.extend(matched if matched else [pattern])

    config = {
        "configurations": [
            {
                "name": "Linux",
                "includePath": expanded_include_paths,
                "defines": [],
                "compilerPath": compiler_path,
                "cStandard": "c17",
                "cppStandard": "c++20",
                "intelliSenseMode": "linux-gcc-x64"
            }
        ],
        "version": 4
    }
    print(f"Generated configuration")

    if os.path.exists(output_path):
        print(f"{output_path} already exists. Skipping writing.")
        return
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(config, f, indent=4)

    print(f"Configuration writen to: {output_path}")



if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: <this_script> <cvmfsversion> [<output_path>]")
        print("Example: python -m richrdf.experimental.generate_cpp_config_json 2024-10-03/x86_64-almalinux9-gcc14.2.0-opt .vscode/c_cpp_properties.json")
        print("Example: python richrdf/experimental/generate_cpp_config_json.py 2024-10-03/x86_64-almalinux9-gcc14.2.0-opt .vscode/c_cpp_properties.json")
        sys.exit(1)

    if len(sys.argv) > 2:
        version = sys.argv[1]

    output_path = ".vscode/c_cpp_properties.json"
    if len(sys.argv) > 3:
        output_path = sys.argv[2]

    generate_cpp_config_json(version, output_path)