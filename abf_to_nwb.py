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

        self.header = self.abf.headerText

        return self.header

    def _getComments(self):

        self.comments = self.abf.tagComments

        return self.comments

    def _createNWBFile(self):

        # Create a shell NWB2 file

        self.start_time = self.abf.abfDateTime
        self.inputFileName = os.path.basename(self.inputFilePath)
        self.inputFileNo = os.path.splitext(self.inputFileName)

        self.NWBFile = NWBFile(
            session_description= "include Cell number and patient condition, from json?",
            session_start_time=self.start_time,
            identifier=self.inputFileNo,
            file_create_date= datetime.today(),
            experimenter='HM',
            lab='Valiante Laboratory',
            institution='University of Toronto',
            notes=self.comments
        )
        return self.NWBFile

    def _createDevice(self):

        self.device = self.NWBFile.create_device(name='Clampfit')

    def _createElectrode(self):

        self.electrode = self.NWBFile.create_ic_electrode(name='elec0', device=self.device)

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
            raise ValueError(f"{unit} is not a valid unit.")

    def _getClampMode(self, channel):

        return self.abf._adcSection.nTelegraphEnable[channel] # Allen runs this fn inside the for loop which loops through within each sweep. how do we get our clamp mode data?
        # would run inside stim/response

    def _addStimulus(self):

        # Determine the correct stimulus class for the given clamp mode (V = 0; I = 1)

        for i in range(self.abf.sweepCount):

            #determine whether we need to go through different channels - header only has 1

            if clampMode == 0:
                stimulusClass = VoltageClampStimulusSeries # figure out how to get access to clamp mode in abfheader and ues that as input, not arg
            elif clampMode == 1:
                stimulusClass = CurrentClampStimulusSeries

            self.abf.setSweep(i)
            seriesName = "Index_{number: 0{math.ceil(math.log(total, 10))}d}" + str(i)
            data = self.abf.sweepC
            unit, conversion = self._unitConversion(self.abf.sweepUnitsC)
            electrode = self.electrode
            gain = None # get from json file? tag comments too unreliable
            resolution = np.nan
            starting_time = self.start_time
            rate = self.abf.dataRate
            description = None # make a json file? is this necessary?

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

    def _addAcquisition(self, clampMode):

        for i in range(self.abf.sweepCount):

            if clampMode == 0:
                acquisitionClass = VoltageClampSeries  # figure out how to get access to clamp mode in abfheader and ues that as input, not arg
            elif clampMode == 1:
                acquisitionClass = CurrentClampSeries

            self.abf.setSweep(i)
            seriesName = "Index_{number: 0{math.ceil(math.log(total, 10))}d}" + str(i)
            data = self.abf.sweepY
            unit, conversion = self._unitConversion(self.abf.sweepUnitsY)
            electrode = self.electrode
            gain = None  # get from json file? tag comments too unreliable
            resolution = np.nan
            starting_time = self.start_time
            rate = self.abf.dataRate
            description = None  # make a json file? is this necessary?

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
                                     description=description
                                     )

            self.NWBFile.add_acquisition(acquisition)

        return True

    def convert(self):

        self._getHeader()
        self._getComments()
        self._createNWBFile()
        self._createDevice()
        self._createElectrode()
        self._addStimulus()
        self._addAcquisition()

        with NWBHDF5IO(self.outputPath, "w") as io:
            io.write(NWBFile)

        return True














