# Benchmarks

##  Memory usage for reading

Two files were read, each containing 892 events and approximately 4.2 GB of data.

All collections of an event accessed using `ReadEvent`:

<img src="../tests/testMemoryLeak/images/allcoll_evt.png" width="300"/>

All collections of an event accessed using `RDataFrame.Define` without further processing:

<img src="../tests/testMemoryLeak/images/allcoll_RDataFrame.png" width="300"/>

`MCParticles` and `PandoraPFOs` of an event accessed using `ReadEvent`:

<img src="../tests/testMemoryLeak/images/mcrec_evt.png" width="300"/>

`MCParticles` and `PandoraPFOs` of an event accessed using `RDataFrame.Define` without further processing:

<img src="../tests/testMemoryLeak/images/mcrec_RDataFrame.png" width="300"/>


The reported time includes environment setup, invocation of Define or ReadEvent, and just-in-time (JIT) compilation. Therefore, it does not accurately reflect the time required solely for reading events.

Source code can be found in `../tests/testMemoryLeak`.
