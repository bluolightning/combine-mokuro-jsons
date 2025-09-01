# Processes all json files in the directory to produce one or more text files with all the Japanese text.
import json
import re
import os
import collections

# --- Configuration ---

# SET THIS FLAG to control the output behavior.
# If True:  Creates a separate .txt file for each volume (e.g., "Volume 01.txt", "Volume 02.txt").
#           A "volume" is assumed to be the parent directory of the .json files.
# If False: Creates a single, consolidated file with text from all volumes,
#           sorted by volume name.
CREATE_FILE_PER_VOLUME = True

# The name of the output file IF CREATE_FILE_PER_VOLUME is False.
# This file will be created in the directory where you run the script.
OUTPUT_FILENAME = "combined_japanese_text.txt"


# --- Main Script ---

def contains_japanese(text):
    """
    Checks if a string contains any Japanese characters
    (Hiragana, Katakana, or Kanji).
    """
    # Unicode ranges for Japanese characters:
    # \u3040-\u309F: Hiragana
    # \u30A0-\u30FF: Katakana
    # \u4E00-\u9FFF: CJK Unified Ideographs (Kanji)
    return re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text)

def process_files():
    """
    Main function to find all .json files in the current directory and all subdirectories,
    extract text, and write to an output file (or files).
    """
    # Use a dictionary to store lines per volume. This allows us to group text
    # by its source directory. e.g., {'Volume 01': ['line 1', 'line 2'], 'Volume 02': ['line 3']}
    volume_data = collections.defaultdict(list)

    # Find all .json files by walking through the directory tree.
    json_filepaths = []
    print("Finding all .json files in the current directory and subdirectories...")
    for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.json'):
                # Construct the full path (e.g., 'Volume 01/00001.json') and add it to our list.
                full_path = os.path.join(dirpath, filename)
                json_filepaths.append(full_path)

    try:
        # Sort the list to process files in a predictable order (e.g., Volume 01, Volume 02...)
        json_filepaths.sort()

        if not json_filepaths:
            print("No .json files were found in this directory or its subdirectories. Exiting.")
            return

        print(f"Found {len(json_filepaths)} JSON file(s) to process.")

    except Exception as e:
        print(f"Error: An unexpected error occurred during file search. {e}")
        return

    # Loop through the list of discovered JSON filepaths
    for filepath in json_filepaths:
        # We should not process our own output file if it happens to be a JSON file.
        if os.path.basename(filepath) == OUTPUT_FILENAME:
            continue

        print(f"Processing {filepath}...")
        try:
            # Determine the volume name from the file's parent directory.
            # e.g., os.path.dirname('Volume 01/00001.json') -> 'Volume 01'
            # We use normpath to clean up paths like './Volume 01'
            volume_name = os.path.basename(os.path.normpath(os.path.dirname(filepath)))
            # If a file is in the root directory, its dirname is empty or '.', so give it a default name.
            if not volume_name or volume_name == '.':
                volume_name = "root_volume"

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # The text is in data['blocks'][...]['lines']
                if 'blocks' in data and data['blocks']:
                    for block in data['blocks']:
                        if 'lines' in block and block['lines']:
                            for line in block['lines']:
                                # Add the line only if it contains Japanese text
                                if contains_japanese(line):
                                    # Append the line to the correct volume's list
                                    volume_data[volume_name].append(line)

        except json.JSONDecodeError:
            print(f"  - Warning: Could not parse JSON from {filepath}. File might be empty or corrupt.")
        except Exception as e:
            print(f"  - An unexpected error occurred with {filepath}: {e}")

    if not volume_data:
        print("\n---")
        print("Processing complete, but no Japanese text was found in any of the files.")
        print("---")
        return

    # Write the collected data to files based on the configuration flag
    print("\n---")
    if CREATE_FILE_PER_VOLUME:
        print("Writing output to a separate file for each volume...")
        total_lines_processed = 0
        for volume_name, lines in sorted(volume_data.items()):
            # Create a filename from the volume name and add the .txt extension
            volume_filename = f"{volume_name}.txt"
            try:
                with open(volume_filename, 'w', encoding='utf-8') as f:
                    for line in lines:
                        f.write(line + '\n')
                print(f"  - Successfully created '{volume_filename}' with {len(lines)} lines.")
                total_lines_processed += len(lines)
            except Exception as e:
                print(f"  - Error writing to output file '{volume_filename}': {e}")

        print("\nSuccess! All volumes have been processed.")
        print(f"Total volumes created: {len(volume_data)}")
        print(f"Total lines extracted: {total_lines_processed}")

    else: # Create a single, consolidated file
        print(f"Consolidating all text into a single file: '{OUTPUT_FILENAME}'")
        all_japanese_lines = []
        # Sort by volume name to ensure a consistent, ordered output
        for volume_name in sorted(volume_data.keys()):
            all_japanese_lines.extend(volume_data[volume_name])

        try:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                for line in all_japanese_lines:
                    f.write(line + '\n')

            print(f"\nSuccess! All Japanese text has been combined into '{OUTPUT_FILENAME}'.")
            print(f"Total lines extracted: {len(all_japanese_lines)}")

        except Exception as e:
            print(f"\nError writing to output file: {e}")

    print("---")


# --- Run the script ---
if __name__ == "__main__":
    process_files()
