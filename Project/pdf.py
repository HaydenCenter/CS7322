import PyPDF2

reader = PyPDF2.PdfFileReader("94.pdf")
numPages = reader.numPages
text = []
for page in range(numPages):
    text.append(reader.pages[page].extractText())

print("\n".join(text))
