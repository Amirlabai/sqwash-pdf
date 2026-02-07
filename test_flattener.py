import fitz
import os
from flatten_pdf import flatten_pdf

def create_dummy_pdf(filename="dummy.pdf"):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a dummy PDF for testing flattening.", fontsize=20)
    doc.save(filename)
    doc.close()
    return filename

def verify_flattening(original_pdf):
    flatten_pdf(original_pdf)
    
    dir_name, file_name = os.path.split(original_pdf)
    name, ext = os.path.splitext(file_name)
    expected_output = os.path.join(dir_name, f"{name}-flat-150{ext}")
    
    if os.path.exists(expected_output):
        print(f"VERIFICATION SUCCESS: Output file created at {expected_output}")
        # cleanup
        os.remove(original_pdf)
        os.remove(expected_output)
    else:
        print(f"VERIFICATION FAILURE: Output file not found at {expected_output}")

if __name__ == "__main__":
    pdf_path = create_dummy_pdf()
    print(f"Created dummy PDF at {pdf_path}")
    verify_flattening(pdf_path)
