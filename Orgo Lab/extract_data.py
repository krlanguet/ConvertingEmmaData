import PyPDF2
from openpyxl import Workbook, load_workbook
from pandas import DataFrame as DF
from pandas import ExcelWriter
from re import search
from os import path
from time import strftime as time
from sys import argv as arguments

from data import *

working_dir = path.dirname(__file__)

# Assumes all parameters passed to script are file names for parsing
rel_paths = arguments[1:]

input_files = [input_file(working_dir, rel_path) for rel_path in rel_paths]

output_name = time('Output %I:%M:%S.xlsx') # Current local time in 12Hour, minute, seconds
writer = ExcelWriter(output_name, engine='openpyxl')
writer.book = Workbook()

for input_file in input_files:
    input_file.extract()

    cur_row = 3

    input_file.full_title.to_excel(writer, input_file.short_title, index=False, startrow=0)
    if not input_file.signals:
        continue
    for signal in input_file.signals:
        if signal.valid:
            signal.parameters.to_excel(writer, input_file.short_title, index=False, startrow=cur_row)
            cur_row += 1
            signal.Data.to_excel(writer, input_file.short_title, index=False, startrow=cur_row)
            cur_row += len(signal.Data.index) + 2

writer.save()

for input_file in input_files:
    input_file.close()
