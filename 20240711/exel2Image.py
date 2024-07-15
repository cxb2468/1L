from PIL import Image
import pytesseract
from openpyxl import Workbook


def load_image(image_path):
    image = Image.open(image_path)
    return image


def convert_to_grayscale(image):
    return image.convert("L")


def extract_text(image):
    return pytesseract.image_to_string(image)


def extract_table_data(text):
    rows = text.strip().split("\n")
    table_data = [row.split("\t") for row in rows]
    return table_data


def save_as_excel(table_data, output_path):
    workbook = Workbook()
    sheet = workbook.active

    for row_index, row_data in enumerate(table_data, start=1):
        for column_index, cell_data in enumerate(row_data, start=1):
            sheet.cell(row=row_index, column=column_index, value=cell_data)

    workbook.save(output_path)


# 调用示例
image_path = "table_image.jpg"
output_path = "table_data.xlsx"

image = load_image(image_path)
grayscale_image = convert_to_grayscale(image)
text = extract_text(grayscale_image)
table_data = extract_table_data(text)
save_as_excel(table_data, output_path)