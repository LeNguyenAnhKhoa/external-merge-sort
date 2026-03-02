"""
Script for generating sample data files to test External Merge Sort.
Can be run standalone without the GUI.
"""

import struct
import random
import os
import sys

DOUBLE_SIZE = 8
DOUBLE_FORMAT = 'd'


def create_sample_file(filepath, count, min_val=-1000, max_val=1000):
    """Create a binary file containing count random double-precision floats."""
    with open(filepath, 'wb') as f:
        for _ in range(count):
            val = round(random.uniform(min_val, max_val), 2)
            f.write(struct.pack(DOUBLE_FORMAT, val))
    print(f"Created file: {filepath}")
    print(f"  Element count: {count}")
    print(f"  File size: {os.path.getsize(filepath)} bytes")


def print_file(filepath, max_show=50):
    """Print the contents of a binary file."""
    numbers = []
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(DOUBLE_SIZE)
            if len(data) < DOUBLE_SIZE:
                break
            numbers.append(struct.unpack(DOUBLE_FORMAT, data)[0])

    count = len(numbers)
    print(f"\nFile: {filepath}")
    print(f"Element count: {count}\n")

    show = min(count, max_show)
    for i in range(show):
        print(f"  [{i:>4d}]  {numbers[i]:.2f}")
    if count > max_show:
        print(f"  ... ({count - max_show} more elements)")


if __name__ == '__main__':
    # Small sample file (16 elements) for easy demonstration
    sample_path = os.path.join(os.path.dirname(__file__), 'sample_data.bin')
    create_sample_file(sample_path, 16)
    print_file(sample_path)

    # Larger sample file (1000 elements)
    large_path = os.path.join(os.path.dirname(__file__), 'sample_large.bin')
    create_sample_file(large_path, 1000)
    print_file(large_path, max_show=10)
