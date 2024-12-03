import os
import yaml
import subprocess
import logging
import mutagen
from mutagen.flac import FLAC

# Setup logging to write to a file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("merge_flac_files.log"), logging.StreamHandler()])

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def reencode_to_wav(source_folder, temp_folder):
    flac_files = sorted([f for f in os.listdir(source_folder) if f.endswith('.flac')], key=lambda x: int(x.split()[0]))
    total_duration = 0
    summary_details = []
    for file_name in flac_files:
        input_file = os.path.join(source_folder, file_name)
        output_file = os.path.join(temp_folder, f"{file_name}.wav")
        logging.info(f"Re-encoding {input_file} to {output_file}")
        try:
            subprocess.run(['ffmpeg', '-i', input_file, output_file], check=True)
            audio = mutagen.File(output_file)
            duration = audio.info.length
            total_duration += duration
            logging.info(f"Re-encoded {output_file} - Duration: {duration} seconds")
            summary_details.append(f"Re-encoded {output_file} - Duration: {duration} seconds")
        except subprocess.CalledProcessError as e:
            logging.warning(f"Failed to re-encode {input_file}: {e}")
            summary_details.append(f"Failed to re-encode {input_file}: {e}")
        except Exception as e:
            logging.warning(f"Failed to get duration of {output_file}: {e}")
            summary_details.append(f"Failed to get duration of {output_file}: {e}")
    logging.info(f"Total duration of re-encoded files: {total_duration} seconds")
    summary_details.append(f"Total duration of re-encoded files: {total_duration} seconds")
    return summary_details, total_duration

def create_wav_list(temp_folder, list_file):
    temp_files = sorted([f for f in os.listdir(temp_folder) if f.endswith('.wav')], key=lambda x: int(x.split()[0]))
    with open(list_file, 'w') as file:
        for file_name in temp_files:
            file_path = os.path.join(temp_folder, file_name)
            logging.info(f"Adding {file_path} to list")
            file.write(f"file '{file_path}'\n")
    logging.info(f"Created list file with {len(temp_files)} entries")

def merge_wav_files(list_file, output_file):
    logging.info(f"Merging files listed in {list_file} to {output_file}")
    try:
        subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', output_file], check=True)
        audio = mutagen.File(output_file)
        duration = audio.info.length
        logging.info(f"Merged file duration: {duration} seconds")
        return duration
    except subprocess.CalledProcessError as e:
        logging.warning(f"Failed to merge files: {e}")
        return f"Failed to merge files: {e}"
    except Exception as e:
        logging.warning(f"Failed to get duration of merged file: {e}")
        return f"Failed to get duration of merged file: {e}"

def convert_wav_to_flac(input_file, output_file):
    logging.info(f"Converting {input_file} to FLAC format as {output_file}")
    try:
        subprocess.run(['ffmpeg', '-i', input_file, '-c:a', 'flac', output_file], check=True)
        audio = FLAC(output_file)
        duration = audio.info.length
        logging.info(f"Converted file duration: {duration} seconds")
        return duration
    except subprocess.CalledProcessError as e:
        logging.warning(f"Failed to convert {input_file} to FLAC: {e}")
        return f"Failed to convert {input_file} to FLAC: {e}"
    except Exception as e:
        logging.warning(f"Failed to get duration of converted file: {e}")
        return f"Failed to get duration of converted file: {e}"

def metadata_dump(output_file):
    try:
        audio = FLAC(output_file)
        metadata_info = audio.pprint()
        logging.info(f"Metadata dump for {output_file}: {metadata_info}")
        return metadata_info
    except Exception as e:
        logging.warning(f"Failed to dump metadata for {output_file}: {e}")
        return f"Failed to dump metadata: {e}"

def clean_temp_files(temp_folder):
    for file_name in os.listdir(temp_folder):
        if file_name.endswith('.wav'):
            file_path = os.path.join(temp_folder, file_name)
            logging.info(f"Removing temporary file {file_path}")
            try:
                os.remove(file_path)
            except OSError as e:
                logging.warning(f"Failed to remove {file_path}: {e}")

def write_summary(summary_file, details):
    with open(summary_file, 'w') as file:
        for detail in details:
            file.write(detail + "\n")
    logging.info(f"Summary written to {summary_file}")

def main(config_path):
    config = load_config(config_path)
    source_folder = os.path.abspath(config['source_folder'])
    output_folder = os.path.abspath(config['output_folder'])
    output_filename = config['output_filename']
    summary_file = os.path.join(output_folder, 'merge_summary.txt')
    temp_folder = os.path.join(source_folder, 'temp')
    os.makedirs(temp_folder, exist_ok=True)
    list_file = os.path.join(temp_folder, 'wav_list.txt')
    wav_output_file = os.path.join(temp_folder, 'merged_file.wav')
    flac_output_file = os.path.join(output_folder, output_filename)

    # Re-encode FLAC to WAV
    summary_details, total_duration = reencode_to_wav(source_folder, temp_folder)

    # Create WAV list file
    create_wav_list(temp_folder, list_file)

    # Merge WAV files
    merge_duration = merge_wav_files(list_file, wav_output_file)
    summary_details.append(f"Merged WAV file duration: {merge_duration} seconds")

    # Convert merged WAV to FLAC
    final_duration = convert_wav_to_flac(wav_output_file, flac_output_file)
    summary_details.append(f"Final FLAC file duration: {final_duration} seconds")

    clean_temp_files(temp_folder)

    # Remove the list file
    try:
        os.remove(list_file)
    except OSError as e:
        logging.warning(f"Failed to remove {list_file}: {e}")

    # Remove the temp folder
    try:
        os.rmdir(temp_folder)
    except OSError as e:
        logging.warning(f"Failed to remove {temp_folder}: {e}")

    # Add metadata dump to summary
    metadata_info = metadata_dump(flac_output_file)
    summary_details.append(f"Metadata dump for {flac_output_file}: {metadata_info}")
    summary_details.append(f"Expected duration: {total_duration} seconds")

    logging.info("Process completed.")
    summary_details.append("Process completed.")
    write_summary(summary_file, summary_details)

if __name__ == "__main__":
    main('config.yaml')
