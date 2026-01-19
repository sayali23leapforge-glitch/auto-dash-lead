import PyPDF2

pdf_path = r"d:\Auto dashboard\DASH Report - Garnica, Ivan - 2025-11-05 10-43-31-EST - En.pdf"
pdf = PyPDF2.PdfReader(open(pdf_path, 'rb'))

text = ""
for page in pdf.pages:
    text += page.extract_text() + "\n"

print(text)
