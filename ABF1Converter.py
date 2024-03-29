import pyabf
import numpy as np
import os
import glob
import json
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBHDF5IO, NWBFile
from pynwb.icephys import CurrentClampStimulusSeries, VoltageClampStimulusSeries, CurrentClampSeries, VoltageClampSeries
from hdmf.backends.hdf5.h5_utils import H5DataIO

def createCompressedDataset(array):
    """
    Request compression for the given array and return it wrapped.
    """

    return H5DataIO(data=array, compression=True, chunks=True, shuffle=True, fletcher32=True)

class ABF1Converter:

    """
    Converts Neuron2BrainLab's ABF1 files from a single cell (collected without amplifier settings from the
    multi-clamp commander) to a collective NeurodataWithoutBorders v2 file.

    Modeled after ABFConverter created by the Allen Institute.

    Parameters
    ----------
    inputPath: path to ABF file or a folder of ABF files to be converted
    outputFilePath: path to the output NWB file
    gain: user-input value
    acquisitionChannelName: Allows to output only a specific acquisition channel, defaults to all
    stimulusChannelName: Allows to output only a specific stimulus channel,
                         defaults to all. The name can also be an AD channel name for cases where
                         the stimulus is recorded as well.
    """

    def __init__(self, inputPath, outputFilePath, gain=None, acquisitionChannelName=None, stimulusChannelName=None):

        self.inputPath = inputPath
        self.debug=False

        if os.path.isfile(self.inputPath):
            print(inputPath)

            abf = pyabf.ABF(self.inputPath)
            if abf.abfVersion["major"] != 1:
                raise ValueError(f"The ABF version for the file {abf} is not supported.")

            self.fileNames = [os.path.basename(self.inputPath)]
            self.abfFiles = [abf]

        elif os.path.isdir(self.inputPath):
            abfFiles = []
            for dirpath, dirnames, filenames in os.walk(self.inputPath):

                # Find all .abf files in the directory
                if len(dirnames) == 0 and len(glob.glob(dirpath + "/*.abf")) != 0:
                    abfFiles += glob.glob(dirpath + "/*.abf")

            if len(abfFiles) == 0:
                raise ValueError(f"{inputPath} contains no ABF Files.")

            # Arrange the ABF files in ascending order
            abfFiles.sort(key=lambda x: os.path.basename(x))

            # Collect file names for description
            self.fileNames = []
            for file in abfFiles:
                self.fileNames += [os.path.basename(file)]

            self.abfFiles = []
            for abfFile in abfFiles:
                # Load each ABF file using pyabf
                abf = pyabf.ABF(abfFile)

                # Check for ABF version
                if abf.abfVersion["major"] != 1:
                    raise ValueError(f"The ABF version for the file {abf} is not supported.")

                self.abfFiles += [abf]

        self.outputPath = outputFilePath

        # Take metadata input, and return hard coded values for None

        if gain:
            self.gain = gain
        else:
            self.gain = 1.0

        self.acquisitionChannelName = acquisitionChannelName
        self.stimulusChannelName    = stimulusChannelName

    def _outputMetadata(self):
        """
        Create metadata files in HTML format next to the existing ABF files.
        """

        for abfFile in self.abfFiles:
            root, ext = os.path.splitext(abfFile.abfFilePath)
            pyabf.abfHeaderDisplay.abfInfoPage(abfFile).generateHTML(saveAs=root + ".html")

    def _getComments(self, abf):

        """
        Accesses the tag comments created in Clampfit
        """

        return abf.tagComments

    def _createNWBFile(self):

        """
        Creates the NWB file for the cell, as defined by PyNWB
        """

        self.start_time =  self.abfFiles[0].abfDateTime
        self.inputCellName = os.path.basename(self.inputPath)

        self.NWBFile = NWBFile(
            session_description="",
            session_start_time=self.start_time,
            identifier=self.inputCellName,
            file_create_date= datetime.now(tzlocal()),
            experimenter=None,
            notes=""
        )
        return self.NWBFile

    def _createDevice(self):

        creatorInfo    = self.abfFiles[0]._headerV1.sCreatorInfo
        creatorVersion = self.abfFiles[0]._headerV1.creatorVersionString

        self.device = self.NWBFile.create_device(name=f"{creatorInfo} {creatorVersion}")

    def _createElectrode(self):

        self.electrode = self.NWBFile.create_ic_electrode(name='elec0', device=self.device, description='PLACEHOLDER')

    def _unitConversion(self, unit):

        # Returns a 2-list of base unit and conversion factor

        if unit == 'V':
            return 1.0, 'V'
        elif unit == 'mV':
            return 1e-3, 'V'
        elif unit == 'A':
            return 1.0, 'A'
        elif unit == 'pA':
            return 1e-12, 'A'
        else:
            # raise ValueError(f"{unit} is not a valid unit.")
            return 1.0, 'V'  # hard coded for units stored as '?'

    def _getClampMode(self):

        """
        Returns the clamp mode of the experiment.

        Voltage Clamp Mode = 0
        Current Clamp Mode = 1
        """

        self.clampMode = self.abfFiles[0]._headerV1.nExperimentType

        return self.clampMode

    def _addStimulus(self):

        """
        Adds a stimulus class as defined by PyNWB to the NWB File.

        Written for experiments conducted from a single channel.
        For multiple channels, refer to https://github.com/AllenInstitute/ipfx/blob/master/ipfx/x_to_nwb/ABFConverter.py
        """

        for idx, abfFile in enumerate(self.abfFiles):

            isStimulus = True

            if self.stimulusChannelName is None:
                channelList = abfFile.adcNames
                channelIndices = range(len(channelList))
            else:
                if self.stimulusChannelName in abfFile.dacNames:
                    channelList = abfFile.dacNames
                    channelIndices = [channelList.index(self.stimulusChannelName)]
                elif self.stimulusChannelName in abfFile.adcNames:
                    isStimulus = False
                    channelList = abfFile.adcNames
                    channelIndices = [channelList.index(self.stimulusChannelName)]
                else:
                    raise ValueError(f"Channel {self.stimulusChannelName} could not be found.")

            for i in range(abfFile.sweepCount):
                for channelIndex in channelIndices:

                    if self.debug:
                        print(f"stimulus: abfFile={abfFile.abfFilePath}, sweep={i}, channelIndex={channelIndex}, channelName={channelList[channelIndex]}")

                    # Collect data from pyABF
                    abfFile.setSweep(i, channel=channelIndex)
                    seriesName = f"Index_{idx}_{i}_{channelIndex}"

                    if isStimulus:
                        data = abfFile.sweepC
                        scaledUnit = abfFile.sweepUnitsC
                    else:
                        data = abfFile.sweepY
                        scaledUnit = abfFile.sweepUnitsY

                    conversion, unit = self._unitConversion(scaledUnit)
                    electrode = self.electrode
                    gain = 1.0  # hard coded for White Noise data
                    resolution = np.nan
                    starting_time = 0.0
                    rate = float(abfFile.dataRate)

                    # Create a JSON file for the description field
                    description = json.dumps({"file_name": os.path.basename(self.fileNames[idx]),
                                              "file_version": abfFile.abfVersionString,
                                              "sweep_number": i,
                                              "protocol": abfFile.protocol,
                                              "protocol_path": abfFile.protocolPath,
                                              "comments": self._getComments(abfFile)},
                                             sort_keys=True, indent=4)

                    # Determine the clamp mode
                    if self.clampMode == 0:
                        stimulusClass = VoltageClampStimulusSeries
                    elif self.clampMode == 1:
                        stimulusClass = CurrentClampStimulusSeries
                    else:
                        raise ValueError(f"Unsupported clamp mode {self.clampMode}")

                    data = createCompressedDataset(data)

                    # Create a stimulus class
                    stimulus = stimulusClass(name=seriesName,
                                             data=data,
                                             sweep_number=i,
                                             electrode=electrode,
                                             gain=gain,
                                             resolution=resolution,
                                             conversion=conversion,
                                             starting_time=starting_time,
                                             rate=rate,
                                             unit=unit,
                                             description=description
                                             )

                    self.NWBFile.add_stimulus(stimulus)

    def _addAcquisition(self):

        """
        Adds an acquisition class as defined by PyNWB to the NWB File.

        Written for experiments conducted from a single channel.
        For multiple channels, refer to https://github.com/AllenInstitute/ipfx/blob/master/ipfx/x_to_nwb/ABFConverter.py
        """

        for idx, abfFile in enumerate(self.abfFiles):

            if self.acquisitionChannelName is None:
                channelList = abfFile.adcNames
                channelIndices = range(len(channelList))
            else:
                if self.acquisitionChannelName in abfFile.adcNames:
                    channelList = abfFile.adcNames
                    channelIndices = [channelList.index(self.acquisitionChannelName)]
                else:
                    raise ValueError(f"Channel {self.acquisitionChannelName} could not be found.")

            for i in range(abfFile.sweepCount):
                for channelIndex in channelIndices:

                    if self.debug:
                        print(f"acquisition: abfFile={abfFile.abfFilePath}, sweep={i}, channelIndex={channelIndex}, channelName={channelList[channelIndex]}")

                    # Collect data from pyABF
                    abfFile.setSweep(i, channel=channelIndex)
                    seriesName = f"Index_{idx}_{i}_{channelIndex}"
                    data = abfFile.sweepY
                    conversion, unit = self._unitConversion(abfFile.sweepUnitsY)
                    electrode = self.electrode
                    gain = 1.0  # hard coded for White Noise data
                    resolution = np.nan
                    starting_time = 0.0
                    rate = float(abfFile.dataRate)

                    # Create a JSON file for the description field
                    description = json.dumps({"file_name": os.path.basename(self.fileNames[idx]),
                                              "file_version": abfFile.abfVersionString,
                                              "sweep_number": i,
                                              "protocol": abfFile.protocol,
                                              "protocol_path": abfFile.protocolPath,
                                              "comments": self._getComments(abfFile)},
                                             sort_keys=True, indent=4)

                    # Create an acquisition class
                    # Note: voltage input produces current output; current input produces voltage output

                    data = createCompressedDataset(data)

                    if self.clampMode == 0:
                        acquisition = CurrentClampSeries(name=seriesName,
                                                         data=data,
                                                         sweep_number=i,
                                                         electrode=electrode,
                                                         gain=gain,
                                                         resolution=resolution,
                                                         conversion=conversion,
                                                         starting_time=starting_time,
                                                         rate=rate,
                                                         unit=unit,
                                                         description=description,
                                                         bias_current=np.nan,
                                                         bridge_balance=np.nan,
                                                         capacitance_compensation=np.nan,
                                                         )

                    elif self.clampMode == 1:
                        acquisition = VoltageClampSeries(name=seriesName,
                                                         data=data,
                                                         sweep_number=i,
                                                         electrode=electrode,
                                                         gain=gain,
                                                         resolution=resolution,
                                                         conversion=conversion,
                                                         starting_time=starting_time,
                                                         rate=rate,
                                                         unit=unit,
                                                         description=description,
                                                         capacitance_fast=np.nan,
                                                         capacitance_slow=np.nan,
                                                         resistance_comp_bandwidth=np.nan,
                                                         resistance_comp_correction=np.nan,
                                                         resistance_comp_prediction=np.nan,
                                                         whole_cell_capacitance_comp=np.nan,
                                                         whole_cell_series_resistance_comp=np.nan
                                                         )
                    else:
                        raise ValueError(f"Unsupported clamp mode {self.clampMode}")

                    self.NWBFile.add_acquisition(acquisition)

    def convert(self):

        """
        Iterates through the functions in the specified order.
        :return: True (for success)
        """

        self._createNWBFile()
        self._createDevice()
        self._createElectrode()
        self._getClampMode()
        self._addStimulus()
        self._addAcquisition()

        with NWBHDF5IO(self.outputPath, "w") as io:
            io.write(self.NWBFile, cache_spec=True)

        print(f"Successfully converted to {self.outputPath}.")
