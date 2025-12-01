import ijson
import csv
import os

# --- CONFIGURATION ---
input_json_file = 'repo_metadata.json'  # Make sure this matches your file name exactly
output_csv_file = 'github_data.csv'
# ---------------------

def clean_list(value):
    """Converts list ['a', 'b'] to string 'a;b' for CSV."""
    if isinstance(value, list):
        # Convert items to string and join, handling potential None values
        return ";".join([str(x) for x in value if x is not None])
    return value

def convert_json_to_csv_stream():
    print(f"Processing {input_json_file}...")

    # Open the file in binary mode for ijson
    with open(input_json_file, 'rb') as f:
        # 'item' tells ijson to look for objects inside a top-level list
        objects = ijson.items(f, 'item')

        csv_file = open(output_csv_file, 'w', newline='', encoding='utf-8')
        writer = None
        count = 0

        try:
            for row in objects:
                # 1. SETUP HEADER (First row only)
                if count == 0:
                    headers = row.keys()
                    # --- THE FIX IS HERE: added escapechar='\\' ---
                    writer = csv.DictWriter(csv_file, fieldnames=headers, escapechar='\\')
                    writer.writeheader()

                # 2. CLEAN DATA
                clean_row = {k: clean_list(v) for k, v in row.items()}

                # 3. WRITE ROW
                writer.writerow(clean_row)
                count += 1

                if count % 10000 == 0:
                    print(f"Converted {count} rows...", end='\r')

        except ijson.common.IncompleteJSONError:
            print("\nWarning: The JSON file ended unexpectedly (it might be corrupted), but we saved what we could.")
        except Exception as e:
             print(f"\nError on row {count}: {e}")

        csv_file.close()
        print(f"\n\nSUCCESS! Processed {count} repositories.")
        print(f"Saved to: {output_csv_file}")

if __name__ == "__main__":
    if not os.path.exists(input_json_file):
        print(f"Error: Could not find '{input_json_file}'. Check the file name!")
    else:
        convert_json_to_csv_stream()