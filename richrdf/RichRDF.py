from types import MethodType
import numpy as np
from .ReadEvent import _ReadEvent, init_Metadata, PODIO_Metadata
from .Evaluate import _Evaluate, init_EvaluateInfo, \
        call_handler, get_callsite_info 
from .LazyAsNumpy import _LazyAsNumpy

class CallableProxy:
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
    
    def __init__(self, backend, context_holder = None):
        self._backend = backend
        if context_holder is not None:
            if hasattr(context_holder, "_eval_context"):
                self._eval_context = context_holder._eval_context

            if hasattr(context_holder, "_podio_metadata"):
                self._podio_metadata = context_holder._podio_metadata

    def getBackend(self):
        return self._backend
    
    def getMetadata(self) -> (PODIO_Metadata|None):
        if hasattr(self, "_podio_metadata"):
            return self._podio_metadata
        else:
            return None
    
    # Lazy action
    def Aggregate(self, *kargs, **kwargs):
        handler = self._backend.Aggregate(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Book(self, *kargs, **kwargs):
        handler = self._backend.Book(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Cache(self, *kargs, **kwargs):
        handler = self._backend.Cache(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Count(self, *kargs, **kwargs):
        handler = self._backend.Count(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Display(self, *kargs, **kwargs):
        handler = self._backend.Display(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Fill(self, *kargs, **kwargs):
        handler = self._backend.Fill(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Graph(self, *kargs, **kwargs):
        handler = self._backend.Graph(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def GraphAsymmErrors(self, *kargs, **kwargs):
        handler = self._backend.GraphAsmmErrors(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    
    def Histo1D(self, *kargs, **kwargs):
        handler = self._backend.Histo1D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Histo2D(self, *kargs, **kwargs):
        handler = self._backend.Histo2D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Histo3D(self, *kargs, **kwargs):
        handler = self._backend.Histo3D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def HistoND(self, *kargs, **kwargs):
        handler = self._backend.HistoND(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Max(self, *kargs, **kwargs):
        handler = self._backend.Max(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())   
    
    def Mean(self, *kargs, **kwargs):
        handler = self._backend.Mean(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Min(self, *kargs, **kwargs):
        handler = self._backend.Min(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Profile1D(self, *kargs, **kwargs):
        handler = self._backend.Profile1D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Profile2D(self, *kargs, **kwargs):
        handler = self._backend.Profile2D(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Reduce(self, *kargs, **kwargs):
        handler = self._backend.Reduce(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Report(self, *kargs, **kwargs):
        handler = self._backend.Report(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    def Stats(self, *kargs, **kwargs):
        handler = self._backend.Stats(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def StdDev(self, *kargs, **kwargs):
        handler = self._backend.StdDev(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())
    
    def Sum(self, *kargs, **kwargs):
        handler = self._backend.Sum(* kargs, **kwargs)
        return call_handler(self, handler, get_callsite_info())

    @property
    def Take(self):
        callsite_info = get_callsite_info()
        proxied = self._backend.Take
        def post(handler):
            return call_handler(self, handler, callsite_info)
        return TemplateProxyProxy(proxied, post)
     
    def AsNumpy(self, *kargs, **kwargs):
        return _LazyAsNumpy(self._backend, *kargs, **kwargs).GetValue()
    
    # added by me
    def AsNumpy_(self, *kargs, **kwargs):
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
        df = self._backend.Alias(*kargs, **kwargs)
        return RRDF(df, self)
    
    def Define(self, *kargs, **kwargs):
        df = self._backend.Define(*kargs, **kwargs)
        return RRDF(df, self)
    
    def DefinePerSample(self, *kargs, **kwargs):
        df = self._backend.DefinePerSample(*kargs, **kwargs)
        return RRDF(df, self)
    
    def DefineSlot(self, *kargs, **kwargs):
        df = self._backend.DefineSlot(*kargs, **kwargs)
        return RRDF(df, self)
    
    def Filter(self, *kargs, **kwargs):
        df = self._backend.Filter(*kargs, **kwargs)
        return RRDF(df, self)
    
    def Range(self, *kargs, **kwargs):
        df = self._backend.Range(*kargs, **kwargs)
        return RRDF(df, self)
    
    def Redefine(self, *kargs, **kwargs):
        df = self._backend.Redefine(*kargs, **kwargs)
        return RRDF(df, self)
    
    def RedefineSlot(self, *kargs, **kwargs):
        df = self._backend.RedefineSlot(*kargs, **kwargs)
        return RRDF(df, self)
    
    def RedefinePerSample(self, *kargs, **kwargs):
        df = self._backend.RedefinePerSample(*kargs, **kwargs)
        return RRDF(df, self)

    def Vary(self, *kargs, **kwargs):
        df = self._backend.Vary(*kargs, **kwargs)
        return RRDF(df, self)



    def ReadEvent(self, eventName: str, collections: list = None, 
                  printGeneratedCode:bool = False,
                  throwExceptionOnRefCollIDNotFound: bool = False):
        df = self._backend
        df = _ReadEvent(df, self._podio_metadata, eventName=eventName, 
                        collections=collections, printGeneratedCode=printGeneratedCode,
                        throwExceptionOnRefCollIDNotFound=throwExceptionOnRefCollIDNotFound)
        return RRDF(df, self)
    
    def Extract(self, varible, members):
        df = self._backend
        for mem in members:
            df = df.Define(varible + "_" + mem, varible + "." + mem)
        return RRDF(df, self)

    def Exposure(self, varible, members):
        df = self._backend
        for mem in members:
            df = df.Define(mem, varible + "." + mem)
        return RRDF(df, self)
    



    def Evaluate(self, *kargs, **kwargs):
        return _Evaluate(self, *kargs, **kwargs)
    


    def printTree(self, indent=0):
        print("".join([" "]*indent), end="")
        print("this is RDF")
        if isinstance(self._backend, RRDF):
            return self._backend.PrintTree(indent+4)
        else:
            print("".join([" "]*(indent+4)), end="")
            print("this is RDataFrame")

    
def RichRDF(*kargs, readMetadata: bool = True, RDataFrame=None, **kwargs):

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
            print(f"Error reading metadata: {e}")
            print(f"But we continue")

    return df



