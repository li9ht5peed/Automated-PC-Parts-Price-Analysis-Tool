import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Set display options to show all columns and disable truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

file_path = r"./fuwell.pdf"
models = ["3060", "3070", "3080", "3090", "4060", "4070", "4080", "4090", "6600", "6650",
          "6700", "6800", "6900", "7600", "7900"]
# poppler_path = r'C:\Users\user\Documents\SELF LEARNING\Selenium\poppler-23.07.0\Library\bin'

# Path to the PDF file
pdf_path = file_path

# Convert the PDF to images
images = convert_from_path(pdf_path)

# We only need the second page
second_page = images[1]

# Save the second page as a JPEG image
jpeg_path = "./page_2.jpeg"
second_page.save(jpeg_path, "JPEG")

# Open the image file
img = Image.open(jpeg_path)

# Use Tesseract to do OCR on the image
text = pytesseract.image_to_string(img)

print(text)
