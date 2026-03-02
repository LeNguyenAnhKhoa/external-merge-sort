"""
External Merge Sort
Sorts a binary file containing 8-byte double-precision floats in ascending order.
"""

import struct
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Size of each double-precision float: 8 bytes
DOUBLE_SIZE = 8
DOUBLE_FORMAT = 'd'


# =============================================================================
#  Binary file I/O utility functions
# =============================================================================

def read_doubles_from_file(filepath):
    """Read all doubles from a binary file."""
    numbers = []
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(DOUBLE_SIZE)
            if len(data) < DOUBLE_SIZE:
                break
            numbers.append(struct.unpack(DOUBLE_FORMAT, data)[0])
    return numbers


def write_doubles_to_file(filepath, numbers):
    """Write a list of doubles to a binary file."""
    with open(filepath, 'wb') as f:
        for num in numbers:
            f.write(struct.pack(DOUBLE_FORMAT, num))


def count_doubles_in_file(filepath):
    """Count the number of doubles in a binary file."""
    return os.path.getsize(filepath) // DOUBLE_SIZE


# =============================================================================
#  External Merge Sort
# =============================================================================

def external_merge_sort(input_path, output_path, chunk_size=4, log_func=print):
    """
    External Merge Sort.

    Phase 1: Split the file into small sorted runs (sorted in RAM).
    Phase 2: Repeatedly merge pairs of runs until a single sorted run remains.

    Parameters:
        input_path  : path to the input file
        output_path : path to the output file
        chunk_size  : maximum number of elements per run during the split phase
        log_func    : logging function used to illustrate the process
    """
    total = count_doubles_in_file(input_path)
    log_func(f"═══════════════════════════════════════════════════")
    log_func(f"  EXTERNAL MERGE SORT")
    log_func(f"  File: {os.path.basename(input_path)}")
    log_func(f"  Total elements: {total}")
    log_func(f"  Chunk size: {chunk_size}")
    log_func(f"═══════════════════════════════════════════════════\n")

    # Display original data (if small enough)
    if total <= 50:
        original = read_doubles_from_file(input_path)
        log_func(f"Input data: {format_numbers(original)}\n")

    # ---- PHASE 1: Create sorted runs ----
    log_func("╔═══════════════════════════════════════════════╗")
    log_func("║  PHASE 1: Split into chunks and sort          ║")
    log_func("╚═══════════════════════════════════════════════╝\n")

    temp_files = []
    run_index = 0

    with open(input_path, 'rb') as f_in:
        while True:
            chunk_data = f_in.read(DOUBLE_SIZE * chunk_size)
            if not chunk_data:
                break

            n = len(chunk_data) // DOUBLE_SIZE
            chunk = list(struct.unpack(f'{n}{DOUBLE_FORMAT}', chunk_data[:n * DOUBLE_SIZE]))

            log_func(f"  Run {run_index}: read {n} elements: {format_numbers(chunk)}")

            chunk.sort()
            log_func(f"           after sort: {format_numbers(chunk)}")

            temp_path = tempfile.mktemp(suffix=f'_run{run_index}.bin')
            write_doubles_to_file(temp_path, chunk)
            temp_files.append(temp_path)

            log_func(f"           → saved to: {os.path.basename(temp_path)}\n")
            run_index += 1

    log_func(f"  Total initial runs: {len(temp_files)}\n")

    # ---- PHASE 2: Merge runs ----
    log_func("╔═══════════════════════════════════════════════╗")
    log_func("║  PHASE 2: Merge runs                          ║")
    log_func("╚═══════════════════════════════════════════════╝\n")

    merge_pass = 0

    while len(temp_files) > 1:
        log_func(f"  ── Merge pass {merge_pass} ── ({len(temp_files)} runs)")
        new_temp_files = []

        # Merge pairs of runs
        i = 0
        pair_index = 0
        while i < len(temp_files):
            if i + 1 < len(temp_files):
                file_a = temp_files[i]
                file_b = temp_files[i + 1]

                log_func(f"    Merge pair {pair_index}: "
                         f"{os.path.basename(file_a)} + {os.path.basename(file_b)}")

                # Show contents before merging (if small enough)
                if total <= 50:
                    data_a = read_doubles_from_file(file_a)
                    data_b = read_doubles_from_file(file_b)
                    log_func(f"      A = {format_numbers(data_a)}")
                    log_func(f"      B = {format_numbers(data_b)}")

                merged_path = tempfile.mktemp(suffix=f'_pass{merge_pass}_pair{pair_index}.bin')
                merge_two_files(file_a, file_b, merged_path)

                # Show merged result (if small enough)
                if total <= 50:
                    merged_data = read_doubles_from_file(merged_path)
                    log_func(f"      Result = {format_numbers(merged_data)}")

                new_temp_files.append(merged_path)

                os.remove(file_a)
                os.remove(file_b)
                log_func(f"      → saved to: {os.path.basename(merged_path)}\n")

                i += 2
            else:
                # Odd run: carry over as-is
                log_func(f"    Odd run: {os.path.basename(temp_files[i])} (kept as-is)\n")
                new_temp_files.append(temp_files[i])
                i += 1

            pair_index += 1

        temp_files = new_temp_files
        merge_pass += 1

    # ---- Final result ----
    if temp_files:
        import shutil
        shutil.move(temp_files[0], output_path)
    else:
        # Empty input file
        write_doubles_to_file(output_path, [])

    log_func(f"\n╔═══════════════════════════════════════════════╗")
    log_func(f"║  DONE                                         ║")
    log_func(f"╚═══════════════════════════════════════════════╝\n")

    if total <= 50:
        result = read_doubles_from_file(output_path)
        log_func(f"Sorted output: {format_numbers(result)}\n")

    log_func(f"Output file: {output_path}")
    log_func(f"Element count: {count_doubles_in_file(output_path)}")


