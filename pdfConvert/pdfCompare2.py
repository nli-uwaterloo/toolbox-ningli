import PyPDF2
import os
from datetime import datetime
from PyPDF2 import PdfReader, PdfFileMerger
import PyPDFCompare as pycompare
'''
step 1: extract file names of old and new sets
step 2: compare or diff the 2 list of file names
step 3: d
'''

def extractSheetName(list):
    newlist = []
    for s in list:
        sheet = s.split('-')[0]
        newlist.append(sheet)
        i = 0
    return newlist

def compareList(list1, list2):
    s = set(list2)
    list3 = [x for x in list1 if x not in s]
    print(list3)
    return list3

def mergePDF_dir(dir, fname_output):
    olddir = os.getcwd()
    list = os.listdir(dir)
    os.chdir(os.path.join(olddir, dir))
    output = PdfFileMerger()
    for s in list:
        f = PdfReader(s)
        output.append(f)
    os.chdir(olddir)

    with open(fname_output, "wb") as output_stream:
        output.write(output_stream)

def prepSets(dir, dirOld, dirNew):
    return True
    olddir = os.getcwd()
    os.chdir(dir)

    listOld = os.listdir(dirOld)
    listNew = os.listdir(dirNew)

    #listOld = extractSheetName(listOld)
    #listNew = extractSheetName(listNew)
    list_diff = compareList(listOld, listNew)
    list_diffrev = compareList(listNew, listOld)
    print (list_diff)
    print (list_diffrev)
    if not list_diff:
        mergePDF_dir(dirOld, "old_merged.pdf")
        mergePDF_dir(dirNew, "new_merged.pdf")
        return True
    else:
        return False
    os.chdir(olddir)

dirpath = r'C:\Users\ginse\OneDrive\Documents\SG\Projects\Backbone - VEP\Engineering\Electrical-Engineering\Electrical-Design\compare_2'
dirpath = r'C:\Users\ginse\OneDrive\Documents\SG\Projects\Swiftwater - Narenco\Design Drawings\Electrical\compare_4'
dirpath = r'C:\Users\ginse\OneDrive\Documents\SG\Projects\Sun Ridge - Energix\Electrical RFP\compare 2'
dirOld = r'Swiftwater Electrical IFC 4-4-2024' #'old_page3.pdf'
dirNew = r'Swiftwater Electrical IFC 8-15-2024'
fnameOld = r'old_2024.05.10 Sun Ridge IFP.pdf'
fnameNew = r'new_2024.09.27 Sun Ridge IFR.pdf'
pycompare.main(dirpath, [fnameOld, fnameNew], ['-mp:NEW'])
# if prepSets(dirpath, dirOld, dirNew):
#     pycompare.main(dirpath, [fnameOld, fnameNew], ['-mp:NEW'])
