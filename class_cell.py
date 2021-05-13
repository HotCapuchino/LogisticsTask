class Cell:
    __empty = True
    __value = None
    __price = None
    __calculated_coeff = None
    __served = False
    __x = None
    __y = None

    def __init__(self, price, x, y, value=None):
        self.__price = price
        self.__x = x
        self.__y = y
        if value:
            self.__value = value
            self.__empty = False

    def setValue(self, new_value):
        if new_value is None:
            self.__empty = True
            self.__value = None
            return
        self.__value = new_value
        self.__calculated_coeff = None
        self.__empty = False

    def setCoeff(self, new_coeff):
        self.__empty = True
        self.__value = None
        self.__calculated_coeff = new_coeff

    def getPrice(self):
        return self.__price

    def getValue(self):
        return self.__value

    def getCoeff(self):
        return self.__calculated_coeff

    def setServed(self, served):
        self.__served = served

    def getX(self):
        return self.__x

    def getY(self):
        return self.__y

    def isEmpty(self):
        return self.__empty

    def isServed(self):
        return self.__served
