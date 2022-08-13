
import os
import shutil
from os.path import isfile, isdir, join
#from typing_extensions import ParamSpecKwargs
from PyPDF2 import PdfFileReader
import PyPDF2
import ocrmypdf
import pathlib
import datetime
from datetime import date
import re # https://www.guru99.com/python-regular-expressions-complete-tutorial.html
import hashlib
from pikepdf import Pdf


# Keywords as one field in the list entry
#    -> valid header for list entry
#       date1; newFilename; wasOCR; moreDates; allKeywords; fileSizeW; fileSizeH; pageCount; neHash; oldHas; oldFilename; processTime,ctime, mtime, atime, 
# Convert rexp dates to datetime -> sort early to late -> use in that order
# Limit filename length
# Include in listentry: md5 hash of converted/ copied file
# Filename: date in yyyymmdd format_ hasOrgFile_ pagenum_wxh_keywords (limited)
# keyword scanning: each letter may be lower or upper case. use of /i ?

#bseFolder = "C:/Users/DSchwenn/Desktop/BigScanProject"
bseFolder = "/mnt/c/Users/DSchwenn/Desktop/BigScanProject"
outFld = "Out"
inFld = "In"


tmpLstFile = 'lst.txt'
tmpTxtFile = 'tmpTxt.txt'
tmpPdfFile = 'tmpPdf.pdf'
resInfoListFile = 'fileInfoList.txt'
tmpFolde = "tmp"


def processFolderRecursive(folderIn,folderOut):
    listEntries = ""
    # caLL ITSELF WOITH ALL SUBFOLDERS
    fldrs = os.listdir(folderIn)
    for f in fldrs:
        if( isdir( join(folderIn, f) ) ):
            listEntries = processFolderRecursive(join(folderIn, f),join(folderOut, f))

    # modify output folder according to subfolder

    # process all pdf files in the folder
    for f in fldrs:
        if( isfile(join(folderIn, f)) and ( f.endswith('.pdf') or f.endswith('.PDF') ) ):
            listEntry = processPdfFile( join(folderIn,f), folderOut )
            if( listEntry != "" ):
                file = open(join(bseFolder,tmpLstFile),mode='a')
                file.write(listEntry)
                file.close()
                listEntries += listEntry + "\n"
    
    return listEntries


def checkFolderForHashInName(folderOut,dig):
    fldrs = os.listdir(folderOut)
    for f in fldrs:
        if(f.find(dig)>=0): # TODO: like this?
            return True
    return False


