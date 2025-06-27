import os
import sys
import glob

def setupROOT(cvmfsversion: str):
    """
    Configure ROOT and environment paths based on a given Key4HEP CVMFS version.

    This function sets up the necessary `LD_LIBRARY_PATH`, Python import paths,
    and ROOT include paths for working with `edm4hep` and `podio` using the CVMFS-based
    Key4HEP stack. It dynamically locates shared libraries and includes, loads required
    ROOT libraries, and modifies the runtime environment accordingly.

    Parameters
    ----------
    cvmfsversion : str
        The Key4HEP release version or full path. Example:
        - "2024-10-03/x86_64-almalinux9-gcc14.2.0-opt"
        - "/cvmfs/sw.hsf.org/key4hep/releases/2024-10-03/x86_64-almalinux9-gcc14.2.0-opt"

    Notes
    -----
    - This function assumes that CVMFS is mounted and accessible at `/cvmfs`.

    Examples
    --------
    >>> setupROOT("2024-10-03/x86_64-almalinux9-gcc14.2.0-opt")
    >>> import ROOT
    """    
    print("CVMFS version", cvmfsversion)

    if cvmfsversion.startswith("/cvmfs/"):
        key4hep_path=cvmfsversion
    else:
        key4hep_path=f"/cvmfs/sw.hsf.org/key4hep/releases/{cvmfsversion}"
        
    lddir = []
    lddir.extend(glob.glob(f"{key4hep_path}/root/*/lib"))
    lddir.extend(glob.glob(f"{key4hep_path}/edm4hep/*/lib"))
    lddir.extend(glob.glob(f"{key4hep_path}/podio/*/lib"))

    print("LDDIR ", lddir)

    lddir = ":".join(lddir)
    os.environ["LD_LIBRARY_PATH"] = lddir + ":" + os.environ.get("LD_LIBRARY_PATH", "")


    # use cvmfs ROOT
    rootdir = glob.glob(f"{key4hep_path}/root/*/lib")
    print("ROOTDIR", rootdir, [rootdir_ + "/root" for rootdir_ in rootdir])
    for rootdir_ in rootdir:
        sys.path.append(rootdir_)
        sys.path.append(rootdir_ + "/root")

    includes = []
    includes.extend(glob.glob(f"{key4hep_path}/edm4hep/*/include"))
    includes.extend(glob.glob(f"{key4hep_path}/podio/*/include"))
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
    ROOT.gSystem.Load(f"libpodioRootIO.so")
    ROOT.gSystem.Load(f"libpodioRootIODict.so")
     
    #ROOT.gSystem.Load(f"libGLU.so")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Setup ROOT for CVMFS.')
    parser.add_argument('cvmfsversion', type=str, help='CVMFS version to setup')
    args = parser.parse_args()
    
    setupROOT(args.cvmfsversion)
    print("\nThis will no long take effect after you exit python\n")
