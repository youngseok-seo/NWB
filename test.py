# -*- coding: utf-8 -*-

import os
import sys
import glob
import csv
from datetime import datetime
import pyabf
import numpy as np
from pynwb import NWBFile, NWBHDF5IO
import pandas as pd

# rootFolder = sys.argv[1]
# print('root folder: ' + rootFolder)
#
# cnt = 0

# rootFolder = r"C:\NWB\Files\NWB Files\18129006.nwb"
# newroot = os.path.join(rootFolder, "new")
# print(newroot)

# abf = pyabf.ABF(rootFolder)
# print(abf.headerText)
# for dirpath, dirnames, filenames in os.walk(rootFolder):
#     cell_paths = [s for s in dirnames if "Cell" in s]
#     for cell in cell_paths:
#         print(cell)
#
#         for format in ["%B %d, %Y", "%b %d, %Y"]:
#             try:
#                 x = datetime.strptime(os.path.split(dirpath)[-1], format)  # dirpath gives up to the date
#                 # print(str(x.year) + "_" + str(x.month) + "_" + str(x.day))
#                 print(x.date())
#             except:
#                 pass
        # print(dirnames)  # dirnames is str list of cell names

    # print(cell_paths)

# excel = r"C:\NWB\Files\Data\Step\Demographic information Feb-05-2019-_Request_HM.xlsx"
# metaSheet = pd.read_excel(excel, sheet_name='Layer 5- cells', header=2, nrows=12)
# print(metaSheet['12/11/2013'])
# dates = {}
# for col in metaSheet.columns:
#     colList = metaSheet[col].tolist()
#     dates[f"{col}"] = colList
#
# print(dates)
#
# for date, file in dates.items():
#     for i in range(len(file)):
#         if file[i] == "19122017.abf":
#             print(date)
#
# with open(r"C:\NWB\Files\Data\Step\metadata.csv", 'a') as csvFile:
#     writer = csv.writer(csvFile)
#     writer.writerow(['1', '2', '3', '4', '5'])
#
# csvFile.close()


# base = path.basename(r"C:\NWB\Files\Human_tissue\Epilepsy cases\April 26, 2018\Cell 1\Gain 40\18426013.abf")
# fileno, ext = path.splitext(base)
# print(base)


# x = [r"C:\NWB\Files\18426011.abf", r"C:\NWB\Files\19516004.abf"]
# x.sort(key=lambda y: path.basename(y))
# print(x)



# # Enter desired rootFolder as command line argument
# rootFolder = sys.argv[1]
# print('Starting at: '+ rootFolder)
#
# dirs = [rootFolder]

# for (dirpath, dirnames, filenames) in walk(dirs[0]):
#
#     if len(dirnames) == 0 and len(glob.glob(dirpath +'/*.xlsx'))!=0:
#         print('Current directory: ' + dirpath)
#         xlsFilePath = dirpath + '/*.xlsx'
#         xlsFiles = glob.glob(xlsFilePath)
#
#         for file in xlsFiles:
#             # Collecting Recording Date and Cell No. from the directory names
#             # ***sample path: '../White_noise/Human_tissue/Epilepsy cases/April 17, 2018/Cell 5/Gain 40'***
#             dirData = dirpath.split('/')
#
#             recordingDate = datetime.strptime(dirData[4], "%B %d, %Y")
#             cellNo = dirData[5]
#
#             print(recordingDate)
#
#             # Collecting metadata from the "Tags" column found in .xlsx files
#             metaDataFile = pd.read_excel(file, index_col=1)
#             tagData = metaDataFile.iloc[0]['Tag'].split(',')
#
#             rmp = tagData[1][7:]
#             print(rmp)




# fpath = file_path; f = cell_id
#
 # Load up abf file
# print('Loading %s ...' % cell_id)
# h = {}
# si = {}  # sampling intervals for each cell in us
# d = {}
# V = {}
# I = {}
#
# a = nio.AxonIO(filename=fpath)
# bl = bl = a.read_block(lazy=False, signal_group_mode='split-all', units_group_mode='split-all')
# # - .segments represent sweeps (one segment = one sweep)
# # - .analogsignals for each segment: numpy array of voltage recordings and current input,
# #   length of recording block, and sampling rate
# iclamp = 0  # channel 4 as voltage channel
# current_in = 1  # channel 14 as command channel
# V[f] = []  # numpy array of voltage recordings for all sweeps/segments - rows = sweeps, columns = data
# for i in range(0, len(bl.segments)):
#     a = bl.segments[i].analogsignals[iclamp].__array__().tolist()
#     V[f].append([item for x in a for item in x])
# V[f] = np.array(V[f])
# I[f] = []  # numpy array of stimulus for all sweeps/segments - rows = sweeps, columns = data
# for i in range(0, len(bl.segments)):
#     a = bl.segments[i].analogsignals[current_in].__array__().tolist()
#     I[f].append([item for x in a for item in x])
# I[f] = np.array(I[f])
#
# # save data block for each cell
# d[f] = bl
#
#
# # ----------------------------------------------------------------------------------------------------------------------
# # Create the NWB file
# # ----------------------------------------------------------------------------------------------------------------------
#
# nwbfile = NWBFile(session_description = ('Cell #'+ cell_number),
#                   session_start_time = date,
#                   source = '',
#                   identifier = cell_id,
#                   file_create_date = date,
#                   experiment_description=(species + ' ' + experiment_condition + ' ' + cell_type),
#                   experimenter='HM',
#                   lab='Valiante Laboratory',
#                   institution='Univ. of Toronto',
#                   protocol = protocol,
#                   notes = ('RMP Offset: ' + offset)
#                   )
#
# # create a new device
# device = nwbfile.create_device(name='Clampfit', source='N/A')
#
# # create a new electrode
# elec = nwbfile.create_ic_electrode(
#     name="elec0", source='', slice='', resistance='', seal='', description='',
#     location='', filtering='', initial_access_resistance='', device=device)
#
#
# ## Current clamp stimulus data
# from pynwb.icephys import CurrentClampStimulusSeries
#
# ccss = CurrentClampStimulusSeries(
#     name="ccss", source="command", data=I[f], unit='pA', electrode = elec,
#     rate=10e4, gain=gain, starting_time=0.0, description='DC%s' % dc)
#
# nwbfile.add_stimulus(ccss)
#
# ## Current Clamp Response data
# from pynwb.icephys import CurrentClampSeries
#
# ccs = CurrentClampSeries(
#     name='ccs', source='command', data=V[f], electrode = elec,
#     unit='mV', rate=10e4,
#     gain=0.00, starting_time=0.0,
#     bias_current=np.nan, bridge_balance=np.nan, capacitance_compensation=np.nan)
#
# nwbfile.add_acquisition(ccs)
#
# # after adding all data,
# # write data to NWBFile
#
# io = NWBHDF5IO(output_path+'%s.nwb' % f, 'w')
# io.write(nwbfile)
# io.close()