def merge_two_files(file_a, file_b, output_path):
    """Merge two sorted binary files into one sorted binary file."""
    with open(file_a, 'rb') as fa, open(file_b, 'rb') as fb, open(output_path, 'wb') as fout:
        a_data = fa.read(DOUBLE_SIZE)
        b_data = fb.read(DOUBLE_SIZE)

        while a_data and b_data:
            a_val = struct.unpack(DOUBLE_FORMAT, a_data)[0]
            b_val = struct.unpack(DOUBLE_FORMAT, b_data)[0]

            if a_val <= b_val:
                fout.write(a_data)
                a_data = fa.read(DOUBLE_SIZE)
            else:
                fout.write(b_data)
                b_data = fb.read(DOUBLE_SIZE)

        # Write remaining elements
        if a_data:
            fout.write(a_data)
            while True:
                chunk = fa.read(4096)
                if not chunk:
                    break
                fout.write(chunk)

        if b_data:
            fout.write(b_data)
            while True:
                chunk = fb.read(4096)
                if not chunk:
                    break
                fout.write(chunk)


def format_numbers(numbers):
    """Format a list of doubles for display."""
    if len(numbers) <= 20:
        return '[' + ', '.join(f'{x:.2f}' for x in numbers) + ']'
    else:
        head = ', '.join(f'{x:.2f}' for x in numbers[:10])
        tail = ', '.join(f'{x:.2f}' for x in numbers[-5:])
        return f'[{head}, ... , {tail}] ({len(numbers)} elements)'


# =============================================================================
#  Sample data generation
# =============================================================================

def generate_sample_file(filepath, count):
    """Generate a binary file containing random double-precision floats."""
    import random
    numbers = [round(random.uniform(-1000, 1000), 2) for _ in range(count)]
    write_doubles_to_file(filepath, numbers)
    return numbers


# =============================================================================
#  Graphical User Interface (GUI) with Tkinter
# =============================================================================

class ExternalMergeSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("External Merge Sort")
        self.root.geometry("820x650")
        self.root.resizable(True, True)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.chunk_size = tk.IntVar(value=4)
        self.sample_count = tk.IntVar(value=16)

        self._build_ui()

    def _build_ui(self):
        # ---- File selection frame ----
        frame_file = tk.LabelFrame(self.root, text="Files", padx=10, pady=5)
        frame_file.pack(fill='x', padx=10, pady=5)

        tk.Label(frame_file, text="Input file:").grid(row=0, column=0, sticky='w')
        tk.Entry(frame_file, textvariable=self.input_path, width=55).grid(row=0, column=1, padx=5)
        tk.Button(frame_file, text="Browse...", command=self._browse_input).grid(row=0, column=2)

        tk.Label(frame_file, text="Output file:").grid(row=1, column=0, sticky='w')
        tk.Entry(frame_file, textvariable=self.output_path, width=55).grid(row=1, column=1, padx=5)
        tk.Button(frame_file, text="Browse...", command=self._browse_output).grid(row=1, column=2)

        # ---- Configuration frame ----
        frame_cfg = tk.LabelFrame(self.root, text="Configuration", padx=10, pady=5)
        frame_cfg.pack(fill='x', padx=10, pady=5)

        tk.Label(frame_cfg, text="Chunk size:").grid(row=0, column=0, sticky='w')
        tk.Spinbox(frame_cfg, textvariable=self.chunk_size, from_=2, to=10000, width=10).grid(row=0, column=1, sticky='w', padx=5)
        tk.Label(frame_cfg, text="elements").grid(row=0, column=2, sticky='w')

        # ---- Sample data generation frame ----
        frame_gen = tk.LabelFrame(self.root, text="Generate sample data", padx=10, pady=5)
        frame_gen.pack(fill='x', padx=10, pady=5)

        tk.Label(frame_gen, text="Element count:").grid(row=0, column=0, sticky='w')
        tk.Spinbox(frame_gen, textvariable=self.sample_count, from_=2, to=1000000, width=10).grid(row=0, column=1, sticky='w', padx=5)
        tk.Button(frame_gen, text="Generate sample file", command=self._generate_sample).grid(row=0, column=2, padx=10)

        # ---- Sort button frame ----
        frame_btn = tk.Frame(self.root)
        frame_btn.pack(pady=5)

        tk.Button(frame_btn, text="  SORT  ", command=self._run_sort,
                  bg='#4CAF50', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=5)

        tk.Button(frame_btn, text="View input file", command=self._view_input).pack(side='left', padx=5)
        tk.Button(frame_btn, text="View output file", command=self._view_output).pack(side='left', padx=5)

        # ---- Log area ----
        frame_log = tk.LabelFrame(self.root, text="Sort process log", padx=5, pady=5)
        frame_log.pack(fill='both', expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(frame_log, wrap='word', font=('Consolas', 10))
        self.log_text.pack(fill='both', expand=True)

    def _log(self, message):
        """Append a message to the log display area."""
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.root.update_idletasks()

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Select input data file",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if path:
            self.input_path.set(path)
            # Auto-set output file name
            base, ext = os.path.splitext(path)
            self.output_path.set(base + '_sorted' + ext)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Select output file location",
            defaultextension=".bin",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if path:
            self.output_path.set(path)

    def _generate_sample(self):
        """Generate a sample data file."""
        path = filedialog.asksaveasfilename(
            title="Save sample data file",
            defaultextension=".bin",
            filetypes=[("Binary files", "*.bin")]
        )
        if not path:
            return

        count = self.sample_count.get()
        numbers = generate_sample_file(path, count)
        self.input_path.set(path)
        base, ext = os.path.splitext(path)
        self.output_path.set(base + '_sorted' + ext)

        self.log_text.delete('1.0', 'end')
        self._log(f"Sample file created: {path}")
        self._log(f"Element count: {count}")
        if count <= 50:
            self._log(f"Data: {format_numbers(numbers)}")
        messagebox.showinfo("Success", f"Generated {count} random doubles.")

    def _run_sort(self):
        """Run external merge sort."""
        input_path = self.input_path.get().strip()
        output_path = self.output_path.get().strip()

        if not input_path or not os.path.isfile(input_path):
            messagebox.showerror("Error", "Please select a valid input file.")
            return
        if not output_path:
            messagebox.showerror("Error", "Please select an output file.")
            return

        chunk = self.chunk_size.get()
        if chunk < 2:
            messagebox.showerror("Error", "Chunk size must be >= 2.")
            return

        self.log_text.delete('1.0', 'end')

        try:
            external_merge_sort(input_path, output_path, chunk_size=chunk, log_func=self._log)
            messagebox.showinfo("Done", "Sort completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _view_input(self):
        """Display the contents of the input file."""
        path = self.input_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Input file not found.")
            return
        self._view_file(path, "Input file")

    def _view_output(self):
        """Display the contents of the output file."""
        path = self.output_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Output file not found.")
            return
        self._view_file(path, "Output file")

    def _view_file(self, path, title):
        """Display the contents of a binary data file."""
        numbers = read_doubles_from_file(path)
        self.log_text.delete('1.0', 'end')
        self._log(f"── {title}: {os.path.basename(path)} ──")
        self._log(f"Element count: {len(numbers)}")
        self._log(f"File size: {os.path.getsize(path)} bytes\n")

        if len(numbers) <= 100:
            for i, num in enumerate(numbers):
                self._log(f"  [{i:>4d}]  {num:.2f}")
        else:
            self._log("(Showing first 50 and last 20 elements)\n")
            for i in range(50):
                self._log(f"  [{i:>4d}]  {numbers[i]:.2f}")
            self._log(f"  ... ({len(numbers) - 70} elements hidden) ...")
            for i in range(len(numbers) - 20, len(numbers)):
                self._log(f"  [{i:>4d}]  {numbers[i]:.2f}")


# =============================================================================
#  Main
# =============================================================================

if __name__ == '__main__':
    root = tk.Tk()
    app = ExternalMergeSortApp(root)
    root.mainloop()
