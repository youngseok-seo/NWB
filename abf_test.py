import pyabf
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

infile = "/Users/youngseo/Documents/Research/NWB/data/abf1/19122043.abf"
abf = pyabf.ABF(infile)

print(abf.headerText)

# path = r"/Users/youngseo/Documents/Research/nwb/Files/allen_nwb2/H19_29_150_11_21_01_0001.abf"

# abf = pyabf.ABF("/Users/youngseo/Documents/Research/nwb/18426011.abf")
# "../White_noise/Human_tissue/Epilepsy cases/Apr 17, 2018/Cell 2/Gain 40/18417017.abf"

# root, ext = os.path.splitext(path)

# abf = pyabf.ABF(path)

# print(abf.abfVersion["major"])
# abf.getInfoPage().generateHTML(saveAs=root + ".html")

# print(abf)
# print('this is header: ' + abf.headerText)

# inputFileName = os.path.basename(path)
# inputFileNo = os.path.splitext(inputFileName)
#
# print(inputFileNo[0])


# abf.setSweep(12)
#
# print("sweep data (ADC):", abf.sweepY)
# print("sweep command (DAC):", abf.sweepC)
# print("sweep times (seconds):", abf.sweepX)


# plot different sweeps
# plt.figure(figsize=(7, 5))
# plt.ylabel(abf.sweepLabelY)
# plt.xlabel(abf.sweepLabelX)
# for i in range(0,30,5):
#     abf.setSweep(i)
#     plt.plot(abf.sweepX, abf.sweepY, alpha=.5, label="sweep %d"%(i))
# plt.legend()
# plt.show()

# print(len(abf.tagComments))  # each .abf file seems to have 2 to 3 comments which appear to be identical
# print(abf.tagComments)


# Determine whether .abf file is v1 or v2
# f = open("18426011.abf", 'rb')
# byteString = f.read(16)
# f.close()
#
# print(byteString)

# print(abf.abfVersion["major"])

