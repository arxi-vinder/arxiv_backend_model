import csv
import pandas as pd
from collections import Counter
from typing import List, Dict
from pathlib import Path
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

STOP_WORDS = set(stopwords.words('english'))
CSV_INPUT_PATH = Path(__file__).parent.parent / "ml" / "arxiv_papers_daily_fixed.csv"


def calculate_tf(abstract: str) -> Dict[str, float]:
    """
    Hitung Term Frequency (TF) untuk satu abstract.
    TF = (frekuensi term) / (total jumlah term)
    """
    if not abstract or abstract.strip() == "":
        return {}

    # Tokenize & filter stopwords
    tokens = abstract.split()
    tokens = [token for token in tokens if token not in STOP_WORDS and len(token) > 1]

    if not tokens:
        return {}

    # Hitung frekuensi
    token_counts = Counter(tokens)
    total_tokens = len(tokens)

    # Hitung TF
    tf_dict = {token: (count / total_tokens) for token, count in token_counts.items()}

    return tf_dict


def load_abstracts_from_csv(csv_path: str, limit: int = 100) -> List[Dict]:
    """
    Baca abstract dari CSV file.

    Args:
        csv_path: path ke CSV file
        limit: jumlah rows yang diambil

    Returns:
        List of dict dengan keys: id, title, abstract, category
    """
    try:
        df = pd.read_csv(csv_path)
        abstracts = []

        for idx, row in df.head(limit).iterrows():
            abstracts.append({
                'id': row.get('id', idx),
                'title': row.get('title', ''),
                'abstract': row.get('abstract', ''),
                'category': row.get('category', ''),
            })

        return abstracts
    except FileNotFoundError:
        print(f"Error: File not found - {csv_path}")
        return []
    except Exception as e:
        print(f"Error reading CSV: {type(e).__name__}: {str(e)}")
        return []


def process_abstracts_to_csv(abstracts: List[Dict], output_file: str = "tf_results.csv"):
    """
    Agregasi term & frekuensi dari 100 abstract, output ke CSV.

    Args:
        abstracts: list of dict {'id': int, 'abstract': str, 'title': str, 'category': str}
        output_file: nama file CSV output (kolom: term, frequency)
    """
    all_terms = Counter()

    # Agregasi semua term dari semua abstract
    for paper in abstracts[:100]:
        abstract_text = paper.get('abstract', '')

        # Tokenize & filter stopwords
        tokens = abstract_text.split()
        tokens = [token for token in tokens if token not in STOP_WORDS and len(token) > 1]

        # Tambah ke aggregated counter
        all_terms.update(tokens)

    # Sort by frequency
    sorted_terms = sorted(all_terms.items(), key=lambda x: x[1], reverse=True)

    # Simpan ke CSV
    if sorted_terms:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['term', 'frequency'])
            for term, freq in sorted_terms:
                writer.writerow([term, freq])

        print(f"✓ Hasil dihemat ke: {output_file}")
        print(f"✓ Total papers diproses: {len(abstracts[:100])}")
        print(f"✓ Total unique terms: {len(sorted_terms)}")
        print(f"✓ Total frekuensi kata: {sum(freq for _, freq in sorted_terms)}")
    else:
        print("✗ Tidak ada data abstract")


def print_tf_summary(abstracts: List[Dict], limit: int = 5):
    """Print ringkasan TF untuk beberapa abstract pertama."""
    print("\n" + "="*80)
    print("RINGKASAN TF UNTUK BEBERAPA ABSTRACT PERTAMA")
    print("="*80 + "\n")

    for idx, paper in enumerate(abstracts[:limit], 1):
        print(f"Paper {idx}: {paper.get('title', 'N/A')}")
        print(f"Category: {paper.get('category', 'N/A')}")

        tf_dict = calculate_tf(paper.get('abstract', ''))
        top_terms = sorted(tf_dict.items(), key=lambda x: x[1], reverse=True)[:5]

        print("Top 5 Terms (TF):")
        for rank, (term, tf_value) in enumerate(top_terms, 1):
            print(f"  {rank}. {term}: {tf_value:.4f}")
        print()


if __name__ == "__main__":
    import sys

    print("\n" + "="*80)
    print("TERM FREQUENCY (TF) CALCULATOR - 100 ABSTRACTS (from CSV)")
    print("="*80 + "\n")

    try:
        csv_path = str(CSV_INPUT_PATH)
        print(f"Reading from CSV: {csv_path}")

        if not Path(csv_path).exists():
            print(f"Error: CSV file not found - {csv_path}")
            sys.exit(1)

        abstracts_data = load_abstracts_from_csv(csv_path, limit=100)

        if not abstracts_data:
            print("No abstracts found in CSV")
            sys.exit(1)

        print(f"Successfully loaded {len(abstracts_data)} abstracts\n")

        print_tf_summary(abstracts_data, limit=3)

        output_file = "tf_results.csv"
        process_abstracts_to_csv(abstracts_data, output_file)

        print("\n" + "="*80)
        print(f"Done! Output saved to: {output_file}")
        print("="*80 + "\n")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
