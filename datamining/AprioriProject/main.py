import json

from datamining.AprioriProject.Apriori import Apriori
from datamining.AprioriProject.cleanformat.CleanData import DataCleaner
from datamining.AprioriProject.util.MyTiming import MyTiming

csvFilePaht = "Base de Dados.csv"
#csvFilePaht = "input.csv"
t = MyTiming()


t.start_counting()
dc = DataCleaner(csvFilePaht, sep=',', decimal='.')
info = dc.generateStructuredTableInfo()


with open('tableData.json', 'w') as jsonFile:
    json.dump(info, jsonFile, indent=4, sort_keys=True)

df = dc.stripeTable()
df.to_csv('cleaned.csv', index=False)

print(df.head())

t.stop_counting()

print('Cleaning duration: {}'.format(t.countElapsed()))
t.resetTimer()

t.start_counting()


minsup = 0.95
minconf = 0.95

if input('Execute Apriori on cleaned data? with minsup={} and minconf={} (y/n)'.format(minsup, minconf)) == 'n':
    exit(0)

apr = Apriori(df, info, minsup=minsup, minconf=minconf, maxgroups=5)
#rules = apr.getAssociationRules()
rules = apr.getAssociationRulesWithMax(8)

print(apr.getInfoText())

i = 0
for rule in rules:
    print('#{} {}'.format(i, rule))
    i+=1


t.stop_counting()
print('Apriori duration: {}'.format(t.countElapsed()))