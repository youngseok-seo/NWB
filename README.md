## Converting ABF1 files to NWB2

`abf_to_nwb.py` converts white noise stimulus ABF v1 files to NWB v2 files.

`cc_step_abf_to_nwb.py` converts step stimulus ABF v1 files to NWB v2 files.

#### Example:

Convert a step stimulus file to NWB by downloading the sample ABF file, and executing the command as specified below. 
The ABF v1 file and the output NWB v2 file can be found in `data/abf1`. 

```
python3 cc_step_abf_to_nwb.py "path/to/inputFolder" "path/to/outputFolder"
```

__Note:__ `"path/to/outputFolder"` must not contain the output file.

### Process

The conversion process as outlined in this repository is divided into a two-step process:
 1.  A customized function parses a specified directory hierarchy to obtain metadata and create NWB file names. The function creates a list of ABF files which are then organized at the cellular level.
 2.  The file(s) are passed onto a general converter class which executes the conversion.
 
Although `ABF1Converter.py` is generalized for all inputs organized at the cell level, the file handling functions require a customized script for each lab per experiment type. The input for the converter class can be one or multiple ABF files per cell; `abf_to_nwb.py` is an example of a function which collects a list of ABF files as input, while `cc_step_abf_to_nwb.py` exemplify a use case where only one ABF file exists per cell. 

It is important to note that these file handling functions should only be referred to as examples--they contain manually assigned variables which are not compatible with other experiment types or file organization structures. 

_Note: The functions were written specifically for files collected using current clamp mode at Toronto Western Hospital. __abf_to_nwb.py__ was written for white noise stimulus experiments, and __cc_step_abf_to_nwb.py__ for step stimulus experiments._

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
  

  
