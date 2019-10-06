## Converting ABF1 files to NWB2

`abf_to_nwb.py` converts ABF v1 files to NWB v2 files.

#### Example:

Convert a step stimulus file to NWB by downloading the sample ABF file and executing the following command. 

```
python3 abf_to_nwb.py "path/to/inputFolder" "path/to/outputFolder"
```

The ABF v1 file and the output NWB v2 file can be found in `data/abf1`. 

__Note:__ `"path/to/outputFolder"` must not contain the output file.

### Process

The conversion process as outlined in this repository is divided into a two-step process:
 1.  `abf_to_nwb.py` parses the specified input folder to create a list of ABF files, which are organized by cell. 
 2.  The file(s) are passed into `ABF1Converter.py` which executes the conversion.

`abf_to_nwb.py` is generalized for the example conversion. It can be customized to collect lab-specific metadata for organizational purposes. The files `white_noise_abf_to_nwb.py` and `cc_step_abf_to_nwb.py` were written for the Toronto Western Hospital, and can be used as reference. 


### Specifications

* The script is customized for intracellular electrophysiology data collected during a patch clamp experiment through a _single_ channel, __without__ the presence of an external file containing amplifier settings.
* The data must be acquired by the Axon pClamp v9.2 software. _[Download pClamp 9](http://mdc.custhelp.com/app/answers/detail/a_id/18826/related/1)_


### Validation

The resulting NWB v2 file can be validated in the following ways:
  * Open the file using HDFView. _[Download HDFView](https://www.hdfgroup.org/downloads/hdfview)_
  * Run `create_nwb_pdf.py` to create a PDF file with graphs that provide a visual representation of the data.
  * Use the NWB Jupyter Widgets provided by Neurodata Without Borders. _[GitHub](https://github.com/NeurodataWithoutBorders/nwb-jupyter-widgets)_
  

  
