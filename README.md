
# Introduction
`Podio` is a lightweight and flexible data model library designed for high-energy physics experiments.
`RDataFrame` is a high-level, declarative framework designed for efficient data processing, with performance.
We develop a python package Rich Root Data Frame (`RichRDF`) to combine `Podio` and RDataFrame to leverage the strengths of both tools.

`Podio` supports a loop-based interface and provides both C++ and Python bindings.
While C++ offers high performance, it's less convenient for interacting directly with Python.
Python, on the other hand, is more user-friendly but less efficient.
We developed **`RichRDF`** to combine **`Podio`** and **`RDataFrame`**, leveraging the strengths of both tools—convenience and efficiency—as shown in the following table:

| Interface               | Convenience         | Efficiency |
|-------------------------|---------------------|------------|
| Podio with C++          | Not convenient      | High       |
| Podio with Python       | Convenient          | Low        |
| Podio with RDataFrame   | Medium convenient   | High       |



# Installation

## Prerequisites

You need to have `ROOT`, `podio`, and `edm4hep` installed.  
The easiest way to set them up is by using CVMFS. For example:

```bash
source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2024-10-03
```


## Install using pip

To install via `pip` from the `github`:
```bash
pip install git+https://github.com/lhprojects/RichRDF.git
```

Alternatively, you can install from the source:

```bash
pip install /path/to/this/project
```

Make sure the `/path/to/this/project` directory contains `richrdf/` and `setup.py`.


## Use without installation

If you prefer not to install the package, you can still use it by setting the `PYTHONPATH`.

In your terminal (`bash`):

```bash
PYTHONPATH=/path/to/this/project:$PYTHONPATH
```

Or, use the provided setup script:

```bash
source /path/to/this/project/setup.sh
```


If you're already inside a Python script or Jupyter notebook and can't change the environment, you can do:

```python
import sys
sys.path.append("/path/to/this/project")
```

# A Tutorial

### Read edm4hep Event

```python
import richrdf
import ROOT

# the edm4hep.root to open
filename = "zh_mumu_REC.edm4hep.root"

# we have some headers, add path of those headers to your system
ROOT.gInterpreter.AddIncludePath(richrdf.get_include_path())

# load the c++ code that analyze the data
ROOT.gInterpreter.Declare('''
#include <rrdf.h> // the header you need to include for richrdf

struct Ans1 {
    ROOT::VecOps::RVec<double> pi0_E;
    // ...
};

Ans1 analyzeEvent(rrdf::Event const &evt) {
    Ans1 ans1;
    ana::span<const MCParticle> mcps = evt.getMCParticles("MCParticles");
    for(int i : rrdf::range(mcps.size())) {
        edm4hep::MCParticle mcp = mcps[i];
        // more code here
    }
    return ans1;
}
''')

df = richrdf.RichRDF("events", filename)

# read event with two collections
df = df.ReadEvent("event", ["MCParticles", "PandoraPFOs"])

# Analyze the data and store the result in 'ans'
# This part works just like using RDataFrame
df = df.Define("ans", "analyzeEvent(event)")
df = df.Define("pi0_n", "ans.pi0_E.size()")
# more code here
```

We will provide a detailed description of how to use each functions.


### `RichRDF`
The usage of `RichRDF` is as follows:
```python
df = richrdf.RichRDF("events", filename)
```
The `RichRDF` function takes a variable number of positional and keyword arguments. Typically, the first positional argument is the name of the `TTree`, such as `"events"`, which is the default for `edm4hep` data. The second is usually the ROOT file name. For `edm4hep` files, the tree is almost always named `"events"`, and metadata is included in the same file. However, if you're reading a plain ROOT file that doesn't follow the `edm4hep` format, you may see warnings or errors due to missing metadata. In such cases, it's recommended to set `readMetadata=False` to skip the metadata reading process. By default, `readMetadata` is set to `True`, because metadata is necessary when using methods like `ReadEvent`. 


You can also pass an `RDataFrame` class,
through the `RDataFrame` parameter instead of using the default one: `ROOT.RDataFrame`, e.g.,
```python
df = richrdf.RichRDF("events", filename, RDataFRame=ROOT.RDF.Experimental.Distributed.Dask.RDataFrame)
```

