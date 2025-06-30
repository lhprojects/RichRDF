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


# In[ ]:


filename = "zh_mumu_REC.edm4hep.root"
df = richrdf.RichRDF("events", filename)

podio_metadata = df.getMetadata().podio_metadata
print(podio_metadata.getCollTypeInfos())
for collName in podio_metadata.getCollNames():
    try:
        collID = podio_metadata.getCollIDByName(collName)
        collType = podio_metadata.getCollTypeByID(collID)
        print(f"{collName:<40} {collID:<15} {collType.name}")
        
    except ValueError as e:
        print(f"Error retrieving collection {collName} ID {collID}")
        

