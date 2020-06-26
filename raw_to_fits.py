# coding:utf-8


import argparse
from math import *
import re

import numpy as np

from my_functions_2 import *


def getLsTpOptShape(strFilePath):
    rawFile = open(strFilePath, 'rb')
    arrRaw = np.fromfile(rawFile, "int16", -1)
    arrRaw.byteswap(True)
    rawLength = arrRaw.size
    initWidth = int(sqrt(rawLength))
    lsRet = []
    cnt = 0
    while True:
        width = int(initWidth + cnt)
        if rawLength % width == 0:
            lsRet.append((int(rawLength / width), width))
            lsRet.append((width, int(rawLength / width)))
        if width == rawLength:
            break
        cnt += 1
    return lsRet


parser = argparse.ArgumentParser(
    description='convert raw file to 2d fits file in a directory')
parser.add_argument('-i', '--input_directory', default='./', help='input directory path (init : ./)')
parser.add_argument('-w', '--width', help='width of output fits (init : None)')
parser.add_argument('-m', '--match_file_name', default='(.+)\.raw', help='file name as regular expression (init : (.+)\\.raw)')
parser.add_argument('-o', '--output_directory', help='directory_path (init : None)')
args = parser.parse_args()

strInputDirPath = args.input_directory
strOutputDirPath = args.output_directory
strMatchFileName = args.match_file_name
strWidth = args.width

strInputDirPath = getStrAbsPath(strInputDirPath)
if strInputDirPath[-1] != '/':
    strInputDirPath += '/'

if strOutputDirPath is None:
    strOutputDirPath = strInputDirPath
if strOutputDirPath[-1] != '/':
    strOutputDirPath += '/'

lsStrFileName = sorted(getLsStrFileName(strInputDirPath, match=strMatchFileName))
if len(lsStrFileName) <= 0:
    print('files are not found.')
    quit()

if strWidth is None:
    strFilePath = strInputDirPath + lsStrFileName[0]
    print('searching optimized width of ' + strFilePath + '...')
    lsTpOptShape = getLsTpOptShape(strFilePath)
    print('finished.')
    for cnt, tpOptShape in enumerate(lsTpOptShape):
        print(str(cnt) + ' : width=' + str(tpOptShape[1]) + ' (height=' + str(tpOptShape[0]) + ')')
    while True:
        strInput = input('select : ')
        match = re.match('\d+', strInput)
        if match is None:
            continue
        selectIndex = int(strInput)
        if selectIndex > len(lsTpOptShape):
            continue
        break
    width = lsTpOptShape[selectIndex][1]
else:
    width = int(strWidth)


for cnt in range(len(lsStrFileName)):
    strFileName = lsStrFileName[cnt]
    strFilePath = strInputDirPath + strFileName
    rawFile = open(strFilePath, 'rb')
    arrRaw = np.fromfile(rawFile, "int16", -1)
    if arrRaw.size % width != 0:
        prints(
            'ERROR',
            'in ' + strFileName,
            'invalid shape!',
            'length of raw file : ' + str(arrRaw.size)
            )
    arrRaw.byteswap(True)
    arrFits = arrRaw.reshape((int(arrRaw.size / width), width))
    match = re.match(strMatchFileName, strFileName)
    saveAsFits(arrFits, strOutputDirPath + match.group(1) + '.fits', message=True)
