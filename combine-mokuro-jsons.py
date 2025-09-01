import json
import re
import os

# --- Configuration ---
# The name of the output file.
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
    Main function to find all .json files, extract text, and write to an output file.
    """
    all_japanese_lines = []
    
    print("Finding all .json files in the current directory...")
    try:
        # Get a list of all files in the directory that end with .json
        json_filenames = [f for f in os.listdir('.') if f.endswith('.json')]
        
        # Sort the list to process files in a predictable order (e.g., 00001, 00002...)
        json_filenames.sort()
        
        if not json_filenames:
            print("No .json files were found in this directory. Exiting.")
            return

        print(f"Found {len(json_filenames)} JSON file(s) to process.")

    except Exception as e:
        print(f"Error: Could not read the directory contents. {e}")
        return

    # Loop through the list of discovered JSON filenames
    for filename in json_filenames:
        # We should not process our own output file if it's a JSON
        if filename == OUTPUT_FILENAME:
            continue
            
        print(f"Processing {filename}...")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
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
            print(f"  - Warning: Could not parse JSON from {filename}. File might be empty or corrupt.")
        except Exception as e:
            print(f"  - An unexpected error occurred with {filename}: {e}")

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