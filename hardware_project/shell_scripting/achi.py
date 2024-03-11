#!/bin/bash

# Archive the input file to a predefined location

# check exactly one input file was given

if [ $# -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit 1
fi

# The archive location
ARCHIVE_DIR="/home/vx/Desktop/hardware_project/20_videos/archives"

# Ensure the archive location exists

if [ ! -d $ARCHIVE_DIR ]; then
    echo "Creating $ARCHIVE_DIR"
    mkdir -p $ARCHIVE_DIR
fi

# Copy the input file to the archive location
cp -r $1 $ARCHIVE_DIR

# Print the result
echo "Archived $1 to $ARCHIVE_DIR"
