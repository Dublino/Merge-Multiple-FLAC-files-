# Merge-Multiple-FLAC-files-
FLAC Merge and Metadata Adjustment Script
This project is designed to merge multiple FLAC files into a single file, ensuring the correct metadata and total duration are maintained. The process involves re-encoding the FLAC files to WAV format, merging them, and then converting back to FLAC format.

Requirements
Python 3.x

ffmpeg

mutagen

Installation
**Before running the script**, make sure you have the required dependencies installed:

sh
sudo apt-get update
sudo apt-get install ffmpeg
pip3 install mutagen


**Configuration**
Create a config.yaml file with the following structure:

**yaml**
source_folder: "./input"
output_folder: "./output"
output_filename: "merged_file.flac"
source_folder: Path to the folder containing the source FLAC files.

output_folder: Path to the folder where the output file will be saved.

output_filename: Name of the merged output file.

**Usage**
Ensure the config.yaml file is correctly configured with the source and output folders.
Ensure the necessary permissions for the directories you're working with:

recommended sh
**sudo chmod -R 777 /path/to/source/folder
sudo chmod -R 777 /path/to/output/folder
**
Run the Python script using the following command with sudo to ensure it has the necessary permissions:

sh
sudo python3 merge_flac_files_with_metadata_dump.py
Script Flow
Re-encode FLAC to WAV:

The script reads the source FLAC files from the specified source_folder.

Each FLAC file is re-encoded to WAV format and saved in a temporary folder.

Durations of the re-encoded files are logged.

Create WAV List File:

A list file (wav_list.txt) is created, containing the paths to the re-encoded WAV files.

Merge WAV Files:

The script uses ffmpeg to concatenate the WAV files into a single WAV file (merged_file.wav).

Convert Merged WAV to FLAC:

The concatenated WAV file is converted back to FLAC format.

Adjust Metadata:

Metadata such as total_samples is adjusted to reflect the correct duration.

A metadata dump is created and added to the summary file.

Clean Temporary Files:

Temporary files created during the process are removed.

Log Summary:

A summary file (merge_summary.txt) is created in the output folder, logging the steps taken, durations, and metadata dump.

Output
Log File: merge_flac_files.log in the same directory where the script is run.

Summary File: merge_summary.txt in the output folder specified in config.yaml.

Merged FLAC File: The final merged FLAC file saved in the output folder.

Example
source_folder: "./input"
output_folder: "./output"
output_filename: "merged_file.flac"
Place your FLAC files in the ./input folder.

Run the script.

Check the ./output folder for the merged FLAC file and summary file.
