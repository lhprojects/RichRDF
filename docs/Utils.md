
# Utils
## `richrdf.include`

After installation, you can run:

```bash
python -m richrdf.include
```

to display the C++ include path.

If you haven't installed the package, you can achieve the same result by running:

```bash
python richrdf/include.py
```

---

## `richrdf.experimental.generate_cpp_config_json`

VSCode is a great editor with excellent IntelliSense support, but it requires a JSON configuration file to work properly with C++.

We provide a small utility to generate this file.

After installation, run:

```bash
python -m richrdf.experimental.generate_cpp_config_json <cvumsversion>
```

This will generate the `.vscode/c_cpp_properties.json` file.  
If the file doesn't take effect, try moving it to the root of your workspace.

A valid `<cvumsversion>` might look like:

```
2024-10-03/x86_64-almalinux9-gcc14.2.0-opt
```

If you haven’t installed the package, you can run the script directly:

```bash
python richrdf/experimental/generate_cpp_config_json.py <cvumsversion>
```
