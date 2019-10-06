import os
import sys
import glob
import pandas as pd
import csv
from datetime import datetime
from ABF1Converter import ABF1Converter

def abf_to_nwb(inputPath, outFolder):

    """
    Sample file handling script for NWB conversion.

    Takes the path to the ABF v1 file as the first command line argument and writes the corresponding NWB file
    to the folder specified by the second command line argument.

    NWB Files organized by cell, with assumption that each abf file corresponds to each cell

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

        for file in files:

            fileName = os.path.basename(file)
            root, ext = os.path.splitext(fileName)

            print(f"Converting {fileName}...")

            outFile = os.path.join(outFolder, root + ".nwb")

            if os.path.exists(outFile):
                raise ValueError(f"The file {outFile} already exists.")

            ABF1Converter(inputPath, outFile).convert()

    return True


def main():

    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    abf_to_nwb(inputPath, outputPath)


main()
