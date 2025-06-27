from types import MethodType
import numpy as np
from .ReadEvent import _ReadEvent, init_Metadata, PODIO_Metadata
from .Evaluate import _Evaluate, init_EvaluateInfo, \
        call_handler, get_callsite_info 
from .LazyAsNumpy import _LazyAsNumpy

class CallableProxy:
    """.. sphinx-hide::"""
    def __init__(self, proxied, post):
        self._proxied = proxied
        self.post = post

    def __call__(self, *args, **kwargs):
        result = self._proxied(*args, **kwargs)
        return self.post(result)
    
class TemplateProxyProxy:
    def __init__(self, proxied, post):
        self._proxied = proxied
        self.post = post

    def __getitem__(self, item):
        return CallableProxy(self._proxied[item], self.post)

    
class RRDF:
    """
    A wrapper class around an RDataFrame backend providing a fluent Python interface.

    The `RRDF` class is the core abstraction returned by `RichRDF`. It mimics the ROOT RDataFrame
    interface while adding evaluation context handling and convenient utility methods. Methods such as
    `Define`, `Filter`, `Aggregate`, `Evaluate`, and `AsNumpy` allow chaining and lazy/instant actions.

    This wrapper tracks evaluation context, and metadata.
    when passed a parent RRDF object, enabling rich evaluation features and metadata-aware operations.

    Example:
        >>> df = RichRDF("events.root")
        >>> df = df.Define("x", "x + 1").Filter("x > 5")
        >>> df.Display("x")
    """
    
    def __init__(self, backend, context_holder = None):
        self._backend = backend
        if context_holder is not None:
            if hasattr(context_holder, "_eval_context"):
                self._eval_context = context_holder._eval_context

            if hasattr(context_holder, "_podio_metadata"):
                self._podio_metadata = context_holder._podio_metadata

    def getBackend(self):
        """
        Return the underlying backend used by this RRDF instance.

        Returns
        -------
        Any
            The internal backend object (typically an RDataFrame or similar).
        """
        return self._backend
    
    def getMetadata(self) -> (PODIO_Metadata|None):
        """
        Retrieve PODIO metadata if available.

        Returns
        -------
        PODIO_Metadata or None
            The metadata object if present, otherwise None.
        """
        if hasattr(self, "_podio_metadata"):
            return self._podio_metadata
        else:
            return None
    
    # Lazy action
    def Aggregate(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Aggregate(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Book(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Book(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Cache(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Cache(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Count(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Count(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Display(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Display(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Fill(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Fill(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Graph(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Graph(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def GraphAsymmErrors(self, *kargs, **kwargs):
        """ """
        handler = self._backend.GraphAsymmErrors(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    
    def Histo1D(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Histo1D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Histo2D(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Histo2D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Histo3D(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Histo3D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def HistoND(self, *kargs, **kwargs):
        """ """
        handler = self._backend.HistoND(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Max(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Max(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())   
    
    def Mean(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Mean(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Min(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Min(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Profile1D(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Profile1D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Profile2D(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Profile2D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Reduce(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Reduce(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Report(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Report(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Stats(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Stats(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def StdDev(self, *kargs, **kwargs):
        """ """
        handler = self._backend.StdDev(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Sum(self, *kargs, **kwargs):
        """ """
        handler = self._backend.Sum(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    @property
    def Take(self):
        """ """
        callsite_info = get_callsite_info()
        proxied = self._backend.Take
        def post(handler):
            return call_handler(self, handler, callsite_info)
        return TemplateProxyProxy(proxied, post)
     
    def AsNumpy(self, *kargs, **kwargs):
        """
        This method behaves similarly to `AsNumpy()` in ROOT's RDataFrame.
        It triggers immediate evaluation and returns the result as a NumPy-compatible
        structure (typically a dict of arrays).
        """
        return _LazyAsNumpy(self._backend, *kargs, **kwargs).GetValue()
    
    def AsNumpy_(self, *kargs, **kwargs):
        """
        Unlike `AsNumpy()`, this method does not immediately evaluate the result.
        """
        handler = _LazyAsNumpy(self._backend, *kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())   
    

    # Instant action
    def __getattr__(self, name):
        instant_action = [
            "Foreach",
            "ForeachSlot",
            "Snapshot",
        ]

        Queries = [
            "Describe",
            "GetColumnNames",
            "GetColumnType",
            "GetColumnTypeNamesList",
            "GetDefinedColumnNames",
            "GetFilterNames",
            "GetNRuns",
            "GetNSlots",
            "SaveGraph",
        ]
        if name in Queries:
            return getattr(self._backend, name)            
        if name in instant_action:
            return getattr(self._backend, name)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def Alias(self, *kargs, **kwargs):
        """  """
        df = self._backend.Alias(*kargs, **kwargs)
        return RRDF(df, self)
    
    def Define(self, *kargs, **kwargs):
        """  """
        df = self._backend.Define(*kargs, **kwargs)
        return RRDF(df, self)
    
    def DefinePerSample(self, *kargs, **kwargs):
        """  """
        df = self._backend.DefinePerSample(*kargs, **kwargs)
        return RRDF(df, self)
    
    def DefineSlot(self, *kargs, **kwargs):
        """  """
        df = self._backend.DefineSlot(*kargs, **kwargs)
        return RRDF(df, self)
    
    def Filter(self, *kargs, **kwargs):
        """  """
        df = self._backend.Filter(*kargs, **kwargs)
        return RRDF(df, self)
    
    def Range(self, *kargs, **kwargs):
        """  """
        df = self._backend.Range(*kargs, **kwargs)
        return RRDF(df, self)
    
    def Redefine(self, *kargs, **kwargs):
        """  """
        df = self._backend.Redefine(*kargs, **kwargs)
        return RRDF(df, self)
    
    def RedefineSlot(self, *kargs, **kwargs):
        """  """
        df = self._backend.RedefineSlot(*kargs, **kwargs)
        return RRDF(df, self)
    
    def RedefinePerSample(self, *kargs, **kwargs):
        """  """
        df = self._backend.RedefinePerSample(*kargs, **kwargs)
        return RRDF(df, self)

    def Vary(self, *kargs, **kwargs):
        """  """
        df = self._backend.Vary(*kargs, **kwargs)
        return RRDF(df, self)



    def ReadEvent(self, eventName: str, collections: list = None, 
                  printGeneratedCode:bool = False,
                  throwExceptionOnRefCollIDNotFound: bool = False):
        """       
        Read an event from the underlying data source, extracting specified collections.

        This will define an `"event"` column in the DataFrame that includes the requested collections.

        Parameters
        ----------
        eventName : str
            The name of the event column to define in the DataFrame.
        collections : list of str or None, optional
            List of collection names to read, e.g., `["MCParticles", "PandoraPFOs"]`.
            If None, all collections will be loaded.
        printGeneratedCode : bool, optional
            Whether to print the C++ code generated by this operation.
        throwExceptionOnRefCollIDNotFound : bool, optional
            If True, raises an exception when a collection refers to another that has not been loaded.

        Returns
        -------
        RRDF
            A new RRDF with the specified event column registered.

        Examples
        --------
        >>> df = df.ReadEvent("event", ["MCParticles", "PandoraPFOs"])
        >>> df = df.ReadEvent("event", None)
        >>> df = df.ReadEvent("event")  # equivalent to loading all collections
        >>> df = df.ReadEvent("event", ["MCParticles", "PandoraPFOs"], throwExceptionOnRefCollIDNotFound=True)

        Notes
        -----
        Elements in `PandoraPFOs` are typically of type `edm4hep::ReconstructedParticle`, which has four 
        associated relations: `clusters`, `tracks`, `particles`, and `vertex`.

        By default, `ReadEvent` does **not** load these related collections unless you explicitly specify 
        them. If you omit them, you can still call `auto clusters = rec.getClusters();`, but this returns 
        an array of **empty clusters** (not an empty array). As a result, `rec.getClusters()[...].isValid()` 
        returns `False`. If you then try `rec.getClusters()[...].getEnergy()`, your program will almost 
        certainly crash.

        This is because `podio` is designed **not to throw exceptions**, even for invalid access.

        Due to limitations in `RDataFrame`, related collections like `clusters` cannot be added automatically. 
        You must specify them manually. Enabling `throwExceptionOnRefCollIDNotFound` helps identify such 
        missing references:

        >>> df = df.ReadEvent("event", ["MCParticles", "PandoraPFOs"], throwExceptionOnRefCollIDNotFound=True)

        This causes the program to throw **at runtime** (when looping over events), not during registration, 
        because collection dependencies require actual data inspection and are not detectable from metadata alone.

        If `collections` is set to `None`, all collections will be read:
        
        >>> df = df.ReadEvent("event", None)

        """
        df = self._backend
        df = _ReadEvent(df, self._podio_metadata, eventName=eventName, 
                        collections=collections, printGeneratedCode=printGeneratedCode,
                        throwExceptionOnRefCollIDNotFound=throwExceptionOnRefCollIDNotFound)
        return RRDF(df, self)
    
    def Extract(self, varible, members):
        """
        This method defines new columns in the DataFrame by accessing individual members
        of a compound object (e.g., a struct or class with attributes).

        Parameters
        ----------
        varible : str
            The name of the compound variable in the DataFrame (e.g., a collection element like `hit`).
        members : list of str
            The list of member field names to extract (e.g., `["x", "y", "z"]`).

        Returns
        -------
        RRDF
            A new RRDF instance with the member fields defined as separate columns.

        Examples
        --------
        >>> df = df.Extract("hit", ["x", "y", "z"])
        # Defines columns: hit_x, hit_y, hit_z as hit.x, hit.y, hit.z respectively.
        """
         
        df = self._backend
        for mem in members:
            df = df.Define(varible + "_" + mem, varible + "." + mem)
        return RRDF(df, self)

    def Exposure(self, varible, members):
        """
        Expose member fields of a compound variable as top-level DataFrame columns.

        This method defines new columns using the member fields of a compound variable.
        Unlike `Extract`, which uses `varible_member` naming, this exposes members directly
        as columns named after the member itself.

        Parameters
        ----------
        varible : str
            The name of the compound variable (e.g., `hit`).
        members : list of str
            The list of member field names to expose (e.g., `["x", "y", "z"]`).

        Returns
        -------
        RRDF
            A new RRDF instance with the member fields exposed as top-level columns.

        Examples
        --------
        >>> df = df.Exposure("hit", ["x", "y", "z"])
        # Defines columns: x, y, z (instead of hit_x, hit_y, hit_z)
        """ 
        df = self._backend
        for mem in members:
            df = df.Define(mem, varible + "." + mem)
        return RRDF(df, self)
    



    def Evaluate(self, *kargs, **kwargs):
        return _Evaluate(self, *kargs, **kwargs)
    


    def printTree(self, indent=0):
        """
        Print the structure of this RRDF instance, including backend nesting.
        This is a diagnostic method for visualizing the composition of RRDF wrappers.

        Parameters
        ----------
        indent : int, optional
            The number of spaces to indent the current level (used for recursion).

        Returns
        -------
        None
            This method prints directly to stdout.

        Examples
        --------
        >>> df.printTree()
        this is RDF
            this is RDataFrame
        """
        print("".join([" "]*indent), end="")
        print("this is RDF")
        if isinstance(self._backend, RRDF):
            return self._backend.PrintTree(indent+4)
        else:
            print("".join([" "]*(indent+4)), end="")
            print("this is RDataFrame")

    
def RichRDF(*kargs, readMetadata: bool = True, RDataFrame=None, **kwargs):
    """
    Create an enriched RRDF (RDataFrame wrapper) with optional metadata support.

    This function wraps a ROOT `RDataFrame` and optionally attaches evaluation context 
    and PODIO metadata. It provides enhanced features via the `RRDF` interface.

    Parameters
    ----------
    *kargs : tuple
        Positional arguments forwarded to the ROOT `RDataFrame` constructor.
    readMetadata : bool, optional
        Whether to try reading and attaching PODIO metadata (default: True).
    RDataFrame : callable, optional
        A custom RDataFrame constructor. If None, uses `ROOT.RDataFrame`.
    **kwargs : dict
        Additional keyword arguments forwarded to the RDataFrame constructor and metadata reader.

    Returns
    -------
    RRDF
        A wrapped ROOT RDataFrame instance with evaluation and optional metadata context.

    Notes
    -----
    - If metadata reading fails, a traceback is printed but execution continues.
    - Evaluation context is always initialized.
    """

    if RDataFrame is None:
        import ROOT
        RDataFrame = ROOT.RDataFrame

    df = RDataFrame(*kargs, **kwargs)

    df = RRDF(df, None)

    df._eval_context = init_EvaluateInfo()
    if readMetadata:
        try:
            metadata = init_Metadata(*kargs, **kwargs)
            df._podio_metadata = metadata
        except Exception as e:
            import traceback
            traceback.print_exc() 
            print(f"Error reading metadata: {e}")
            print(f"But we continue")

    return df



