import os
import sys
import tkinter as tk
from tkinter import filedialog

from lib.flatten import flatten_pdf_bytes


def select_files():
    """Opens a file dialog to select multiple PDF files."""
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select PDF files to flatten",
        filetypes=[("PDF files", "*.pdf")],
    )
    return file_paths


def flatten_pdf(file_path, DPI=150, jpg_quality=75):
    """
    Flattens a PDF file by converting each page to an image and back to PDF.
    Saves the new file with a flat and dpi suffix.
    """
    try:
        print(f"Processing: {file_path}")

        with open(file_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        output_bytes = flatten_pdf_bytes(pdf_bytes, dpi=DPI, jpg_quality=jpg_quality)

        directory, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}-flat-{DPI}{ext}"
        output_path = os.path.join(directory, output_filename)

        with open(output_path, "wb") as output_file:
            output_file.write(output_bytes)

        original_size = os.path.getsize(file_path)
        new_size = os.path.getsize(output_path)
        reduction = ((original_size - new_size) / original_size) * 100

        print(f"Successfully saved to: {output_path}")
        print(f"Original size: {format_size(original_size)}")
        print(f"New size:      {format_size(new_size)}")
        print(f"Reduction:     {reduction:.2f}%")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def format_size(size_bytes):
    """Converts bytes to a human-readable string (KB, MB, GB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_input_with_default(prompt, default_val):
    val = input(prompt)
    if val.strip() == "":
        return default_val
    try:
        return int(val)
    except ValueError:
        print(f"Invalid input, using default: {default_val}")
        return default_val


if __name__ == "__main__":
    print("Select PDF files to flatten...")
    try:
        selected_files = select_files()

        if not selected_files:
            print("No files selected. Exiting.")
        else:
            DPI = get_input_with_default("Enter DPI range 72-300 (default is 150): ", 150)
            jpg_quality = get_input_with_default("Enter JPG quality range 0-100 (default is 75): ", 75)

            for pdf_file in selected_files:
                flatten_pdf(pdf_file, DPI, jpg_quality)
            print("Done!")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