### `ReadEvent`

```python
df = df.ReadEvent("event", ["MCParticles", "PandoraPFOs"])
```
This will define an `"event"` column in the DataFrame that includes the `MCParticles` and `PandoraPFOs` collections.






Elements in `PandoraPFOs` are typically of type `edm4hep::ReconstructedParticle`, which has four associated relations: `clusters`, `tracks`, `particles`, and `vertex`.
By default, `ReadEvent` does **not** load these related collections unless you explicitly specify them as arguments when calling `ReadEvent`.
If you don't provide these collections as arguments, you can still call `auto clusters = rec.getClusters();`.
However, this will return an array of **empty clusters** (not an empty array of cluster).
As a result, `rec.getClusters()[...].isValid()` will return `false`.  
If you try to access data like `rec.getClusters()[...].getEnergy()`, your program is almost guaranteed to crash. This is because `podio` is designed **not to throw exceptions**, even for invalid access.



Due to limitations of `RDataFrame`, we cannot automatically add related collections such as clusters for you—you'll need to do this manually. You can enable `throwExceptionOnRefCollIDNotFound` to catch missing references, e.g.,
```python
df = df.ReadEvent("event", ["MCParticles", "PandoraPFOs"], throwExceptionOnRefCollIDNotFound=True)
```
This setting makes the program throw an exception if a collection refers to another collection that hasn’t been loaded. Note that the exception will be raised when you loop over events, not when registering collections. This is because collection dependencies cannot be determined just from metadata; they require reading the actual event data. This is also why we can’t automatically register the related collections for you.


You can leave collection `None`, to read all collections, e.g.,
```python
df = df.ReadEvent("event", None)
# or simply
df = df.ReadEvent("event")
```


### `rrdf::Event`

You can get an `ana::span<const MCParticle>` from `evt.getMCParticles()` like this:
```c++
ana::span<const MCParticle> mcps = evt.getMCParticles("MCParticles");
MCParticle mcp = mcps[0];
```

An `ana::span<const MCParticle>` is essentially just two raw pointers. It's similar to `std::span` in C++ and does not own the underlying data, so you're free to copy it as needed.

For other collections, you can use `evt.getElements<Type>()`. `evt.getMCParticles` is essentially `evt.getElements<edm4hep::MCParticle>`.

Alternatively, you can call `evt.getMCParticleCollection("MCParticles")` to get a `const MCParticleCollection&`. The key issue here is that while you can iterate over this collection like:
```c++
for (auto x : evt.getMCParticleCollection("MCParticles")) { ... }
```
But you **cannot** copy the iterator of `MCParticleCollection` due to design constraints. This means you'll run into compilation errors if you try something very simple like:
```c++
auto& coll = evt.getMCParticleCollection("MCParticles");
std::find(coll.begin(), coll.end(), ...);
```
Moreover, when you do `*coll.begin()`, it returns a newly constructed `MCParticle` instead of a reference. the underlying collection does not actually store an array of `MCParticle` objects.
Although constructing an `MCParticle` is nearly as cheap as copying a pointer. This could lead to failures of compilation in corner cases.
To address this, I've decided to internally store an array of `MCParticle` objects for you, so that you have a easier-to-use `ana::span<...>`.







Note:
`mcp` is of type `edm4hep::MCParticle`. The documentation from `edm4hep` for `edm4hep::MCParticle` provides a detailed introduction. Here, we give a short introduction to `edm4hep::MCParticle`. `mcp` is essentially a lightweight wrapper around a raw pointer. 
You don’t need to use `mcp->getXXX()` — it’s conveniently designed so that you can simply use `mcp.getXXX()`. Note that `mcp` does not own the memory it points to. Copying `mcp` is very cheap, so feel free to copy it as needed. While it's not as lightweight as a raw pointer, it's still cheaper than using a `shared_ptr`. Of course, copying `mcp` does not perform a deep copy.



### `Evaluate`
(In progress.)

# Utils

[Utils](./docs/Utils.md)

# Examples

[Examples](./docs/Examples.md)


# Benchmarks

[Benchmarks](./docs/Benchmarks.md)
