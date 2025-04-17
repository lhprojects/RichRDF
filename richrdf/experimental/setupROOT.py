import os
import sys
import glob

def setupROOT(cvmfsversion: str):
    print("CVMFS version", cvmfsversion)
        
    lddir = []
    lddir.extend(glob.glob(f"/cvmfs/sw.hsf.org/key4hep/releases/{cvmfsversion}/root/*/lib"))
    lddir.extend(glob.glob(f"/cvmfs/sw.hsf.org/key4hep/releases/{cvmfsversion}/edm4hep/*/lib"))
    lddir.extend(glob.glob(f"/cvmfs/sw.hsf.org/key4hep/releases/{cvmfsversion}/podio/*/lib"))

    print("LDDIR ", lddir)

    lddir = ":".join(lddir)
    os.environ["LD_LIBRARY_PATH"] = lddir + ":" + os.environ["LD_LIBRARY_PATH"]


    # use cvmfs ROOT
    rootdir = glob.glob(f"/cvmfs/sw.hsf.org/key4hep/releases/{cvmfsversion}/root/*/lib")
    print("ROOTDIR", rootdir)
    for rootdir_ in rootdir:
        sys.path.append(rootdir_)

    includes = []
    includes.extend(glob.glob(f"/cvmfs/sw.hsf.org/key4hep/releases/{cvmfsversion}/edm4hep/*/include"))
    includes.extend(glob.glob(f"/cvmfs/sw.hsf.org/key4hep/releases/{cvmfsversion}/podio/*/include"))
    print("Includes", includes)


    import ROOT
    # this line must be before OT.gSystem.Load
    for inc in includes:
        ROOT.gInterpreter.AddIncludePath(inc)

    ROOT.gSystem.Load("libedm4hep.so")
    ROOT.gSystem.Load("libedm4hepDict.so")
    ROOT.gSystem.Load(f"libedm4hepRDF.so")
    ROOT.gSystem.Load(f"libedm4hepUtils.so")

    ROOT.gSystem.Load(f"libpodio.so")
    ROOT.gSystem.Load(f"libpodioDict.so")
     
    #ROOT.gSystem.Load(f"libGLU.so")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Setup ROOT for CVMFS.')
    parser.add_argument('cvmfsversion', type=str, help='CVMFS version to setup')
    args = parser.parse_args()
    
    setupROOT(args.cvmfsversion)
    print("\nThis will no long take effect after you exit python\n")
