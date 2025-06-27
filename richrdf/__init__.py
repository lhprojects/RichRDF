from .FlattenNpArray import  FlattenNpArray
from .RichRDF import RichRDF
from .RichRDF import RRDF

def get_include_path():
    """
    Return the absolute path to the local C++ header include directory.

    This function is useful for setup scripts or bindings that need access
    to the `cpp_include` folder located alongside this file.

    Returns
    -------
    str
        Absolute path to the `cpp_include` directory.
    """
    import os
    return os.path.join(os.path.dirname(__file__), "cpp_include")

def get_dependent_collection_names(filename, colls, printOnEachIter=False):
    """
    Dynamically detect and append missing collection names required for event reading.

    This function attempts to read the specified event collections from the input file,
    and if a referenced collection is missing, it parses the exception and adds the
    missing collection name to the list, retrying until success or exhaustion.

    Parameters
    ----------
    filename : str
        Path to the event file.
    colls : list of str
        List of collection names to start with; more may be appended.
    printOnEachIter : bool, optional
        Whether to print collection status after each attempt.

    Returns
    -------
    list of str
        Complete list of required collections after dynamic resolution.
    """

    for iter in range(10000):  # try reading the event multiple times to catch all missing collections
        try:
            df = RichRDF("events", filename)
            df = df.ReadEvent("evt", colls, throwExceptionOnRefCollIDNotFound=True)
            df = df.Define("index", "evt.index")
            df.Sum("index").GetValue()  # force reading the event
            break
        except Exception as e:
            full_exception_name = f"{e.__class__.__module__}.{e.__class__.__name__}"
            if full_exception_name != "cppyy.gbl.ana.exception_t":
                raise

            what = e.what()
            import re
            match = re.search(r"Collection (\w+) \(\d+\) not found", what)
            if match:
                missing_collection = match.group(1)
                colls.append(missing_collection)
            else:
                raise  # rethrow if it's not a collection-not-found error
        if printOnEachIter:
            print("iter%2d: "%iter, colls)

    return colls

