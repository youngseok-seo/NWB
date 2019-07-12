import pyabf
import numpy as np
import os
import glob
import json
from datetime import datetime
from pynwb import NWBHDF5IO, NWBFile
from pynwb.icephys import CurrentClampStimulusSeries, VoltageClampStimulusSeries, CurrentClampSeries, VoltageClampSeries


class ABF1Converter:

    """
    ABF1Converter converts Neuron2BrainLab's ABF1 files from a single cell to a collective NeurodataWithoutBorders v2 file
    """

    def __init__(self, inputPath, outputFilePath):

        self.inputPath = inputPath

        check = 0
        abfFiles = []
        for dirpath, dirnames, filenames in os.walk(self.inputPath):

            if len(dirnames) == 0 and len(glob.glob(dirpath + "/*.abf")) != 0:
                check += 1
                abfFiles += glob.glob(dirpath + "/*.abf")

        if check == 0:
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

    # def _getHeader(self):
    #
    #     """
    #     Refer to "Unofficial Guide to the ABF File Format" by Scott Harden for bytestring values
    #     """
    #
    #     self.headerText = self.abf.headerText
    #
    #     return self.headerText

    def _getComments(self, abf):

        return abf.tagComments

    def _createNWBFile(self):

        # Create a shell NWB2 file

        self.start_time = self.abfFiles[0].abfDateTime  # TODO: must find the correct time (.abfDateTime may be unreliable)
        self.inputCellName = os.path.basename(self.inputPath)

        self.NWBFile = NWBFile(
            session_description="",
            session_start_time=self.start_time,
            identifier=self.inputCellName,
            file_create_date= datetime.today(),
            experimenter="HM",
            lab="Valiante Laboratory",
            institution="University of Toronto",
            notes=""
        )
        return self.NWBFile

    def _createDevice(self):

        self.device = self.NWBFile.create_device(name='Clampfit')

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
            return 1.0, 'V'  # hard coded because some units were '?'

    def _getClampMode(self):

        self.clampMode = 1

        return self.clampMode  # hard coded for Current Clamp Mode

    def _addStimulus(self):

        # Determine the correct stimulus class for the given clamp mode (V = 0; I = 1)

        sweepGlobal = 0
        for idx, abfFile in enumerate(self.abfFiles):

            for i in range(abfFile.sweepCount):

                # determine whether we need to go through different channels - header only has 1

                abfFile.setSweep(i)
                seriesName = "Index_" + str(i + sweepGlobal)
                data = abfFile.sweepC
                conversion, unit = self._unitConversion(abfFile.sweepUnitsC)
                electrode = self.electrode
                gain = 1.0  # hard coded for White Noise data
                resolution = np.nan
                starting_time = 0.0
                rate = float(abfFile.dataRate)
                description = json.dumps({"file_name": os.path.basename(self.fileNames[idx]),
                                          "file_version": abfFile.abfVersionString,
                                          "sweep_number": i,
                                          "protocol": abfFile.protocol,
                                          "protocol_path": abfFile.protocolPath,
                                          "comments": self._getComments(abfFile)},
                                         sort_keys=True, indent=4)

                if self.clampMode == 0:
                    stimulusClass = VoltageClampStimulusSeries
                elif self.clampMode == 1:
                    stimulusClass = CurrentClampStimulusSeries

                stimulus = stimulusClass(name=seriesName,
                                         data=data,
                                         sweep_number=i,
                                         unit=unit,
                                         electrode=electrode,
                                         gain=gain,
                                         resolution=resolution,
                                         conversion=conversion,
                                         starting_time=starting_time,
                                         rate=rate,
                                         description=description
                                         )

                self.NWBFile.add_stimulus(stimulus)

            sweepGlobal += abfFile.sweepCount

        return True

    def _addAcquisition(self):

        sweepGlobal = 0
        for idx, abfFile in enumerate(self.abfFiles):

            for i in range(abfFile.sweepCount):

                abfFile.setSweep(i)
                seriesName = "Index_" + str(i + sweepGlobal)
                data = abfFile.sweepY
                conversion, unit = self._unitConversion(abfFile.sweepUnitsY)
                electrode = self.electrode
                gain = 1.0  # hard coded for White Noise data
                resolution = np.nan
                starting_time = 0.0
                rate = float(abfFile.dataRate)
                description = json.dumps({"file_name": os.path.basename(self.fileNames[idx]),
                                          "file_version": abfFile.abfVersionString,
                                          "sweep_number": i,
                                          "protocol": abfFile.protocol,
                                          "protocol_path": abfFile.protocolPath,
                                          "comments": self._getComments(abfFile)},
                                         sort_keys=True, indent=4)

                # Voltage input produces current output; current input produces voltage output

                if self.clampMode == 0:
                    acquisition = CurrentClampSeries(name=seriesName,
                                                     data=data,
                                                     sweep_number=i,
                                                     unit=unit,
                                                     electrode=electrode,
                                                     gain=gain,
                                                     resolution=resolution,
                                                     conversion=conversion,
                                                     starting_time=starting_time,
                                                     rate=rate,
                                                     description=description,
                                                     bias_current=np.nan,
                                                     bridge_balance=np.nan,
                                                     capacitance_compensation=np.nan,
                                                     )

                elif self.clampMode == 1:
                    acquisition = VoltageClampSeries(name=seriesName,
                                                     data=data,
                                                     sweep_number=i,
                                                     unit=unit,
                                                     electrode=electrode,
                                                     gain=gain,
                                                     resolution=resolution,
                                                     conversion=conversion,
                                                     starting_time=starting_time,
                                                     rate=rate,
                                                     description=description,
                                                     capacitance_fast=np.nan,
                                                     capacitance_slow=np.nan,
                                                     resistance_comp_bandwidth=np.nan,
                                                     resistance_comp_correction=np.nan,
                                                     resistance_comp_prediction=np.nan,
                                                     whole_cell_capacitance_comp=np.nan,
                                                     whole_cell_series_resistance_comp=np.nan
                                                     )

                self.NWBFile.add_acquisition(acquisition)

            sweepGlobal += abfFile.sweepCount

        return True

    def convert(self):

        print(f"Converting files in {os.path.basename(self.inputPath)}...")
        # self._getHeader()
        self._createNWBFile()
        self._createDevice()
        self._createElectrode()
        self._getClampMode()
        self._addStimulus()
        self._addAcquisition()

        with NWBHDF5IO(self.outputPath, "w") as io:
            io.write(self.NWBFile)

        print(f"Successfully converted to {self.outputPath}.")

        return True













