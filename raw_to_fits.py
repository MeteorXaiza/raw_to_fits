# coding:utf-8


import argparse

from xaizalibs.CMOSanalyzerlib import *


print('ver_2.0.0')

class Manager():
    def __init__(self):
        self.config = Config()
    def main(self):
        def getArrRaw(strInputFileAbsPath):
            print('loading ' + strInputFileAbsPath + '...')
            rawFile = open(strInputFileAbsPath, 'rb')
            print('finished.')
            arrRaw = np.fromfile(rawFile, "int16", -1)
            arrRaw.byteswap(True)
            return arrRaw
        mkdirs(
            genLsStrDirPathAndFileName(
                self.config.lsStrOutputFileAbsPath[0])[0])
        for cnt in range(len(self.config.lsStrInputFileAbsPath)):
            arrRaw = getArrRaw(self.config.lsStrInputFileAbsPath[cnt])
            if self.config.width is None:
                self.config.defineWidthFromLength(arrRaw.size)
            if arrRaw.size % self.config.width != 0:
                print(
                    'can\'t transfer '
                    + self.config.lsStrInputFileAbsPath[cnt] + ' by '
                    + str(self.config.width) + ' as ...')
                continue
            arrFits = arrRaw.reshape(
                (int(arrRaw.size / self.config.width), self.config.width))
            saveAsFits(
                arrFits, self.config.lsStrOutputFileAbsPath[cnt], message=True)
            print('')


class Config():
    def __init__(self):
        self.lsStrInputFileAbsPath = None
        self.lsStrOutputFileAbsPath = None
        self.width = None
        self.set()
    def set(self):
        parser = argparse.ArgumentParser(
            description='convert raw file to 2d fits file in a directory')
        parser.add_argument('-i', '--input_directory', default='./', help='input directory path (init : ./)')
        parser.add_argument('-m', '--match_file_name', default='.+\.raw', help='file name as regular expression (init : .+\\.raw)')
        parser.add_argument('-w', '--width', help='width of output fits (init : None)')
        parser.add_argument('-o', '--output_directory', help='directory_path (init : None)')
        args = parser.parse_args()
        strInputDirAbsPath = getStrAbsPath(args.input_directory)
        strOutputDirAbsPath = getStrAbsPath(args.output_directory)
        if strOutputDirAbsPath[-1] != '/':
            strOutputDirAbsPath += '/'
        print(strInputDirAbsPath, strOutputDirAbsPath)
        lsStrInputFileName = sorted(
            getLsStrFileName(strInputDirAbsPath, match=args.match_file_name))
        self.lsStrInputFileAbsPath = []
        self.lsStrOutputFileAbsPath = []
        for strInputFileName in lsStrInputFileName:
            self.lsStrInputFileAbsPath.append(
                strInputDirAbsPath + strInputFileName)
            match = re.match('(.+)\..+?', strInputFileName)
            if match is not None:
                strOutputFileName = match.group(1) + '.fits'
            else:
                strOutputFileName = strInputFileName + '.fits'
            self.lsStrOutputFileAbsPath.append(
                strOutputDirAbsPath + strOutputFileName)
        if args.width is not None:
            self.width = int(args.width)
    def defineWidthFromLength(self, length):
        def getLsTpOptShape(length):
            initWidth = int(sqrt(length))
            lsRet = []
            cnt = 0
            while True:
                width = int(initWidth + cnt)
                if length % width == 0:
                    lsRet.append((int(length / width), width))
                    lsRet.append((width, int(length / width)))
                if width == length:
                    break
                cnt += 1
            return lsRet
        print('searching optimized width...')
        lsTpOptShape = getLsTpOptShape(length)
        print('finished.')
        for cnt, tpOptShape in enumerate(lsTpOptShape):
            print(
                str(cnt) + ' : width=' + str(tpOptShape[1]) + ' (height='
                + str(tpOptShape[0]) + ')')
        strSelectIndex = getStrSelect(
            strMessage='select : ',
            lsStrValid=list(range(len(lsTpOptShape))))
        self.width = lsTpOptShape[int(strSelectIndex)][1]


manager = Manager()
manager.main()
