import linecache

def load_source(filename, lineno, context=2):
    # Try standard Python source
    if filename.startswith('/tmp/ipykernel'):
        try:
            from IPython import get_ipython  # lazy import
            ip = get_ipython()
            if not ip:
                return "Not running in IPython/Jupyter."

            cell_id = None
            code_lines = []

            for i, code in enumerate(reversed(ip.user_ns.get('In', []))):
                lines = code.splitlines()
                if 0 < lineno <= len(lines):
                    cell_id = len(ip.user_ns['In']) - i - 1
                    code_lines = lines
                    break

            if cell_id is None:
                return "[DEBUG] Cell not found."

            lines_out = [f"Cell In[{cell_id}], line {lineno}"]

            start = max(lineno - context, 1)
            end = lineno + context

            for i in range(start, end + 1):
                if i > len(code_lines): break
                prefix = "--->" if i == lineno else "    "
                lines_out.append(f"{prefix} {i:>3} {code_lines[i - 1]}")

            return "\n".join(lines_out)

        except Exception as e:
            return f"[DEBUG] Error while formatting trace: {e}"
    else:
        source = linecache.getline(filename, lineno)
        return source


class _DeferredValue:
    """
    A deferred-evaluation wrapper that raises an error if you attempt to use
    *any* operator, special method, or container protocol method
    before explicitly calling GetValue().
    """

    def __init__(self, func, callsite_info=None):
        """
        :param func: A callable that, when called, returns the "real" value.
        """
        self._func = func
        self._evaluated = False
        self._value = None
        self.callsite_info = callsite_info

    def _evaluate(self):
        """Force creation of the underlying value if not already done."""
        if not self._evaluated:
            try:
                self._value = self._func()
            except Exception as e:
                if self.callsite_info:
                    src = load_source(self.callsite_info['filename'], self.callsite_info['lineno'])
                    error = f"Error evaluating deferred value at call site:\n" + \
                    f"{self.callsite_info['filename']}:{self.callsite_info['lineno']}:0:\n{src}"
                else:
                    error = "Error evaluating deferred value."
                raise Exception(error)

            self._evaluated = True

    def __getattr__(self, name):
        """
        Called if 'name' is not found as an attribute on self.
        Forwards the call to the underlying value, raising an error
        if it's not yet evaluated.
        """
        if not self._evaluated:
            raise Exception("Cannot use methods or attributes before evaluation.")
        return getattr(self._value, name)


    def GetValue(self):
        """
        Manually force evaluation and return the real underlying value.
        """
        self._evaluate()
        return self._value

    def __repr__(self):
        """
        If not evaluated, return a custom placeholder representation.
        Otherwise, return the normal repr of the underlying value.
        """
        if not self._evaluated:
            return "<DeferredValue: not yet evaluated>"
        return repr(self._value)

    #
    # ========= ARITHMETIC / BINARY OPERATORS =========
    #
    def __add__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __add__ before _DeferredValue is evaluated.")
        return self._value + other

    def __radd__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __radd__ before _DeferredValue is evaluated.")
        return other + self._value

    def __sub__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __sub__ before _DeferredValue is evaluated.")
        return self._value - other

    def __rsub__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rsub__ before _DeferredValue is evaluated.")
        return other - self._value

    def __mul__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __mul__ before _DeferredValue is evaluated.")
        return self._value * other

    def __rmul__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rmul__ before _DeferredValue is evaluated.")
        return other * self._value

    def __truediv__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __truediv__ before _DeferredValue is evaluated.")
        return self._value / other

    def __rtruediv__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rtruediv__ before _DeferredValue is evaluated.")
        return other / self._value

    def __floordiv__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __floordiv__ before _DeferredValue is evaluated.")
        return self._value // other

    def __rfloordiv__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rfloordiv__ before _DeferredValue is evaluated.")
        return other // self._value

    def __mod__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __mod__ before _DeferredValue is evaluated.")
        return self._value % other

    def __rmod__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rmod__ before _DeferredValue is evaluated.")
        return other % self._value

    def __divmod__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __divmod__ before _DeferredValue is evaluated.")
        return divmod(self._value, other)

    def __rdivmod__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rdivmod__ before _DeferredValue is evaluated.")
        return divmod(other, self._value)

    def __pow__(self, other, modulo=None):
        if not self._evaluated:
            raise Exception("Cannot use __pow__ before _DeferredValue is evaluated.")
        if modulo is None:
            return self._value ** other
        else:
            return pow(self._value, other, modulo)

    def __rpow__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rpow__ before _DeferredValue is evaluated.")
        return other ** self._value


    #
    # ========= BITWISE OPERATORS =========
    #
    def __lshift__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __lshift__ before _DeferredValue is evaluated.")
        return self._value << other

    def __rlshift__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rlshift__ before _DeferredValue is evaluated.")
        return other << self._value

    def __rshift__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rshift__ before _DeferredValue is evaluated.")
        return self._value >> other

    def __rrshift__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rrshift__ before _DeferredValue is evaluated.")
        return other >> self._value

    def __and__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __and__ before _DeferredValue is evaluated.")
        return self._value & other

    def __rand__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rand__ before _DeferredValue is evaluated.")
        return other & self._value

    def __or__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __or__ before _DeferredValue is evaluated.")
        return self._value | other

    def __ror__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __ror__ before _DeferredValue is evaluated.")
        return other | self._value

    def __xor__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __xor__ before _DeferredValue is evaluated.")
        return self._value ^ other

    def __rxor__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __rxor__ before _DeferredValue is evaluated.")
        return other ^ self._value

    def __invert__(self):
        if not self._evaluated:
            raise Exception("Cannot use __invert__ before _DeferredValue is evaluated.")
        return ~self._value


    #
    # ========= UNARY OPERATORS =========
    #
    def __neg__(self):
        if not self._evaluated:
            raise Exception("Cannot use __neg__ before _DeferredValue is evaluated.")
        return -self._value

    def __pos__(self):
        if not self._evaluated:
            raise Exception("Cannot use __pos__ before _DeferredValue is evaluated.")
        return +self._value

    def __abs__(self):
        if not self._evaluated:
            raise Exception("Cannot use __abs__ before _DeferredValue is evaluated.")
        return abs(self._value)


    #
    # ========= COMPARISON OPERATORS =========
    #
    def __lt__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __lt__ before _DeferredValue is evaluated.")
        return self._value < other

    def __le__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __le__ before _DeferredValue is evaluated.")
        return self._value <= other

    def __eq__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __eq__ before _DeferredValue is evaluated.")
        return self._value == other

    def __ne__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __ne__ before _DeferredValue is evaluated.")
        return self._value != other

    def __gt__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __gt__ before _DeferredValue is evaluated.")
        return self._value > other

    def __ge__(self, other):
        if not self._evaluated:
            raise Exception("Cannot use __ge__ before _DeferredValue is evaluated.")
        return self._value >= other

    #
    # ========= LOGICAL/BOOLEAN CONTEXT =========
    #
    def __bool__(self):
        if not self._evaluated:
            raise Exception("Cannot use __bool__ before _DeferredValue is evaluated.")
        return bool(self._value)

    #
    # ========= CONTAINER / SEQUENCE PROTOCOL =========
    #
    def __len__(self):
        if not self._evaluated:
            raise Exception("Cannot use __len__ before _DeferredValue is evaluated.")
        return len(self._value)

    def __getitem__(self, key):
        if not self._evaluated:
            raise Exception("Cannot use __getitem__ before _DeferredValue is evaluated.")
        return self._value.__getitem__(key)

    def __setitem__(self, key, value):
        if not self._evaluated:
            raise Exception("Cannot use __setitem__ before _DeferredValue is evaluated.")
        self._value.__setitem__(key, value)

    def __delitem__(self, key):
        if not self._evaluated:
            raise Exception("Cannot use __delitem__ before _DeferredValue is evaluated.")
        self._value.__delitem__(key)

    def __contains__(self, item):
        if not self._evaluated:
            raise Exception("Cannot use __contains__ before _DeferredValue is evaluated.")
        return (item in self._value)

    def __iter__(self):
        if not self._evaluated:
            raise Exception("Cannot iterate before _DeferredValue is evaluated.")
        return iter(self._value)

    def __reversed__(self):
        if not self._evaluated:
            raise Exception("Cannot use reversed() before _DeferredValue is evaluated.")
        return reversed(self._value)

