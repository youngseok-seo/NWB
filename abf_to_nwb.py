import os
import sys
import glob
import pyabf
from ABF1Converter import ABF1Converter

def abf_to_nwb(inputFileorFolder, outFolder):

    """
    Takes the path to the ABF v1 file(s) as the first command line argument and writes the corresponding NWB file(s)
    to the folder specified by the second command line argument

    """

    if not os.path.exists(inputFileorFolder):
        raise ValueError(f"The file or folder {inputFileorFolder} does not exist.")

    if not os.path.exists(outFolder):
        raise ValueError(f"The file or folder {outFolder} does not exist.")

    # The input path is a file
    if os.path.isfile(inputFileorFolder):

        fileName = os.path.basename(inputFileorFolder)
        root, ext = os.path.splitext(fileName)

        print(f"Converting {fileName}...")

        abf = pyabf.ABF(inputFileorFolder)
        if abf.abfVersion["major"] != 1:
            raise ValueError(f"The ABF version for the file {inputFileorFolder} is not supported.")

        if ext != ".abf":
            raise ValueError(f"The extension {ext} is not supported.")

        outFile = os.path.join(outFolder, root + ".nwb")

        ABF1Converter(inputFileorFolder, outFile).convert()
        print(f"{filename} was successfully converted to {outFile}.")


    # The input path is a folder or directory
    elif os.path.isdir(inputFileorFolder):

        for dirpath, dirnames, filenames in os.walk(inputFileorFolder):

            if len(dirnames) == 0 and len(glob.glob(dirpath + "/*.abf")) != 0:

                files = glob.glob(dirpath + "/*.abf")

                for file in files:

                    fileName = os.path.basename(file)
                    root, ext = os.path.splitext(fileName)

                    print(f"Converting {fileName}...")

                    abf = pyabf.ABF(file)
                    if abf.abfVersion["major"] != 1:
                        raise ValueError(f"The ABF version for the file {file} is not supported.")

                    if ext != ".abf":
                        raise ValueError(f"The extension {ext} is not supported.")

                    outFile = os.path.join(outFolder, root + ".nwb")

                    ABF1Converter(file, outFile).convert()
                    print(f"{fileName} was successfully converted to {outFile}.")

    else:
        print("Conversion failed.")

def main():

    input = sys.argv[1]
    output = sys.argv[2]
    abf_to_nwb(input, output)

main()