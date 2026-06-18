"""
Main script untuk hitung Term Frequency (TF) untuk 100 abstract.
Ambil data dari CSV file, proses TF, output ke CSV.
"""

import sys
import os
from pathlib import Path

# Tambah project root ke path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.tf_calculator import (
    load_abstracts_from_csv,
    process_abstracts_to_csv,
    print_tf_summary,
    CSV_INPUT_PATH
)


def main():
    """Main function untuk run TF calculation dari CSV."""
    print("\n" + "="*80)
    print("TERM FREQUENCY (TF) CALCULATOR - 100 ABSTRACTS (from CSV)")
    print("="*80 + "\n")

    try:
        csv_path = str(CSV_INPUT_PATH)
        print(f"Reading from CSV: {csv_path}")

        if not Path(csv_path).exists():
            print(f"Error: CSV file not found - {csv_path}")
            return

        # Baca CSV
        print("Loading 100 abstracts from CSV...")
        abstracts_data = load_abstracts_from_csv(csv_path, limit=100)

        if not abstracts_data:
            print("No abstracts found in CSV")
            return

        print(f"Successfully loaded {len(abstracts_data)} abstracts\n")

        # Print ringkasan
        print_tf_summary(abstracts_data, limit=3)

        # Proses TF & simpan ke CSV
        output_file = "tf_results.csv"
        process_abstracts_to_csv(abstracts_data, output_file)

        print("\n" + "="*80)
        print(f"Done! Output file: {os.path.abspath(output_file)}")
        print("="*80 + "\n")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