def processPdfFile( filenameIn, folderOut ):
    # create output folder if non existing
    if( not isdir(folderOut) ):
        os.makedirs(folderOut)
    print(filenameIn)
    pdfFileObj = open(filenameIn,'rb')#The pdfReader variable is a readable object that will be parsed.
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)#Discerning the number of pages will allow us to parse through all the pages.
    
    tmpOut = join(join(bseFolder, tmpFolde), tmpPdfFile)

    count = 0
    text = ""#The while loop will read each page.
    w=0.0
    h=0.0
    num_pages = 0

    try:
        if pdfReader.isEncrypted:
            pdfReader.decrypt('')
    except NotImplementedError:
        with Pdf.open(filenameIn,password='') as pdf:
            pdf.save(tmpOut)
            pdfFileObj = open(tmpOut,'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    try:
        num_pages = pdfReader.numPages
        while count < num_pages:
            if(count==0):
                w = float(pdfReader.getPage(count).mediaBox.getWidth())*0.352 # 1 point of putput = 0.352mm "user space unit"
                h = float(pdfReader.getPage(count).mediaBox.getHeight())*0.352
            pageObj = pdfReader.getPage(count)
            count +=1
            text += pageObj.extractText()#This if statement exists to check if the above library returned words. It's done because PyPDF2 cannot read scanned files.
    except NotImplementedError:
        text = "DecryptFailed"


    #check if output file exists with same hash exists -> if so return ""
    dig = md5fromFile(filenameIn)
    if( checkFolderForHashInName(folderOut,dig) ):
        return ""

    
    ocr_done = True

    if text != "":
        #shutil.copy(filenameIn,tmpOut)
        #os.rename(filenameIn,tmpOut) # copy to filenameOut
        ocr_done = False
        text = text#If the above returns as False, we run the OCR library textract to #convert scanned/image based PDF files into text.
    else:
        #print("DBG: would have OCRed...")
        #file = open(tmpOut,mode='w')
        #file.close()
        try:
            ocrmypdf.ocr(filenameIn, tmpOut, deskew=True, rotate_pages=True, language='deu+eng', sidecar=tmpTxtFile,clean=True,optimize=2)
            file = open(tmpTxtFile,mode='r')
            text = file.read()
            file.close()
        except ocrmypdf.exceptions.PriorOcrFoundError:
            text = "ORCFailed"


    dates = parseForDates(text)
    keys = parseTextContent(text) # keywords/ dates and also page num, HDF5, file creation timedate and page size
    
    docNums = str(num_pages)+"_"+str(int(w))+"x"+str(int(h))
    newFileName1 = filenameFromInfos( keys, dates, docNums, dig )

    newFileName = join(folderOut,newFileName1)
    #os.rename(tmpOut,newFileName) # move/ rename temp file to newFileName
    if(ocr_done):
        os.rename(tmpOut,newFileName)
        #tmpTxtFile
    else:
        shutil.copy(filenameIn,newFileName)

    # copy= pathlib.Path(filenameIn) from in file. creation time only a thing on windows...
    fInName = pathlib.Path(filenameIn)
    ctime = datetime.datetime.fromtimestamp(fInName.stat().st_ctime)
    mtime = datetime.datetime.fromtimestamp(fInName.stat().st_mtime)
    atime = datetime.datetime.fromtimestamp(fInName.stat().st_atime)
    os.utime(newFileName, (fInName.stat().st_atime, fInName.stat().st_mtime))

    sp = os.path.split(filenameIn)
    # sp2 = os.path.split(newFileName)
    # if( len(dates)>0 ):
    #     infos = [sp2[1], sp[1] , dates[0] , dig , docNums] + keys
    # else:
    #    infos = [sp2[1], sp[1], "0000", dig, docNums] + keys

    # if( len(dates)>1 ):
    #    infos += dates[1::]

    sp = os.path.split(filenameIn)
    dig2 = md5fromFile(newFileName)
    fileListEntry = fileListEntryFromInfos(dates,keys,[datetime.datetime.now(),ctime,mtime,atime],[sp[1],newFileName1],[dig,dig2],[num_pages,w,h],ocr_done)

    return fileListEntry

def filenameFromInfos( infos, dates, docNums,dig ):
    sOut = ""


    if(len(dates)>0):
        sOut += dates[0].strftime("%Y%m%d") + "_" + dig + "_" + docNums
    else:
        sOut += "00000000" + "_" + dig + "_" + docNums

    for w in infos:
        sOut += "_" + w

    if(len(sOut) > 124): # limit filename length
        sOut = sOut[0:123:]

    sOut += ".pdf"

    return sOut



def fileListEntryFromInfos(dates,keys,x4times,fileNames,hashes,nums,ocrFlag):
    # (dates,keys,[datetime.datetime.now(),ctime,mtime,atime],[sp,newFileName1],[dig,dig2],[num_pages,w,h],ocr_done)
    # date1; newFilename; wasOCR; moreDates; allKeywords; fileSizeW; fileSizeH; pageCount; oldHas; neHash; oldFilename; processTime,ctime, mtime, atime, 

    sOut = ""

    if(len(dates)>0):
        sOut = str(dates[0]) + ";"
    else:
        sOut = "00000000" + ";"

    sOut += fileNames[1] + ";" + str(ocrFlag) + ";"

    if(len(dates)>1):
        for t in dates:
            sOut += str(t) + ","
    else:
        sOut += "00000000"
    sOut += ";"
    
    for w in keys:
        sOut += w + ","
    sOut += ";"

    sOut += str(nums[1]) + ";" + str(nums[2]) + ";" + str(nums[0]) + ";"

    sOut += hashes[0] + ";" + hashes[1] + ";"

    sOut += fileNames[0] + ";" 

    for t in x4times:
        sOut += str(t) + ","
    

    return sOut


def parseTextContent(text):
    kw1 = parseForKeywords(text,getSauceKey()) #,"SRC:")
    kw2 = parseForKeywords(text,getPlaceKey()) #,"PLC:")
    kw3 = parseForKeywords(text,getLivingKey()) #,"LVG:")
    kw4 = parseForKeywords(text,getTypeKey()) #,"TYP:")

    infos = kw1+kw2+kw3+kw4

    return infos

def parseForKeywords(text,keywords):
    lst =list()
    for k in keywords:
        kwv = generateKeyWordVariants(k)
        kwRes = re.findall(kwv,text)
        n = 0
        if kwRes is not None:
            n = len( kwRes )
        if(n>0):
            lst.append(k)
    return lst



def generateKeyWordVariants(keyw):
    #  ä ü ö -> alt a u o
    # ' ' or '-' -> \s{0,2}
    # ? \s+ between each letter?
    outstr = ""
    for c in keyw[0:len(keyw)-1:1]:
        outstr += c + "\s?" 
    outstr += keyw[len(keyw)-1]
    return outstr

def md5fromFile(fileNm):
    md5_hash = hashlib.md5()

    a_file = open(fileNm, "rb")

    content = a_file.read()

    md5_hash.update(content)
    a_file.close()

    digest = md5_hash.hexdigest()

    return digest


def parseForDates(text):
    dateLst = list()
    dateTimeLst = list()

    d1 = re.findall(getDatePattern1(),text)
    for d in d1:
        dateLst.append(d[0])
        dateTimeLst.append(str2date( d[0], 0 ))
    d2 = re.findall(getDatePattern2(),text)
    for d in d2:
        dateLst.append(d[0])
        dateTimeLst.append(str2date( d[0], 1 ))

    dateTimeLst.sort()

    return dateTimeLst

def str2date(str,typ):
    dt = date(1980, 1, 1)

    if( typ==0 ):
        splitres = re.findall(r'(\d{1,2})([.,]|\s)(\d{1,2})([.,]|\s)([1-2][0-9][0-2][0-9])',str)
        if(len(splitres)>0):
            #print(splitres[0])
            y = int(splitres[0][4])
            m = int(splitres[0][2])
            d = int(splitres[0][0])
            if(d<1 or d>31 or m<1 or m>12):
                return dt
            dt = date(y,m,d)
    elif(typ==1):
        dict1 = {"januar":1,"februar":2,"märz":3,"april":4,"mai":5,"juni":6,"juli":7,"august":8,"september":9,"oktober":10,"november":11,"dezember":12,"jan":1,"feb":2,"aug":8,"sept":9,"okt":10,"nov":11,"dez":12,"marz":4}
        splitres = re.findall(r'(?i)(\d{1,2})([.,]*)(\s{0,2})(Januar|Jan|Februar|Feb|März|Marz|April|Mai|Juni|Juli|August|Aug|September|Sept|Oktober|Okt|November|Nov|Dezember|Dez)([.,]*)(\s{0,2})([1-2][0-9][0-2][0-9])',str)
        if(len(splitres)>0):
            print(splitres[0])
            d = int(splitres[0][0])
            y = int(splitres[0][6])
            m = dict1[splitres[0][3].lower()]
            if(d<1 or d>31 or m<1 or m>12):
                return dt
            try:
                dt = date(y,m,d)
            except ValueError: # day too large for month...?
                dt = date(y,m,d-1)
    return dt



def getSauceKey():
    sauceKey = [
        "Gebühreneinzugszentrale",
        "badenova",
        "1&1",
        "Telef nica",
        "Kabel BW",
        "Alice",
        "Fonic",
        "Techniker Krankenkasse",
        "VG-Wort",
        "Deutsche Beamtenversicherung",
        "BBBank",
        "Badische Beamten Bank",
        "Landeskrankenhilfe",
        "Barmenia",
        "Badische Versicherungen",
        "Versorgungsanstalt",
        "DBV-winterthur",
        "IKK-Direkt",
        "Winfried Werne",
        "Stadt Freiburg",
        "Bundesagentur",
        "Auto Bayer",
        "Renault",
        "Strassenverkehrsamt",
        "dextra",
        "Maxblue",
        "Deustche Bank",
        "Deustche Post AG",
        "Hamilton Medical",
        "Shaker Verlag",
        "Universität Karlsruhe",
        "DHL Paket",
        "Europa Park",
        "DB Fernverkehr",
        "IEEE",
        "schufa",
        "Volksbank Offenburg",
        "Bundeswehrverband",
        "Sparkasse Offenburg",
        "DJH Hauptverband",
        "Cumulus",
        "Post CH",
        "SBB Contact center",
        "Aquilana",
        "diventa",
        "Allianz",
        "Gemeinde Felsberg",
        "UPC",
        "cablecom",
        "wingo",
        "gkb.ch",
        "Kantonalbank",
        "Swisscard",
        "COOP",
        "supercard",
        "cashback",
        "tscholl",
        "Rhiienergie",
        "ALID SUISSE",
        "AHV",
        "CAP Rechtsschutz",
        "VDE-suedbaden",
        "VDI",
        "World Vision",
        "Sammelbestätigung",
        "Sozialversicherung",
        "Renteninformation",
        "Rentenversicherung",
        "DecryptFailed",
        "ORCFailed"
    ]
    return sauceKey

def getPlaceKey():
    placeKey = [ 
        "Hochschule Furtwangen",
        "Fachhochschule Offenburg",
        "Universitätsklinikum"
    ]
    return placeKey

def getLivingKey():
    livingKey = [ 
        "Fehrenbachalle",
        "Sundgauallee",
        "Schutterstr",
        "Freiburg",
        "Under-Chrüzli",
        "Offenburg",
        "Furthwangen",
        "Felsberg",
        "Neried",
        "Graubünden"
    ]
    return livingKey

def getTypeKey():
    typeKey = [
        "Entgeldabrechnung",
        "Rechnung",
        "Erinnerung",
        "Mahnung",
        "Mietvertrag",
        "Kontoauszug",
        "4389670",
        "Abrechnung",
        "VISA",
        "Mastercard",
        "Kontoabschluss",
        "Depot"
        ]
    return typeKey


def getDatePattern1():
    # German date format numeric:
    datePattern1 = re.compile(
        r'((\d{1,2}([.,]|\s))' # day
        r'(\d{1,2}([.,]|\s))' # month
        r'((20[0-2][0-9])|(199[0-9])))' # year
        )
    return datePattern1

def getDatePattern2():
    # German date format Writtem months:
    datePattern2 = re.compile(
        r'(?i)((\d{1,2}([.,]*)(\s{0,2}))' # day
        r'(Januar|Jan|Februar|Feb|März|Marz|April|Mai|Juni|Juli|August|Aug|September|Sept|Oktober|Okt|November|Nov|Dezember|Dez)' 
        r'([.,]*)(\s{0,2})'
        r'((20[0-2][0-9])|(199[0-9])))' # year
        )
    return datePattern2
    # https://regexr.com/

# works in ubuntu 20 /mnt/c/Users/DSchwenn/Desktop/MyEIS/pycode  python ocr_test_01.py

if __name__ == '__main__':  # To ensure correct behavior on Windows and macOS
    #ocrmypdf.ocr('input.pdf', 'output.pdf', deskew=True, rotate_pages=True, language='deu+eng', sidecar='output.txt',clean=True,optimize=2)
    # https://ocrmypdf.readthedocs.io/en/v9.7.1/api.html


    outpFld = join(bseFolder,outFld)

    if( not os.path.exists(outpFld) ):
        os.mkdir(outpFld)

    if( not os.path.exists(tmpFolde) ):
        os.mkdir(tmpFolde)

    tmpPdfFile = join(join(bseFolder,tmpFolde), tmpPdfFile)
    tmpTxtFile = join(join(bseFolder,tmpFolde), tmpTxtFile)
    inpFld = join(bseFolder,inFld)
    
    listEntries = processFolderRecursive(inpFld,outpFld)

    file = open(join(bseFolder,resInfoListFile),mode='a')
    file.write(listEntries)
    file.close()

    # Check if theres text in the pdf - if so do not OCR, but check text for keywords only
    # https://betterprogramming.pub/how-to-convert-pdfs-into-searchable-key-words-with-python-85aab86c544f





#List: Scan date time, keywords, org filename, new filename, collected dates, subfolder, org and res c hecksum, processing date time, 
#List: Apparently empty files
