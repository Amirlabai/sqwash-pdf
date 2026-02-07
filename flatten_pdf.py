import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
import os
import sys

def select_files():
    """Opens a file dialog to select multiple PDF files."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(
        title="Select PDF files to flatten",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_paths

def flatten_pdf(file_path, DPI=150, jpg_quality=75):
    """
    Flattens a PDF file by converting each page to an image and back to PDF.
    Saves the new file with a flat and dpi suffix.
    """
    try:
        doc = fitz.open(file_path)
        output_doc = fitz.open()

        print(f"Processing: {file_path}")

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=DPI)  # Render page to image at 200 DPI

            # Compress to JPEG to reduce size
            img_data = pix.tobytes("jpg", jpg_quality=jpg_quality)
            
            # Create a new page in the output document with the same dimensions
            new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, stream=img_data)
        
        # Construct output filename
        directory, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}-flat-{DPI}{ext}"
        output_path = os.path.join(directory, output_filename)

        output_doc.save(output_path)
        output_doc.close()
        doc.close()
        
        # Calculate sizes
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
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
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
