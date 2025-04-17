def get_include_path():
    import os
    return os.path.join(os.path.dirname(__file__), "cpp_include")

if __name__ == "__main__":
    print(get_include_path())