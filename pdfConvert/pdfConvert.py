import pandas as pd
import tabula
import os
#os.environ["JAVA_HOME"] ="/home/sruthi/miniconda3/envs/pyimagej/lib/jvm"

def pdf_to_excel(dir, input_fname, output_fname):
    dir_old = os.getcwd()
    os.chdir(dir)
    # Read PDF file
    tables = tabula.read_pdf(input_fname, pages='all', multiple_tables=True)

    # Write each table to a separate sheet in the Excel file
    with pd.ExcelWriter(output_fname) as writer:
        for i, table in enumerate(tables):
            table.to_excel(writer, sheet_name=f'Sheet{i+1}')

dir = r'C:\Users\ginse\OneDrive\Documents\Tools\pdfConvert\pdfs'
fname = r'Blairs_CableSchedule'
input_fname = fname+'.pdf'
output_fname= fname+'.xlsx'
pdf_to_excel(dir, input_fname, output_fname)