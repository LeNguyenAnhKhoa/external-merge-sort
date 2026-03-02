# External Merge Sort

Sorts a binary file of **8-byte double-precision floats** in ascending order using the external merge sort algorithm. Includes a Tkinter GUI to visualise each phase of the process.

## Requirements

- Python 3.x (standard library only — no extra packages needed)

## Usage

### 1. Generate sample data

```bash
python generate_data.py
```

Creates `sample_data.bin` (16 random doubles) in the project directory.

### 2. Run the sorter

```bash
python external_merge_sort.py
```

The GUI will open. Steps:

1. **Select input file** — choose a `.bin` file (e.g. `sample_data.bin`).
2. **Select output file** — choose where to save the sorted result.
3. **Set chunk size** — number of elements loaded into RAM per run (default: 4).
4. Click **Run Sort** — the log panel shows every split and merge step.

## How it works

| Phase | Description |
|-------|-------------|
| **Phase 1 – Split** | Reads the file in chunks, sorts each chunk in RAM, writes sorted runs to temporary files. |
| **Phase 2 – Merge** | Repeatedly merges pairs of sorted runs until a single sorted file remains. |

## File format

Binary file — each element is a **64-bit IEEE 754 double** (little-endian, 8 bytes).  
Use `generate_data.py` or write your own generator with Python's `struct.pack('d', value)`.
