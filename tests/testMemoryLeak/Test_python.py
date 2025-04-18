#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
import os

print("python path", sys.executable)
print("python version", sys.version)

richrdf_path = os.path.abspath(os.path.join(os.getcwd(), '../..'))
sys.path.append(richrdf_path)

import richrdf
import richrdf.experimental

try:
    import ROOT
except ImportError:
    import richrdf.experimental.setupROOT
    cvmfsversion="2024-10-03/x86_64-ubuntu22.04-gcc11.4.0-opt"
    print(f"\nNo ROOT can be imported, trying to set up ROOT from cvmfs {cvmfsversion}\n")
    try:
        richrdf.experimental.setupROOT.setupROOT(cvmfsversion=cvmfsversion)
        import ROOT
        print("\nROOT from cvmfs loaded\n")
    except ImportError:
        print("\nROOT not found, please set up ROOT\n")

ROOT.gInterpreter.AddIncludePath(richrdf.get_include_path())

print(richrdf.get_include_path())


# In[ ]:


if not os.path.exists("zh_mumu_REC.edm4hep.root"):
    # Download the sample file
    import urllib.request
    url = "https://raw.githubusercontent.com/lhprojects/edm4hep_sample/refs/heads/main/ILD/zh_mumu_REC.edm4hep.root"
    urllib.request.urlretrieve(url, "zh_mumu_REC.edm4hep.root")
    
filename = "zh_mumu_REC.edm4hep.root"




# In[ ]:


ROOT.gInterpreter.Declare('''
#include <rrdf.h>
struct Ans1 { int mcp_size; };
Ans1 analyzeEvent(rrdf::Event const &event) {
    static int i = 0;
    //rrdf::print("Event number: {}", i++);
    //fprintf(stderr, "stderr Event number: %d\\n", i);
    Ans1 ans;
    ans.mcp_size = event.getMCParticles("MCParticles").size();
    return ans;
}''')


# In[ ]:


import sys

arg = "allcoll_evt"
if len(sys.argv) > 1:
    arg = sys.argv[1]

huge_file_name = "/home/liangh/huge.edm4hep.root"
NRepeat=2

if arg == "allcoll_evt":
    df = richrdf.RichRDF("events", [huge_file_name]*NRepeat)
    df = df.ReadEvent("event")
    df = df.Define("a", "analyzeEvent(event).mcp_size")
    a = df.Sum("a").GetValue()
    print("a", a)

elif arg == "allcoll_RDataFrame":
    df = ROOT.RDataFrame("events", [huge_file_name]*NRepeat)
    vector_branches = [b  for b in df.GetColumnNames() if "." not in b]

    for b in vector_branches:
        df = df.Define(f"{b}_size", f"{b}.size()")

    size_columns = [f"{b}_size" for b in vector_branches]
    sum_expr = " + ".join(size_columns)
    df = df.Define("total_size_sum", sum_expr)

    total_sum = df.Sum("total_size_sum").GetValue()
    print("Total size sum over all vector branches:", total_sum)
elif arg == "mcrec_evt":
    df = richrdf.RichRDF("events", [huge_file_name]*NRepeat)
    df = df.ReadEvent("event", ["MCParticles", "PandoraPFOs"])
    df = df.Define("a", "analyzeEvent(event).mcp_size")
    a = df.Sum("a").GetValue()
    print("a", a)

elif arg == "mcrec_RDataFrame":
    df = ROOT.RDataFrame("events", [huge_file_name]*NRepeat)
    df = df.Define("totalsize", "MCParticles.size() + PandoraPFOs.size()")
    mcp_size_sum = df.Sum("totalsize")
    print("mcp_size_sum", mcp_size_sum.GetValue())


