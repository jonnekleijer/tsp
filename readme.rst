TSP
===

intro
-----
Python scripts for plotting transient model result with measurements in timeseries figures. Written for Python 3.5. Required packages:
- Pandas
- Matplotlib

contents
--------
scripts (*.py):
- series2store.py: read series from Menyanthes style CSV file and write to HDF5 store
- plot.py: plot timeseries from HDF5 stores, grouped by name and filternumber
- iplot.py: interactive plot timeseries from HDF5 stores, grouped by name and filternumber

input files (*.yaml):
- series2store_ijkset.yaml: inputfile for series2store.py for measurements ("ijkset")
- series2store_ns_gemref.yaml: example inputfile for series2store.py for scenario gemref
- series2store_ns_gemref.yaml: example inputfile for series2store.py for scenario kal2
- plot.yaml: inputfile for plot.py
- iplot.yaml: inputfile for iplot.py

batchfiles (*.bat):
- series2store.bat: run series2store.py for selected inputfiles
- plot.bat run plot.py for selected inputfiles
- iplot.bat run iplot.py for selected inputfiles

workflow
--------
1. run series2store.py for measurements if not yet present
2. run series2store.py for selected scenarios / model results
3. run plot.py or run iplot.py

Be sure to check the input files before running the scripts, especially the output folder.
