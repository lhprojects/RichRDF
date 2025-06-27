from .FlattenNpArray import  FlattenNpArray
from .RichRDF import RichRDF
from .include import get_include_path


def get_dependent_collection_names(filename, colls, printOnEachIter=False):
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

__all__ = ["include", "experimental"]  # Only expose these models
