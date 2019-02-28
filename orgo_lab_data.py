import PyPDF2
from openpyxl import Workbook
from pandas import DataFrame as DF, Series, ExcelWriter
from re import search, sub, split
from os import path
from time import strftime as time
from sys import argv as arguments

class signal:
    def __init__(self, raw_text):
        if ': MWD' not in raw_text:
            self.valid = False
            return
        self.valid = True
        self.number = raw_text[0]
        self.parameters = DF(data=[0], columns=["Signal: " + self.number + " " + search("(?<=\d: )MWD.*(?=Peak)" , raw_text)[0]])
        self.columns = ["Peak #", "RetTime [min]", "Type", "Width [min]", "Area [mAU*S]", "Height [mAU]", "Area %"]

        rows = search("(?<=--\|) {1,3}\d.*(?=Totals)", raw_text)[0]
        rows = sub("Data *File.*Page\d of\d", '', rows)
        rows = rows.split()
        for i, item in enumerate(rows):
            if (i + 1) < len(rows) and item.isalpha() and rows[i + 1].isalpha():
                rows[i] = item + ' ' + rows[i + 1]
                del(rows[i + 1])

        self.rows = []
        for i in range(0, len(rows), 7):
            self.rows.append(rows[i: i + 7])
        
        self.totals = search("Totals : * \d*.*$", raw_text)[0].split()[-2:]

        self.Data = DF(data = self.rows, columns = self.columns)

class input_file:
    def __init__(self, working_dir, rel_path):
        #print(rel_path)
        self.rel_path = rel_path
        file_path = path.join(working_dir, rel_path)
        title = path.basename(file_path)
        self.short_title = ""
        for word in split('\(|\)|,|\.| ', title)[:-1]:
            if len(word):
                self.short_title += word[0]
        self.full_title = DF(data=[0], columns=[title])

        self.input_file = open(file_path, 'rb')
        self.reader = PyPDF2.PdfFileReader(self.input_file)
        self.signals = None

    def close(self):
        self.input_file.close()

    def extract(self):
        numPages = self.reader.numPages
        '''
        if (numPages != 3):
            print("File {} actually has {} pages! Ignoring.".format(self.rel_path, numPages))
            return ''
        '''

        text = ""
        for i in range(numPages):
            text += self.reader.getPage(i).extractText()

        if not 'Signal' in text:
            return
        
        self.signals = [signal(raw_text) for raw_text in text.split("Signal ")]

