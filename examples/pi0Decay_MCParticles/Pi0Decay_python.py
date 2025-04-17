#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import os

print("python path", sys.executable)
print("python version", sys.version)

richrdf_path = os.path.abspath(os.path.join(os.getcwd(), '../..'))
sys.path.append(richrdf_path)

try:
    import ROOT
except ImportError:
    import richrdf.experimental.setupROOT
    cvmfsversion="2024-10-03/x86_64-almalinux9-gcc14.2.0-opt"
    print(f"\nNo ROOT can be imported, trying to set up ROOT from cvmfs {cvmfsversion}\n")
    try:
        import richrdf.experimental
        richrdf.experimental.setupROOT.setupROOT(cvmfsversion=cvmfsversion)
        import ROOT
        print("\nROOT from cvmfs loaded\n")
    except ImportError:
        print("\nROOT not found, please set up ROOT\n")

import richrdf
print(richrdf.get_include_path())



# In[2]:


if not os.path.exists("zh_mumu_REC.edm4hep.root"):
    # Download the sample file
    import urllib.request
    url = "https://raw.githubusercontent.com/lhprojects/edm4hep_sample/refs/heads/main/ILD/zh_mumu_REC.edm4hep.root"
    urllib.request.urlretrieve(url, "zh_mumu_REC.edm4hep.root")
    


# In[3]:


import richrdf
ROOT.gInterpreter.AddIncludePath(richrdf.get_include_path())
ROOT.gInterpreter.Declare('#include "analyzeEvent.cpp"')


# In[4]:


filename = "zh_mumu_REC.edm4hep.root"
df = richrdf.RichRDF("events", filename)
df = df.ReadEvent("event", ["MCParticles", "PandoraPFOs"], throwExceptionOnRefCollIDNotFound=False)
df = df.Define("ans", "analyzeEvent(event)")
df = df.Define("pi0_n", "ans.pi0_E.size()")
df = df.Define("photon_n", "ans.ph_E1.size()")


ph_sum = df.Sum("photon_n")
pi0_sum = df.Sum("pi0_n")
        
ratio = ph_sum.GetValue()/pi0_sum.GetValue()
print("Braching ratios", ratio)

