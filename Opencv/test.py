from PIL import Image
import pytesseract

text = pytesseract.image_to_string(Image.open(r'D:\1\123.jpg'))
print(text)