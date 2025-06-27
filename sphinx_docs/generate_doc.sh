rm richrdf*.rst

sphinx-apidoc -o . \
       	../richrdf \
        ../richrdf/ReadEvent.py \
        ../richrdf/Evaluate.py \
        ../richrdf/FlattenNpArray.py \
        ../richrdf/LazyAsNumpy.py \
        ../richrdf/RichRDF.py \
	../richrdf/experimental/misc.py \

sed -i '/^\.\. automodule:: richrdf$/a\   :imported-members:' richrdf.rst

make html



