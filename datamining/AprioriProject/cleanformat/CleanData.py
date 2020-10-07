import json
import math
import pprint

import numpy as np
import pandas as pd

from datamining.AprioriProject.util.FileRenamer import FileRenamer as Fr


class DataCleaner:
    def __init__(self, inputFileName = "in.csv",jsonInfoFile = 'info.json', outputFileName = "out.csv", sep = ';', decimal = ','):
        self.inputFileName = inputFileName
        self.jsonInfoFile = jsonInfoFile
        self.outputFileName = outputFileName
        self.df = pd.read_csv(inputFileName, sep=sep, decimal=decimal)
        self.groupsAsTouples = {}
        self.dataDivisionThresholdPercent = 0.01


    def nogetNumberOfIntervals(self, columnName):
        if np.issubdtype(self.df[columnName].dtype, np.number):
            stdDeviation = self.df[columnName].std()
            max = self.df[columnName].max()
            min = self.df[columnName].min()

            result = math.floor((max-min) / stdDeviation)
            if result <= 1:
                result += 1

            return result
        else:
            return 0


    def nogetIntervalLayout(self, columnName, lastMax):
        intervals = 20
        intevalAnswer = []
        if intervals != 0:
            lastMax = int(lastMax)
            beginCount = lastMax + (10 - (lastMax % 10))

            maxv = self.df[columnName].max()
            minv = self.df[columnName].min()
            totalSum = self.df[columnName].sum()
            stdDeviation = self.df[columnName].std()
            avg  = self.df[columnName].mean()

            i = 0
            for i in range(intervals):
                a = beginCount + i
                b = minv + ((i+1) * (avg / (intervals/2)))
                intevalAnswer.append((str(a), b))
                i += 1

            a = beginCount + i
            b = maxv + 1
            intevalAnswer.append((str(a), b))

            #intervalList = {str(key): value for key, value in intervalList.items()}
            text = str(pprint.pformat(intevalAnswer))
            text = text.replace(',\n', '')
            print(text)

            self.groupsAsTouples[columnName] = intevalAnswer
            return dict(intevalAnswer)
        return None

    def getIntervalLayout(self, columnName, lastMax):
        intevalAnswer = []
        lastMax = int(lastMax)
        beginCount = lastMax + (10 - (lastMax % 10))

        maxv = self.df[columnName].max()
        minv = self.df[columnName].min()
        #totalSum = self.df[columnName].sum()
        stdDeviation = self.df[columnName].std()
        mean = self.df[columnName].mean()
        #dfSorted = self.df[columnName].sort_values()

        coefVariacao = (stdDeviation / mean / 100)

        intervals = math.floor(coefVariacao * 10) * 5

        if intervals <= 0:
            intervals = 1
        i = 0
        for i in range(intervals):
            a = beginCount + i
            b = minv + ((i + 1) * (mean / (intervals / 2)))
            intevalAnswer.append((str(a), b))
            i += 1

        a = beginCount + i
        b = maxv + 1
        intevalAnswer.append((str(a), b))

        text = str(pprint.pformat(intevalAnswer))
        text = text.replace(',\n', '')
        print(text)

        self.groupsAsTouples[columnName] = intevalAnswer
        return dict(intevalAnswer)



    def generateStructuredTableInfo(self):
        answ = {}
        lastMax = -1

        for columnName in self.df:
            column = self.df[columnName]
            if np.issubdtype(column.dtype, np.number):
                mean = float(column.mean())
                variance = float(column.var())
                stdDeviation = float(column.std())
                maxValue = float(column.max())
                minValue = float(column.min())

                interval = self.getIntervalLayout(column.name, lastMax)

                tempLst = []
                for item in self.groupsAsTouples[columnName]:
                    tempLst.append(item[0])
                lastMax = max(tempLst)
                print('Max = {}'.format(lastMax))

                temp = {"max": maxValue,"min": minValue,"mean": mean,"stddev": stdDeviation,"variance": variance,"groups": interval }
                #pprint(temp)
                answ[column.name] = temp
        return answ


    def tableInfoToJson(self):
        content = self.generateStructuredTableInfo()
        with open('data.json', 'w', encoding='utf8') as outfile:
            json.dump(content, outfile)

    def addZscoreNDumps(self):
        cols = list(self.df.columns)

        for column in cols:
            if not np.issubdtype(self.df[column].dtype, np.number):
                cols.remove(column)

        for col in cols:
            #colInfo = content[col]

            col_zscore = col + '_zscore'
            self.df[col_zscore] = (self.df[col] - self.df[col].mean())/self.df[col].std(ddof=0) #computes the z-score

            #for key, value in colInfo['groups'].values():
            #    pass

            self.df.to_csv(Fr(self.inputFileName).appendNameAtEnd('_zscored'))


    def stripeTable(self, ):
        #content = self.generateStructuredTableInfo()
        newData = {}

        print(self.groupsAsTouples)

        for rowname in self.df:
            newColumn = []

            print('Testing values from {}'.format(rowname))
            for data in self.df[rowname]:
                groupData = self.groupsAsTouples[rowname]
                for item in groupData:
                    groupLabel = item[0]
                    groupMin = item[1]

                    #print('{:.2f} < {:.2f} ?   :   '.format(data, groupMin), end='')
                    if data < groupMin:
                        newColumn.append(groupLabel)

                        #print('True')
                        break
                    #print('False')

            newData[rowname] = newColumn

        print(newData)

        df2 = pd.DataFrame(newData)
        #print(df2)


        df2.to_csv('cleaned.csv')
        return df2









