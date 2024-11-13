import os
from PIL import Image


def convert_pngs_to_pdfs(source_directory, output_directory):

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # List all files in the source directory
    for filename in os.listdir(source_directory):
        if filename.lower().endswith('.png'):
            # Construct the full path for the source PNG and output PDF
            png_path = os.path.join(source_directory, filename)
            pdf_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0]}.pdf")

            # Open the image, convert to RGB, and save as PDF
            with Image.open(png_path) as img:
                img.convert("RGB").save(pdf_path, "PDF")
                print(f"Converted {filename} to PDF: {pdf_path}")


current_directory = os.getcwd()
screenshots_dir = os.path.join(current_directory, 'screenshots')
pdfs_dir = os.path.join(current_directory, 'pdfs')

convert_pngs_to_pdfs(screenshots_dir, pdfs_dir)