import os
import sys
import glob
import pandas as pd
from datetime import datetime
from ABF1Converter import ABF1Converter

def abf_to_nwb(inputPath, outFolder):

    """
    Takes the path to the ABF v1 file(s) as the first command line argument and writes the corresponding NWB file(s)
    to the folder specified by the second command line argument.

    NWB Files organized by cell, with assumption that each abf file corresponds to each cell

    Reads data from a spreadsheet and writes important metadata to a CSV file

    """

    if not os.path.exists(inputPath):
        raise ValueError(f"The file or folder {inputPath} does not exist.")

    if not os.path.isdir(inputPath) and not os.path.isfile(inputPath):

        raise ValueError("Invalid path: input must be a path to a file or a directory")

    if not os.path.exists(outFolder):
        raise ValueError(f"The file or folder {outFolder} does not exist.")

    # The input path is a file

    if os.path.isfile(inputPath):

        fileName = os.path.basename(inputPath)
        root, ext = os.path.splitext(fileName)

        print(f"Converting {fileName}...")

        outFile = os.path.join(outFolder, root + ".nwb")

        if os.path.exists(outFile):
            raise ValueError(f"The file {outFile} already exists.")

        ABF1Converter(inputPath, outFile).convert()

    # The input path is a folder or directory

    elif os.path.isdir(inputPath):

        files = glob.glob(inputPath + "/*.abf")

        # Parse excel spreadsheet to gather date information

        excel = r"C:\NWB\Files\Data\Step\Demographic information Feb-05-2019-_Request_HM.xlsx"
        metaSheet = pd.read_excel(excel, sheet_name='L23-cells', header=3, usecols='B:G', nrows=8)
        dates = {}
        for col in metaSheet.columns:
            colList = metaSheet[col].tolist()
            dates[f"{col.date()}"] = colList

        for file in files:

            fileName = os.path.basename(file)
            root, ext = os.path.splitext(fileName)

            for date, files in dates.items():
                for i in range(len(files)):
                    if files[i] == fileName:
                        expDate = date

            print(f"Converting {fileName}...")

            outFile = os.path.join(outFolder, expDate + "-C" + root[-3:] + ".nwb")

            if os.path.exists(outFile):
                raise ValueError(f"The file {outFile} already exists.")

            ABF1Converter(inputPath, outFile).convert()

        # date = ""
        # for dirpath, dirnames, filenames in os.walk(inputPath):

            # Create NWB file for each cell ABF file
            # cells = [s for s in dirnames if "Cell" in s]
            # for cell in cells:
            #
            #     cellFolder = os.path.join(dirpath, cell)
            #
            #     # Create uniform datetime object for file name consistency
            #     dateStr = os.path.split(dirpath)[-1]
            #     failCount = 0
            #     for fmt in ["%B %d, %Y", "%b %d, %Y"]:
            #         try:
            #             dt = datetime.strptime(dateStr, fmt)
            #         except:
            #             failCount += 1
            #             pass
            #
            #     if failCount > 1:
            #         raise ValueError("The file hierarchy is not compatible: date must be present.")
            #
            #     date = str(dt.date())
            #
            #     cellNumber = cell[5:]

                # Create an NWB v2 file (MM-DD-YY-C#.nwb)
                # outFile = os.path.join(outFolder, date + "-" + f"C{cellNumber}" + ".nwb")
                #
                # if os.path.exists(outFile):
                #     raise ValueError(f"The file {outFile} already exists.")
                #
                # ABF1Converter(cellFolder, outFile).convert()



    return True


def main():

    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    abf_to_nwb(inputPath, outputPath)


main()
