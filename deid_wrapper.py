import os  
import subprocess
import pandas as pd
import chardet

# Ensure required directories exist
def ensure_dir_exists(path):
    os.makedirs(path, exist_ok=True)

# Wrapper to handle CSV and integrate with Philter
def deidentify_csv(input_csv, output_csv, input_dir, output_dir, config_path):
    # Ensure directories exist
    ensure_dir_exists(input_dir)
    ensure_dir_exists(output_dir)

    # Detect encoding
    with open(input_csv, "rb") as f:
        result = chardet.detect(f.read(100000))
    file_encoding = result['encoding']

    # Read CSV with detected encoding
    df = pd.read_csv(input_csv, encoding=file_encoding)

    # Check if 'Note' column exists
    if 'Note' not in df.columns:
        raise ValueError("The input CSV must contain a 'Note' column.")

    # Convert notes into individual text files
    for idx, note in enumerate(df['Note'], start=1):
        file_path = os.path.join(input_dir, f"note_{idx}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(note))  # Ensure note is string

    # Run Philter
    result = subprocess.run(
        [
            "python", "main.py",
            "-i", input_dir,
            "-o", output_dir,
            "-f", config_path,
            "--outputformat", "asterisk"
        ],
        capture_output=True,
        text=True
    )

    # Check for errors
    if result.returncode != 0:
        print(f"Error during Philter execution: {result.stderr}")
        raise RuntimeError("Philter failed to process the notes. Check the setup and configuration.")

    # Collect de-identified notes and map them to the DataFrame
    deid_notes = []
    for idx in range(1, len(df) + 1):
        output_file = os.path.join(output_dir, f"note_{idx}.txt")
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as file:
                deid_notes.append(file.read().strip())
        else:
            deid_notes.append("")  # Add empty string if output is missing

    # Add de-identified notes to the DataFrame
    df['De-identified Notes'] = deid_notes

    # Save the updated DataFrame to a new CSV file with proper encoding
    df.to_csv(output_csv, index=False, encoding="Windows-1252")
    print(f"De-identified notes saved to {output_csv}")

# Example usage
if __name__ == "__main__":
    # File paths
    input_csv = "./data/i2b2_notes/Data30.csv"
    output_csv = "./data/i2b2_results/deidentified_notes37.csv"
    input_dir = "./data/i2b2_notes/"
    output_dir = "./data/i2b2_results/"
    config_path = "./configs/integration_1.json"

    try:
        deidentify_csv(input_csv, output_csv, input_dir, output_dir, config_path)
    except Exception as e:
        print(f"Error: {e}")
