# Processes all json files in the directory to produce one, consolidated file with all the Japanese text
import json
import re
import os

# --- Configuration ---
# The name of the output file.
# This file will be created in the directory where you run the script (the Parent dir).
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
    extract text, and write to an output file.
    """
    all_japanese_lines = []
    
    # --- MODIFICATION START ---
    # Find all .json files by walking through the directory tree.
    json_filepaths = []
    print("Finding all .json files in the current directory and subdirectories...")
    for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.json'):
                # Construct the full path (e.g., 'Volume 01/00001.json') and add it to our list.
                full_path = os.path.join(dirpath, filename)
                json_filepaths.append(full_path)
    # --- MODIFICATION END ---
    
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

    # --- MODIFICATION START ---
    # Loop through the list of discovered JSON filepaths
    for filepath in json_filepaths:
        # We should not process our own output file if it's a JSON.
        # os.path.basename gets the filename from the full path.
        if os.path.basename(filepath) == OUTPUT_FILENAME:
            continue
            
        # Use the full filepath in the print statement for clarity.
        print(f"Processing {filepath}...")
        try:
            # Open the file using its full path.
            with open(filepath, 'r', encoding='utf-8') as f:
    # --- MODIFICATION END ---
                data = json.load(f)
                
                # The text is in data['blocks'][...]['lines']
                if 'blocks' in data and data['blocks']:
                    for block in data['blocks']:
                        if 'lines' in block and block['lines']:
                            for line in block['lines']:
                                # Add the line only if it contains Japanese text
                                if contains_japanese(line):
                                    all_japanese_lines.append(line)

        except json.JSONDecodeError:
            # --- MODIFICATION START ---
            # Use the full filepath in the error message.
            print(f"  - Warning: Could not parse JSON from {filepath}. File might be empty or corrupt.")
        except Exception as e:
            print(f"  - An unexpected error occurred with {filepath}: {e}")
            # --- MODIFICATION END ---

    # Write all collected lines to the output file
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            for line in all_japanese_lines:
                f.write(line + '\n')
        
        print("\n---")
        print(f"Success! All Japanese text has been combined into '{OUTPUT_FILENAME}'.")
        print(f"Total lines extracted: {len(all_japanese_lines)}")
        print("---")

    except Exception as e:
        print(f"\nError writing to output file: {e}")


# --- Run the script ---
if __name__ == "__main__":
    process_files()
