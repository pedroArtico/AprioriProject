from datamining.AprioriProject.util.ProgressBar import ProgressBar
from datamining.AprioriProject.util.RuleHandSize import RuleHandSize

from datamining.AprioriProject.util.AssociationRule import AssociationRule


#df = pd.read_csv('input.csv', sep=',')

class Apriori():
    def __init__(self, dataframe, descriptor, minsup, minconf, maxgroups):
        self.df = dataframe
        self.minsup = minsup
        self.minconf = minconf
        self.groups = maxgroups
        self.rows = self.df.shape[0]
        self.columns = self.df.shape[1]
        self.tbDescriptor = descriptor
        self.results = []

    #Confiança
    def confidence(self, tuparr) -> float:
        '''
        Confiança (X->Y) = Número de registros contendo X e Y / Número de registros contendo X
        Confiança (X->Y) = Sup(x,y)/ Sup(x)

        :param tuparr:
        :return:
        '''
        items0 = tuparr
        items1 = tuparr[:-1]
        #sup1Num = self.support(allItems)
        #sup2Den = self.support([ruleItem])

        #result1 = sup1Num / sup2Den

        sup1Num = self.matchLines(items0)
        sup2Den = self.matchLines(items1)

        #print('\nCalclulating {}'.format(tuparr))
        result = sup1Num / sup2Den
        return result

    def support(self, tupArr) -> float:
        '''
        Suporte (X->Y) = número de registros contendo X e Y / Total de registros
        O método recebe um vetor com tuplas: [(nome_da_coluna, valor_a_testar), ...]

        :param tupArr: vetor de tuplas no formato (nome_da_coluna, valor_a_testar)
        :return: suporte dos itens enviados
        '''
        totalRegisters = self.rows  # total de registros
        equal = self.matchLines(tupArr)
        return equal / totalRegisters #número de registros contendo X e Y / Total de registros

    def matchLines(self, tupArr):
        '''
        O método recebe um vetor com tuplas: [(nome_da_coluna, valor_a_testar), ...]
        É feita a contagem das linhas no dataset que contenham os valores a testar nas colunas indicadas

        :param tupArr: tupArr: vetor de tuplas no formato (nome_da_coluna, valor_a_testar)
        :return: quantas linhas do dataset tem os valores de entrada
        '''
        equal = 0  # contador de linhas com todos os registros enviados
        tableRows = self.df.iterrows()
        for line in tableRows:  # para cada linha do dataframe
            localEqual = 0
            for element in tupArr:  # para cada linha do vetor de tuplas
                templine = int(line[1][element[0]])  # Acessando valor da linha em uma das colunas a testar
                tempitem = int(element[1])  # acessando o valor submetido na tupla
                if templine == tempitem:  # se o valor na tabela e na tupla forem os mesmos
                    localEqual += 1  # existe uma igualdade local
                else:  # Caso contrário o valor na coluna não é igual ao da tupla, posso passar para a próxima linha
                    continue
            if localEqual == len(tupArr):  # se para cada elemento do vetor enviado existir uma igualdade na linha
                equal += 1  # a linha faz parte dos registros que contém X e y
        return equal


    def combineItemsets(self, itemset1, itemset2):
        answer = []
        for item1 in itemset1:
            for item2 in itemset2:
                answer.append([item1, item2])
        return answer

    def combineItemsets2(self, itemsetComposed, itemsetSimple):
        answer = []
        for element in itemsetComposed:
            for item in itemsetSimple:
                lstelem = list(element)
                lstelem.append(item)
                answer.append(lstelem)
        return answer

    def apriori(self):
        with open('rules.txt', 'w') as file:
            file.write('')

        firstItemset = []
        firstItemset2 = []
        processBuffer = []


        for column, elem in self.tbDescriptor.items():
            for delimiter, value in elem['groups'].items():
                firstItemset.append((column, int(delimiter)))

        for element in firstItemset:
            support = self.support([element])

            if support > self.minsup:
                firstItemset2.append(element)
                processBuffer.append(element)
                #self.results.append(
                #    AssociationRule([RuleHandSize(element[0], element[1])], RuleHandSize(element[0], element[1]), support, 0)
                #)

        for i in range(2, self.groups):
            if i > 2:
                combinations = self.combineItemsets2(processBuffer, firstItemset2)
            else:
                combinations = self.combineItemsets(processBuffer, firstItemset2)
            combinations = self.removeWrongRules(combinations)
            if combinations == []:
                break

            processBuffer = []


            print('\n\nPROCESSING RULES WITH {} ELEMENTS.'.format(i))
            pb = ProgressBar(len(combinations))
            for element in combinations:

                pb += 1

                sup = self.support(element)
                conf = self.confidence(element)

                rules = []
                for temp in element[:-1]:
                    rules.append(RuleHandSize(temp[0], temp[1]))

                if sup > self.minsup and conf > self.minconf:
                    processBuffer.append(element)

                    self.results.append(
                        AssociationRule(rules, RuleHandSize(element[-1][0], element[-1][1]),sup, conf)
                    )


        print('\n\n\n\n')

    def getAssociationRules(self):
        print('{:^50s}'.format('EXECUTING APRIORI ALGORITHM'))
        self.apriori()

        print('WRITING RESULTS TO A FILE')
        pb = ProgressBar(len(self.results))

        with open('rules.txt', 'w') as file:
            for rule in self.results:
                file.write('{}\n'.format(rule))
                pb+=1

        print('DONE.')
        print('\n\n\n')
        print('RULES FOUND: {}'.format(len(self.results)))

        return self.results


    def getAssociationRulesWithMax(self, wantedRules):
        sortedLst = self.getAssociationRulesSorted()
        if wantedRules > len(sortedLst):
            wantedRules = len(sortedLst)
        return sortedLst[0: wantedRules]

    def getAssociationRulesSorted(self):
        assocRules = self.getAssociationRules()
        sortedLst = sorted(assocRules, key=lambda elem: elem.sum, reverse=True)
        return sortedLst

    def toupleArrHasEqual(self, arr, pos):
        values = []
        for element in arr:
            if element[pos] in values:
                return True
            values.append(element[pos])
        return False


    def removeWrongRules(self, combs):
        answ = []
        for item in combs:
            if not self.toupleArrHasEqual(item, 0):
                answ.append(item)
        return answ

    def getInfoText(self):
        return 'minsup: [{}], minconf: [{}]'.format(self.minsup, self.minconf)





