## Converting ABF1 files to NWB2

`abf_to_nwb.py` converts ABF v1 files to NWB v2 files.

#### Example:
```
abf_to_nwb.py "path/to/inputFolder" "path/to/outputFolder"
```


### Specifications

* The script is customized for intracellular electrophysiology data collected during a patch clamp experiment through a _single_ channel, __without__ the presence of an external file containing amplifier settings.
* The data must be acquired by the Axon pClamp v9.2 software. _[Download pClamp 9](http://mdc.custhelp.com/app/answers/detail/a_id/18826/related/1)_

### Organization 

Files are organized at the _cell_ level.
  * Date and cell number are collected from the directory names, which must be present in "path/to/inputFolder" as __"Month Day, Year/Cell #"__.
  * The script collects all ABF v1 files located in each cell directory and converts them into a unified NWB v2 file __"MM-DD-YY-C#.nwb"__.

### Validation

The resulting NWB v2 file can be validated in the following ways:
  * Open the file using HDFView. _[Download HDFView](https://www.hdfgroup.org/downloads/hdfview)_
  * Run `create_nwb_pdf.py` to create a PDF file with graphs that provide a visual representation of the data.
  * Use the NWB Jupyter Widgets provided by Neurodata Without Borders. _[GitHub](https://github.com/NeurodataWithoutBorders/nwb-jupyter-widgets)_
  

  
