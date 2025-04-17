from .Evaluate import _Evaluate, _DeferredValue

class DotDict(dict):
    """A dictionary that allows dot notation access to its keys."""
    def __getattr__(self, name):
        return self[name]
    

def _LazyAsNumpy(df, columns=None, exclude=None):
    try:
        import numpy
    except ImportError:
        raise ImportError("Failed to import numpy during call of RDataFrame.AsNumpy.")

    if columns is None:
        columns = list(df.GetColumnNames())

    if exclude:
        columns = [col for col in columns if col not in exclude]

    result_proxies = {}
    for column in columns:
        column_type = df.GetColumnType(column)
        result_proxies[column] = df.Take[column_type](column)

    class ndarray(numpy.ndarray):
        def __new__(cls, numpy_array, result_ptr):
            obj = numpy.asarray(numpy_array).view(cls)
            obj.result_ptr = result_ptr  # hold reference to prevent memory release
            obj.__class__.__name__ = "numpy.array"  # for clean repr
            return obj

        def __array_finalize__(self, obj):
            if obj is None:
                return
            self.result_ptr = getattr(obj, "result_ptr", None)

        

    class LazyAsNumpyHandler:
        def __init__(self, result_proxies):
            self._result_proxies = result_proxies
            
        def GetValue(self):
            result = DotDict()
            for key, proxy in self._result_proxies.items():
                cpp_vec = proxy.GetValue()
                if hasattr(cpp_vec, "__array_interface__"):
                    array = numpy.array(cpp_vec)
                else:
                    array = numpy.empty(len(cpp_vec), dtype=object)
                    for i, x in enumerate(cpp_vec):
                        array[i] = x
                result[key] = ndarray(array, proxy)  # wrap with memory-safe ndarray
            return result

    return LazyAsNumpyHandler(result_proxies)
