import pyabf
import numpy as np
import os
from datetime import datetime
from pynwb import NWBHDF5IO, NWBFile
from pynwb.icephys import CurrentClampStimulusSeries, VoltageClampStimulusSeries, CurrentClampSeries, VoltageClampSeries


class ABF1Converter:

    """
    ABF1Converter converts Neuron2BrainLab's ABF1 file to NeurodataWithoutBorders v2 file
    """

    def __init__(self, inputFilePath, outputFilePath):

        self.inputFilePath = inputFilePath
        self.abf = pyabf.ABF(self.inputFilePath)
        self.outputPath = outputFilePath

    def _getHeader(self):

        """
        Refer to "Unofficial Guide to the ABF File Format" by Scott Harden for bytestring values
        """

        self.headerText = self.abf.headerText

        return self.headerText

    def _getComments(self):

        self.comments = self.abf.tagComments

        return self.comments

    def _createNWBFile(self):

        # Create a shell NWB2 file

        self.start_time = self.abf.abfDateTime
        self.inputFileName = os.path.basename(self.inputFilePath)
        self.inputFileNo = os.path.splitext(self.inputFileName)[0]

        notes = ''
        for comment in self.comments:
            notes += comment

        self.NWBFile = NWBFile(
            session_description= "include Cell number and patient condition, from json?",
            session_start_time=self.start_time,
            identifier=self.inputFileNo,
            file_create_date= datetime.today(),
            experimenter='HM',
            lab='Valiante Laboratory',
            institution='University of Toronto',
            notes=notes
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
            return 1.0, 'V' # hard coded because some units were '?'

    def _getClampMode(self):

        self.clampMode = 1

        return 1  # hard coded for Iclamp

    def _addStimulus(self):

        # Determine the correct stimulus class for the given clamp mode (V = 0; I = 1)

        for i in range(self.abf.sweepCount):

            # determine whether we need to go through different channels - header only has 1

            if self.clampMode == 0:
                stimulusClass = VoltageClampStimulusSeries
            elif self.clampMode == 1:
                stimulusClass = CurrentClampStimulusSeries

            self.abf.setSweep(i)
            seriesName = "Index_{number: 0{math.ceil(math.log(total, 10))}d}" + str(i)
            data = self.abf.sweepC
            conversion, unit = self._unitConversion(self.abf.sweepUnitsC)
            electrode = self.electrode
            gain = 1.0  # hard coded for White Noise data
            resolution = np.nan
            starting_time = 0.0
            rate = float(self.abf.dataRate)
            description = 'N/A'

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

        return True

    def _addAcquisition(self):

        for i in range(self.abf.sweepCount):

            # Voltage input produces current output; current input produces voltage output
            if self.clampMode == 0:
                acquisitionClass = CurrentClampSeries
            elif self.clampMode == 1:
                acquisitionClass = VoltageClampSeries

            self.abf.setSweep(i)
            seriesName = "Index_{number: 0{math.ceil(math.log(total, 10))}d}" + str(i)
            data = self.abf.sweepY
            conversion, unit = self._unitConversion(self.abf.sweepUnitsY)
            electrode = self.electrode
            gain = 1.0  # hard coded for White Noise data
            resolution = np.nan
            starting_time = 0.0
            rate = float(self.abf.dataRate)
            description = 'N/A'
            acquisition = acquisitionClass(name=seriesName,
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

        return True

    def convert(self):

        self._getHeader()
        self._getComments()
        self._createNWBFile()
        self._createDevice()
        self._createElectrode()
        self._getClampMode()
        self._addStimulus()
        self._addAcquisition()

        with NWBHDF5IO(self.outputPath, "w") as io:
            io.write(NWBFile)

        return True


ABF1Converter(r"C:\NWB\Files\18426011.abf", r"C:\NWB\Files").convert()











