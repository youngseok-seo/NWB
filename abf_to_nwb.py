import os
import sys
from datetime import datetime
from ABF1Converter import ABF1Converter

def abf_to_nwb(inputPath, outFolder):

    """
    Takes the path to the ABF v1 file(s) as the first command line argument and writes the corresponding NWB file(s)
    to the folder specified by the second command line argument

    """

    if not os.path.exists(inputPath):
        raise ValueError(f"The file or folder {inputPath} does not exist.")

    if not os.path.exists(outFolder):
        raise ValueError(f"The file or folder {outFolder} does not exist.")

    # The input path is a single file
    # if os.path.isfile(inputFileorFolder):
    #
    #     fileName = os.path.basename(inputFileorFolder)
    #     root, ext = os.path.splitext(fileName)
    #
    #     print(f"Converting {fileName}...")
    #
    #     abf = pyabf.ABF(inputFileorFolder)
    #     if abf.abfVersion["major"] != 1:
    #         raise ValueError(f"The ABF version for the file {inputFileorFolder} is not supported.")
    #
    #     if ext != ".abf":
    #         raise ValueError(f"The extension {ext} is not supported.")
    #
    #     outFile = os.path.join(outFolder, root + ".nwb")
    #
    #     if os.path.exists(outFile):
    #         raise ValueError(f"The file {outFile} already exists.")
    #
    #     ABF1Converter(inputFileorFolder, outFile).convert()
    #     print(f"{fileName} was successfully converted to {outFile}.")

    # The input path is a folder or directory
    if not os.path.isdir(inputPath):

        raise ValueError("Invalid path: input must be a path to a folder or a directory")

    elif "Cell *" in inputPath.split(r"\|/")[:-1]:

        raise ValueError("Invalid path: input must be or lead to a Cell folder.")

    else:

        date = ""
        for dirpath, dirnames, filenames in os.walk(inputPath):

            # Create NWB file for each cell (YYYY.MM.DD.C#.nwb)
            cells = [s for s in dirnames if "Cell" in s]
            for cell in cells:

                cellFolder = os.path.join(dirpath, cell)

                # Create uniform datetime object for file name consistency
                dateStr = os.path.split(dirpath)[-1]
                failCount = 0
                for fmt in ["%B %d, %Y", "%b %d, %Y"]:
                    try:
                        dt = datetime.strptime(dateStr, fmt)
                    except:
                        failCount += 1
                        pass

                if failCount > 1:
                    raise ValueError("The file hierarchy is not compatible: date must be present.")

                date = str(dt.date())


                cellNumber = cell[5:]

                outFile = os.path.join(outFolder, date + "-" + f"C{cellNumber}" + ".nwb")

                if os.path.exists(outFile):
                    raise ValueError(f"The file {outFile} already exists.")

                ABF1Converter(cellFolder, outFile).convert()

    return True


def main():

    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    abf_to_nwb(inputPath, outputPath)


main()
