## Example ABF v2 Files

#### Sample files from laboratories collecting ABF v2 files

This directory contains files obtained from collaborators using pClamp v10+. These files are stored in ABF version 2. 
The conversion process outlined in this repository address ABF version 1 files, and therefore are incompatible with the files listed in this directory.



#### Attempts to use the Allen Institute's conversion pipeline

The Allen Institute's [ipfx repository](https://github.com/AllenInstitute/ipfx) contains converter scripts for ABF version 2 files. 
`18823042.abf` and `JS-A2-C03(350)-P01-2017_10_13_0013.abf` were given as inputs to the converter in attempts to create NWB version 2.. files.

The conversion failed due to errors in the [PyNWB](https://github.com/NeurodataWithoutBorders/pynwb) module. 
These error messages were documented and raised as an issue on the [ipfx/x_to_nwb](https://github.com/AllenInstitute/ipfx/tree/master/ipfx/x_to_nwb) repository.

The issue can be found [here](https://github.com/AllenInstitute/ipfx/issues/261).
