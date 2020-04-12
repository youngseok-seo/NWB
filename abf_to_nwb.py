#!/bin/env python

import os
import sys
import glob
import argparse

from ABF1Converter import ABF1Converter


def abf_to_nwb(inputPath, outFolder, outputMetadata, acquisitionChannelName, stimulusChannelName, overwrite):
    """
    Sample file handling script for NWB conversion.

    Takes the path to the ABF v1 file as the first command line argument and writes the corresponding NWB file
    to the folder specified by the second command line argument.

    NWB Files organized by cell, with assumption that each abf file corresponds to each cell
    """

    if not os.path.exists(inputPath):
        raise ValueError(f"The file or folder {inputPath} does not exist.")

    if not os.path.exists(outFolder):
        raise ValueError(f"The file or folder {outFolder} does not exist.")

    if os.path.isfile(inputPath):
        files = [inputPath]
    elif os.path.isdir(inputPath):
        files = glob.glob(inputPath + "/*.abf")
    else:
        raise ValueError(f"Invalid path {inputPath}: input must be a path to a file or a directory")

    if len(files) == 0:
        raise ValueError(f"Invalid path {inputPath} does not contain any ABF files.")

    for inputFile in files:

        fileName = os.path.basename(inputFile)
        root, _ = os.path.splitext(fileName)

        print(f"Converting {fileName}...")

        outFile = os.path.join(outFolder, root + ".nwb")

        if os.path.exists(outFile):
            if overwrite:
                os.unlink(outFile)
            else:
                raise ValueError(f"The file {outFile} already exists.")

        conv = ABF1Converter(inputFile, outFile, acquisitionChannelName=acquisitionChannelName, stimulusChannelName=stimulusChannelName)
        conv.convert()

        if outputMetadata:
            conv._outputMetadata()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--acquisitionChannelName", default=None,
                        help="Output only the given acquisition channel.")
    parser.add_argument("--stimulusChannelName", default=None,
                        help="Output only the given stimulus channel.")
    parser.add_argument("--outputPath", default=".",
                        help="Output path for the nwb files.")
    parser.add_argument("--outputMetadata", action="store_true", default=False,
                        help="Helper for debugging which outputs HTML files with the metadata contents of the files.")
    parser.add_argument("--overwrite", action="store_true", default=False,
                        help="Overwrite output files.")
    parser.add_argument("fileOrFolder", help="ABF file/folder  to convert.")

    args = parser.parse_args()

    abf_to_nwb(args.fileOrFolder, args.outputPath, outputMetadata=args.outputMetadata,
               acquisitionChannelName=args.acquisitionChannelName,
               stimulusChannelName=args.stimulusChannelName, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
