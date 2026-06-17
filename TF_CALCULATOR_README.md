# Term Frequency (TF) Calculator

Script untuk menghitung **Term Frequency** dari 100 abstract pertama di file CSV `app/ml/arxiv_papers_daily_fixed.csv`, lalu output hasilnya ke file CSV baru.

## File-file

| File | Deskripsi |
|------|-----------|
| `app/utils/tf_calculator.py` | Logic TF + main block (bisa jalankan langsung) |
| `tf_main.py` | Main script alternatif untuk run TF calculator |
| `run_tf.bat` | Script terminal untuk Windows |
| `run_tf.sh` | Script terminal untuk Linux/Mac |
| `tf_results.csv` | Output CSV (hasil TF calculation) |

## Cara Menjalankan

### Option 1: Langsung dari tf_calculator.py (Recommended)
```bash
python app/utils/tf_calculator.py
```
atau
```cmd
python app\utils\tf_calculator.py
```

### Option 2: Windows (menggunakan .bat)
```cmd
run_tf.bat
```

### Option 3: Linux/Mac (menggunakan .sh)
```bash
bash run_tf.sh
```

### Option 4: Menggunakan tf_main.py
```bash
python tf_main.py
```

## Deskripsi Output CSV

File `tf_results.csv` berisi agregasi term & frekuensi dari 100 abstract, dengan kolom:

| Kolom | Deskripsi |
|-------|-----------|
| `term` | Kata yang dianalisis |
| `frequency` | Total frekuensi kata pada 100 abstract |

### Contoh:
```csv
term,frequency
model,156
data,142
algorithm,98
network,87
train,76
learning,65
system,54
```

## Penjelasan Frequency

Script menghitung **total frekuensi** (jumlah kemunculan) setiap term di seluruh 100 abstract.

Contoh:
- Word "model" muncul 3x di abstract-1, 2x di abstract-2, 1x di abstract-3
- Total frequency("model") = 3 + 2 + 1 = 6

Script ini:
1. Mengambil 100 abstract pertama dari CSV
2. Menghapus stopwords (a, the, is, etc.)
3. Menghitung total frekuensi setiap term di semua 100 abstract
4. Sort by frequency (descending)
5. Output ke CSV (kolom: term, frequency)

## Prerequisite

- File CSV `app/ml/arxiv_papers_daily_fixed.csv` sudah ada
- Python 3.8+
- Library: `nltk`, `pandas` (sudah ada di project)
- Tidak perlu database connection

## Output Contoh

Saat menjalankan script, output console akan seperti:

```
================================================================================
TERM FREQUENCY (TF) CALCULATOR - 100 ABSTRACTS (from CSV)
================================================================================

Reading from CSV: app/ml/arxiv_papers_daily_fixed.csv
Loading 100 abstracts from CSV...
Successfully loaded 100 abstracts

================================================================================
RINGKASAN TF UNTUK BEBERAPA ABSTRACT PERTAMA
================================================================================

Paper 1: Distribution of independent sets in perfect r-ary trees
Category: Combinatorics (math.CO)
Top 5 Terms (TF):
  1. tree: 0.0856
  2. set: 0.0712
  3. vertex: 0.0634
  4. independent: 0.0576
  5. conjecture: 0.0512

[...]

================================================================================
✓ Hasil dihemat ke: tf_results.csv
✓ Total papers diproses: 100
✓ Total unique terms: 3245
✓ Total frekuensi kata: 25847
================================================================================
```

**Output CSV (`tf_results.csv`):**
```csv
term,frequency
model,156
network,142
data,98
algorithm,87
train,76
learning,65
system,54
```

## Troubleshooting

**Error: File not found - app/ml/arxiv_papers_daily_fixed.csv**
- Pastikan file CSV ada di path: `app/ml/arxiv_papers_daily_fixed.csv`
- File harus memiliki kolom: `id`, `title`, `abstract`, `category`

**Error: No abstracts found in CSV**
- Pastikan CSV file tidak kosong
- Cek format CSV file (gunakan text editor untuk verifikasi)

**CSV output tidak terbuat**
- Cek permission folder untuk write file CSV
- Pastikan disk space cukup
- Cek apakah ada abstract yang kosong/null (akan diabaikan)

**pandas not found**
- Install pandas: `pip install pandas`

## Customization

Untuk mengubah jumlah abstract yang diproses, edit `app/utils/tf_calculator.py` baris di `load_abstracts_from_csv()`:
```python
load_abstracts_from_csv(csv_path, limit=100)  # Ubah 100 ke jumlah lain
```

Untuk mengubah file CSV input, edit `app/utils/tf_calculator.py` baris:
```python
CSV_INPUT_PATH = Path(__file__).parent.parent / "ml" / "arxiv_papers_daily_fixed.csv"
```

Untuk mengubah nama output file, edit baris dalam `tf_main.py` atau `tf_calculator.py`:
```python
output_file = "tf_results.csv"  # Ubah ke nama file lain
```
