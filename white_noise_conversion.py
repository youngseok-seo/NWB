import sys
from os import walk
from os.path import join
import glob
import pyabf
# import re
from datetime import datetime
import numpy as np
import pandas as pd
from pynwb import NWBFile, NWBHDF5IO
from pynwb.icephys import CurrentClampStimulusSeries
from pynwb.icephys import CurrentClampSeries


rootFolder = sys.argv[1]
print("Root folder: " + rootFolder)

# ATTEMPTED TO COLLECT METADATA FROM TAG COMMENTS IN THE ABF FILES BUT METHOD WAS DISCARDED DUE TO DATA INCONSISTENCY

# Collect and load .abf files
# abfFiles = []
# for dirpath, dirnames, filenames in walk(rootFolder):
#     if len(dirnames) == 0 and len(glob.glob(dirpath + '/*.abf')) != 0:
#         abfFilesPaths = glob.glob(dirpath + '/*.abf')
#         for path in abfFilesPaths:
#             abfFiles += [path]
#
# successFiles = []
# failedFiles = []
# failCount = 0
# for file in abfFiles:
#     try:
#         successFiles += [pyabf.ABF(file)]
#     except:
#         failCount += 1
#         failedFiles += [file]

# for file in failedFiles:
#     print(file)
#
# print("Number of files loaded: " + str(len(successFiles)))
# print("Number of files which failed to load: " + str(failCount))
# print("Total files: " + str(len(abfFiles)))

# Collect metadata from tag comments
# for abfFile in successFiles:
#     comment = (abfFile.tagComments)
# if len(comment) != 0:
#     tags = re.split(' ; |, |; ', comment[0])
#     layer = [s for s in tags if ("L" or "l") in s]
#
#     print(str(layer[0])[-1])
# print(comment)


# Create an NWB file for each cell

cells = []
for dirpath, dirnames, filenames in walk(rootFolder):

    cells = [s for s in dirnames if "Cell" in s]
    if len(cells) != 0:

        for cell in cells:

            path = dirpath + '/' + cell
            sessionDate = datetime.strptime(dirpath.split('/')[4], "%b %d, %Y")

            nwbFile = NWBFile(session_description=(str(sessionDate) + " - " + cell),
                              session_start_time=sessionDate,
                              identifier=cell,
                              # file_create_date=datetime.date.today,
                              experiment_description=(sys.argv[1].split('/')[-2] + ", " + sys.argv[1].split('/')[-1]),
                              experimenter='HM',
                              lab='Valiante Laboratory',
                              institution='Univ. of Toronto',
                              protocol=(sys.argv[1].split('/')[0]),
                              )

            nwbFile.add_trial_column(name='Stimulus', description='Stimulus data')
            nwbFile.add_trial_column(name='Acquisition', description='Acquisition data')
            nwbFile.add_trial_column(name='CellNo', description='Cell Number')
            nwbFile.add_trial_column(name='RMP', description='Resting Memory Potential')
            nwbFile.add_trial_column(name='Layer', description='Layer')
            nwbFile.add_trial_column(name='Tau', description='Tau value')
            nwbFile.add_trial_column(name='Gain', description='Gain value')
            nwbFile.add_trial_column(name='DC', description='DC')
            nwbFile.add_trial_column(name='Date', description='Date Recorded')

            # create a new device
            device = nwbFile.create_device(name='Clampfit')

            # create a new electrode
            elec = nwbFile.create_ic_electrode(
                name="elec0", slice='', resistance='', seal='', description='',
                location='', filtering='', initial_access_resistance='', device=device)

            start = 0
            end = 1

            for dpath, dnames, fnames in walk(path):

                if len(dnames) == 0 and len(glob.glob(dpath + '/*.xlsx')) != 0:
                    xlsFilePath = dpath + '/*.xlsx'
                    xlsFiles = glob.glob(xlsFilePath)

                    for i in range(len(xlsFiles)):
                        # print("File: " + file)

                        # Collect metadata from the "Tags" column found in .xlsx files
                        metadataFile = pd.read_excel(xlsFiles[i], index_col=1)
                        tagData = metadataFile.iloc[0]['Tags'].split(', ')


                        if len(tagData) == 6:
                            cellNo = tagData[0]
                            rmp = tagData[1]
                            layer = tagData[2]
                            tau = tagData[3]
                            gain = tagData[4]
                            dc = tagData[5]

                        # Special case for files with inconsistent tag comments
                        else:
                            cellNo = tagData[0]
                            rmp = tagData[1][1:13]
                            layer = tagData[1][14:16]
                            tau = tagData[2]
                            gain = tagData[3]
                            dc = tagData[4]

                        metadata = {
                            'Cell No.': cellNo,
                            'Session Date': sessionDate,
                            'RMP': rmp,
                            'Layer': layer,
                            'Tau': tau,
                            'Gain': gain,
                            'DC': dc
                        }

                        # Access sweep data in the ABF files
                        abfFiles = glob.glob(dpath + '/*.abf')
                        abfFile = pyabf.ABF(abfFiles[i])
                        sweepADC = abfFile.sweepY
                        sweepDAC = abfFile.sweepC

                        # Create time series

                        stimulus = CurrentClampStimulusSeries(
                            name="ccss", data=sweepADC, unit='pA', electrode=elec,
                            rate=10e4, gain= float(metadata['Gain'][5:8])  , starting_time=0.0, description='DC%s' % dc)

                        acquisition = CurrentClampSeries(
                            name='ccs', data=sweepDAC, electrode=elec,
                            unit='mV', rate=10e4,
                            gain=0.00, starting_time=0.0,
                            bias_current=np.nan, bridge_balance=np.nan, capacitance_compensation=np.nan)

                        nwbFile.add_trial(start_time=float(start),
                                          stop_time=float(end),
                                          Stimulus=stimulus,
                                          Acquisition=acquisition,
                                          CellNo=metadata['Cell No.'],
                                          RMP=metadata['RMP'],
                                          Layer=metadata['Layer'],
                                          Tau=metadata['Tau'],
                                          Gain=metadata['Gain'],
                                          DC=metadata['DC'],
                                          Date=metadata['Session Date']
                                          )

                        start += 1
                        end += 1

            output = sys.argv[2]
            io = NWBHDF5IO(join(output, str(sessionDate) + ' - ' + metadata['Cell No.'] + '.nwb'), mode='w')
            io.write(nwbFile)
            io.close()
            print("Success")






