import inspect

def get_callsite_info(skip=2):
    frame = inspect.currentframe()
    for _ in range(skip):
        frame = frame.f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    return {
        'filename': str(filename),
        'lineno': int(lineno)
    }

def print_callsite_info(info, label="[DEBUG] Called from"):
    if not info:
        print("[DEBUG] No callsite info available.")
        return
    print(f"{label} {info['filename']}:{info['lineno']}")


def call_handler(self, handler, callsite_info):
    if len(self._eval_context) > 0:
        _deffered = _DeferredValue(lambda: handler.GetValue(), callsite_info=callsite_info)
        self._eval_context[-1]._deffered.append(_deffered)
        return _deffered
    
    return handler

def call_old_hnalder_function(self, old_method, callsite_info, kargs, kwargs):
    handler = old_method(*kargs, **kwargs)
    if len(self._eval_context) > 0:
        _deffered = _DeferredValue(lambda: handler.GetValue(), callsite_info=callsite_info)
        self._eval_context[-1]._deffered.append(_deffered)
        return _deffered
    
    return handler

# we will not use automatically generated function, to let the stacktrace simpler a bit
def _Sum(self, *kargs, **kwargs):
    return call_old_hnalder_function(self, self._old_Sum, get_callsite_info(), kargs, kwargs)

def _Mean(self, *kargs, **kwargs):
    return call_old_hnalder_function(self, self._old_Mean, get_callsite_info(), kargs, kwargs)

def _Min(self, *kargs, **kwargs):
    return call_old_hnalder_function(self, self._old_Min, get_callsite_info(), kargs, kwargs)

def _Max(self, *kargs, **kwargs):
    return call_old_hnalder_function(self, self._old_Max, get_callsite_info(), kargs, kwargs)

def _Histo1D(self, *kargs, **kwargs):
    return call_old_hnalder_function(self, self._old_Histo1D, get_callsite_info(), kargs, kwargs)

def _Histo2D(self, *kargs, **kwargs):
    return call_old_hnalder_function(self, self._old_Histo2D, get_callsite_info(), kargs, kwargs)

def _Histo3D(self, *kargs, **kwargs):
    return call_old_hnalder_function(self, self._old_Histo3D, get_callsite_info(), kargs, kwargs)

class _EvaluateContext:
    def __init__(self, outer,autoeval):
        self.autoeval = autoeval
        self.outer = outer
        self._deffered = []

    def __enter__(self):
        if not hasattr(self.outer, "_eval_context"):
            self.outer._eval_context = []
        self.outer._eval_context.append(self)

        return self
    
    def evalAll(self):
        for deffered in self._deffered:
            deffered._evaluate()

    def __exit__(self, exc_type, exc_val, exc_tb):
        
        if self.autoeval:
            self.evalAll()

        self.outer._eval_context.pop()

def _Evaluate(df, autoeval=True):
    eval_ctx = _EvaluateContext(df, autoeval)
    return eval_ctx

def init_EvaluateInfo():
    return []
