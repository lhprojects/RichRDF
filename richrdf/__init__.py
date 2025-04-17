from .FlattenNpArray import  FlattenNpArray
from .RichRDF import RichRDF
def get_include_path():
    import os
    return os.path.join(os.path.dirname(__file__), "cpp_include")

__all__ = ["include", "experimental"]  # Only expose these models
