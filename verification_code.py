import pandas as pd
import chardet

def add_human_verification_column(output_csv, verification_csv):
    """
    Select 100 random samples from the de-identified output CSV file
    and add a column named 'human verification' initialized with empty strings.

    Args:
        output_csv (str): Path to the de-identified CSV file.
        verification_csv (str): Path to save the human verification samples CSV file.
    """
    # Detect encoding
    with open(output_csv, "rb") as f:
        result = chardet.detect(f.read(100000))
    file_encoding = result['encoding']

    # Load the de-identified notes CSV file using detected encoding
    df = pd.read_csv(output_csv, encoding=file_encoding)

    # Ensure the file has been processed
    if "De-identified Notes" not in df.columns:
        raise ValueError("The input CSV does not contain a 'de-id notes' column.")

    # Select 100 random samples for human verification
    sampled_df = df.sample(n=100, random_state=42).copy()

    # Add the 'human verification' column initialized to empty strings
    sampled_df["human verification"] = ""

    # Save the sampled DataFrame to a new CSV file for manual review
    sampled_df.to_csv(verification_csv, index=False, encoding="Windows-1252")
    print(f"Human verification file saved to: {verification_csv}")

# Paths to files
output_csv = "./data/i2b2_results/deidentified_notes36.csv"
verification_csv = "./data/i2b2_results/verification_1.csv"

# Run the process
add_human_verification_column(output_csv, verification_csv)
