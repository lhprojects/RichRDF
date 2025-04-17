
# dfa: dict of array
def FlattenNpArray(dfa):
    import numpy as np
    dfa_ = {}
    for k,v in dfa.items():
        if v.dtype != object:
            dfa_[k + "_"] = v.flatten()
        else:
            if len(v) > 0:
                if "RVec<bool>" in type(v[0]).__name__:
                    dfa_[k + "_"] =  np.concatenate(v) != 0
                else:
                    dfa_[k + "_"] =  np.concatenate(v)
    dfa.update(dfa_)
    return dfa
    
