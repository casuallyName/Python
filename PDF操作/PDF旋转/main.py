import PyPDF2

# 输入文件
getFile = open('A.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(getFile)
page = pdfReader.getPage(0)
# 页面旋转90度
page.rotateClockwise(90)
pdfWriter = PyPDF2.PdfFileWriter()
pdfWriter.addPage(page)
# 输出文件
outFile = open('B.pdf', 'wb')
pdfWriter.write(outFile)
outFile.close()
