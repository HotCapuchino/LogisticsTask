from class_field import Field


class Task:
    __open_task = False
    __field = None
    __lifecycle_methods = None
    __demand_needs = []
    __supply_resources = []

    def __init__(self):
        self.__lifecycle_methods = [
            self.getDemand,
            self.getSupply,
            self.getPrices,
            self.defineTaskType,
            self.solveTask,
            self.showSolution
        ]

    def start(self, path=None):
        if not path:
            self.__lifecycle_methods[0]()
        else:
            self.__readFile(path)

    def __readFile(self, path):
        with open(path, 'r') as f:
            cons_num = int(f.readline()[:-1])
            if cons_num < 2:
                print('Make sure you have at least 2 consumers in your file!')
                return
            for i in range(cons_num):
                cons_demand = int(f.readline()[:-1])
                if cons_demand <= 0:
                    print('Demand can\'t be negative or equals to zero!')
                    return
                self.__demand_needs.append(cons_demand)
            provider_num = int(f.readline()[:-1])
            if provider_num < 2:
                print('Make sure Make sure you have at least 2 providers in your file!')
                return
            for i in range(provider_num):
                provider_supply = int(f.readline()[:-1])
                if provider_supply <= 0:
                    print('Supply can\'t be negative or equals to zero!')
                    return
                self.__supply_resources.append(provider_supply)
            prices_matrix = []
            for i in range(provider_num):
                prices = list(map(int, f.readline().strip().split(' ')))
                for price in prices:
                    if price <= 0:
                        print('Price can\'t be negative or equals zero!')
                        return
                if len(prices) != len(self.__demand_needs):
                    print(
                        f'Amount of prices should be equal to amount of consumers! Entered amount of prices: {len(prices)}, current amount of consumers: {len(self.__demand_needs)}')
                    return
                prices_matrix.append(prices)
            self.defineTaskType(prices_matrix)

    def __getNextLifecycleHook(self, ref):
        for i in range(len(self.__lifecycle_methods)):
            if ref == self.__lifecycle_methods[i]:
                if i == len(self.__lifecycle_methods) - 1: return None
                return self.__lifecycle_methods[i + 1]

    def getDemand(self):
        nextHook = self.__getNextLifecycleHook(self.getDemand)
        while True:
            demand_amount = int(input('Enter the number of consumers: '))
            if demand_amount >= 2:
                break
            else:
                print('It\'s too little! Try the number greater than 1!')
        for i in range(demand_amount):
            while True:
                demand = int(input(f'Enter demand of {i + 1} consumer: '))
                if demand > 0:
                    break
                else:
                    print('Demand can\'t be negative! Please, try again!')
            self.__demand_needs.append(demand)
        nextHook()

    def getSupply(self):
        nextHook = self.__getNextLifecycleHook(self.getSupply)
        while True:
            supply_amount = int(input('Enter the number of providers: '))
            if supply_amount >= 2:
                break
            else:
                print('It\'s too little! Try the number greater than 1!')
        for i in range(supply_amount):
            while True:
                supply = int(input(f'Enter the number of resources {i + 1} provider can supply: '))
                if supply > 0:
                    break
                else:
                    print('Supply can\'t be negative! Please, try again!')
            self.__supply_resources.append(supply)
        nextHook()

    def getPrices(self):
        nextHook = self.__getNextLifecycleHook(self.getPrices)
        prices_matrix = []
        print('Enter matrix of prices, use whitespace as separator:', end='\n')
        for i in range(len(self.__supply_resources)):
            correct = False
            while not correct:
                prices = list(map(int, input(f'{i + 1}:').strip().split(' ')))
                price_check = True
                for price in prices:
                    if price <= 0:
                        print('Price can\'t be negative or equals zero!')
                        price_check = False
                        break
                if not price_check: continue
                if len(prices) != len(self.__demand_needs):
                    print(
                        f'Amount of prices should be equal to amount of consumers! Entered amount of prices: {len(prices)}, current amount of consumers: {len(self.__demand_needs)}')
                    continue
                prices_matrix.append(prices)
                correct = True
        nextHook(prices_matrix)

    def defineTaskType(self, prices_matrix):
        nextHook = self.__getNextLifecycleHook(self.defineTaskType)
        self.__open_task = sum(self.__demand_needs) != sum(self.__supply_resources)
        rows = len(self.__supply_resources)
        cols = len(self.__demand_needs)
        if sum(self.__demand_needs) > sum(self.__supply_resources):
            rows += 1
            self.__supply_resources.append(sum(self.__demand_needs) - sum(self.__supply_resources))
            prices_matrix.append([0] * cols)
        elif sum(self.__demand_needs) < sum(self.__supply_resources):
            cols += 1
            self.__demand_needs.append(sum(self.__supply_resources) - sum(self.__demand_needs))
            for i in range(len(prices_matrix)):
                prices_matrix[i].append(0)
        self.__field = Field(rows, cols, prices_matrix, self.__demand_needs, self.__supply_resources)
        nextHook()

    def solveTask(self):
        nextHook = self.__getNextLifecycleHook(self.solveTask)
        while True:
            self.__field.leastCoefficientsMethod()
            if self.__field.calculateCellCoeffs():
                break
            if not self.__field.buildCycle():
                nextHook(False)
        nextHook(True)

    def showSolution(self, is_solved):
        if not is_solved:
            print('Seems like this task has no solution, or mb I\'m too dumb to solve it...')
            return
        schema, total_price = self.__field.getOptimalSchema()
        for sentence in schema:
            print(sentence)
        print(f'Total price of optimal logistics schema will be: {total_price}')
        return
