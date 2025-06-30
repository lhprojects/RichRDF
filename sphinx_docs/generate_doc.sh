rm richrdf*.rst

sphinx-apidoc -o . \
       	../richrdf \
        ../richrdf/Evaluate.py \
        ../richrdf/FlattenNpArray.py \
        ../richrdf/LazyAsNumpy.py \
        ../richrdf/RichRDF.py \
	../richrdf/experimental/misc.py \
        
	#../richrdf/ReadEvent.py \

sed -i '/^\.\. automodule:: richrdf$/a\   :imported-members:' richrdf.rst

make html



