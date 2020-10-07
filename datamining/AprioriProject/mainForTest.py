import json

import pandas as pd

from datamining.AprioriProject.Apriori import Apriori
from datamining.AprioriProject.util.MyTiming import MyTiming

csvFilePaht = "Base de Dados.csv"
#csvFilePaht = "input.csv"
t = MyTiming()

df = pd.read_csv('testing/cleaned_camolesi.csv')

with open('testing/tableData_camolesi.json') as file:
    info = json.load(file)


t.start_counting()

minsup = 0.23
minconf = 0.40

apr = Apriori(df, info, minsup=minsup, minconf=minconf, maxgroups=5)

#rules = apr.getAssociationRulesWithMax(20)
rules = apr.getAssociationRules()
print(apr.getInfoText())

i = 0
for rule in rules:
    print('#{} {}'.format(i, rule))
    i+=1
t.stop_counting()
print('Apriori processing time: {}'.format(t.countElapsed()))