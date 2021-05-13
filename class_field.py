from class_cell import Cell
import numpy as np


class Field:
    __cells = []
    __rows = 0
    __cols = 0
    __demand = None
    __supply = None
    __u_coefficients = None
    __v_coefficients = None

    def __init__(self, rows, cols, prices_matrix, demand, supply):
        self.__rows = rows
        self.__cols = cols
        self.__u_coefficients = [None] * self.__rows
        self.__v_coefficients = [None] * self.__cols
        self.__u_coefficients[0] = 0
        self.__demand = demand
        self.__supply = supply
        self.__fillTheField(prices_matrix)

    def __fillTheField(self, matrix):
        self.__cells = []
        for i in range(self.__rows):
            row = []
            for j in range(self.__cols):
                row.append(Cell(matrix[i][j], j, i))
            self.__cells.append(row)

    def __isDegenerate(self):
        filled_cells_amount = 0
        for cell in np.array(self.__cells).flatten():
            if not cell.isEmpty():
                filled_cells_amount += 1
        return self.__rows + self.__cols - 1 != filled_cells_amount

    def __fixDegenerativity(self):
        vector = [1, 0, -1, 0]
        target_x, target_y = None, None
        for cell in np.array(self.__cells).flatten():
            if not cell.isEmpty() and cell.getValue() == self.__supply[cell.getY()]:
                target_x, target_y = cell.getX(), cell.getY()
                break
        extra_cell = None
        min_price = 10 ** 10  # just big value
        for i in range(len(vector)):
            for j in range(len(vector)):
                try:
                    if target_y + vector[i] == target_y and target_x + vector[j] == target_x:
                        continue
                    current_cell = self.__cells[target_y + vector[i]][target_x + vector[j]]
                    if not current_cell.isEmpty():
                        continue
                    if current_cell.getPrice() <= min_price:
                        min_price = current_cell.getPrice()
                        extra_cell = current_cell
                except IndexError:
                    pass
        extra_cell.setValue(0)

    def leastCoefficientsMethod(self):
        prices_desc = sorted((np.array(self.__cells)).flatten(), key=lambda cell: cell.getPrice())
        supply, demand = self.__supply[:], self.__demand[:]
        for cell in prices_desc:
            if cell.isServed():
                continue
            x = cell.getX()
            y = cell.getY()
            # if supply is greater than demand
            if supply[y] > demand[x]:
                cell.setValue(demand[x])
                supply[y] -= demand[x]
                demand[x] = 0
                for i in range(self.__rows):
                    self.__cells[i][x].setServed(True)
            # if demand is greater than supply
            elif supply[y] < demand[x]:
                cell.setValue(supply[y])
                demand[x] -= supply[y]
                supply[y] = 0
                for row_cell in self.__cells[y]:
                    row_cell.setServed(True)
            # if supply equals to demand
            elif supply[y] == demand[x]:
                cell.setValue(supply[y])
                demand[x], supply[y] = 0, 0
                for i in range(self.__rows):
                    self.__cells[i][x].setServed(True)
                for row_cell in self.__cells[y]:
                    row_cell.setServed(True)
        if self.__isDegenerate():
            self.__fixDegenerativity()

    def calculateCellCoeffs(self):
        self.__calculateUVCoeffs(True, 0)
        is_solved = True
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__cells[i][j].isEmpty():
                    coeff = self.__cells[i][j].getPrice() - (self.__u_coefficients[i] + self.__v_coefficients[j])
                    if coeff < 0:
                        is_solved = False
                    self.__cells[i][j].setCoeff(coeff)
        return is_solved

    def __calculateUVCoeffs(self, row, index):
        if row:
            for i in range(self.__cols):
                if not self.__cells[index][i].isEmpty() and not self.__v_coefficients[i]:
                    self.__v_coefficients[i] = self.__cells[index][i].getPrice() - self.__u_coefficients[index]
                    self.__calculateUVCoeffs(False, i)
        else:
            for j in range(self.__rows):
                if not self.__cells[j][index].isEmpty() and not self.__u_coefficients[j]:
                    self.__u_coefficients[j] = self.__cells[j][index].getPrice() - self.__v_coefficients[index]
                    self.__calculateUVCoeffs(True, j)
        return

    def __findStartCellForCycle(self):
        min_coeff = 0
        min_coeff_cell_options = None
        for i in range(self.__rows):
            for j in range(self.__cols):
                if self.__cells[i][j].isEmpty():
                    cell = self.__cells[i][j]
                    if cell.getCoeff() < min_coeff:
                        min_coeff = cell.getCoeff()
                        min_coeff_cell_options = (cell.getX(), cell.getY())
        return min_coeff_cell_options

    def __findPath(self, column, path, visited, start_x, start_y, current_x, current_y):
        if column:
            if current_x == start_x and len(path) % 2 == 0 and len(path) > 2:
                return True
            for j in range(self.__rows):
                if self.__cells[j][current_x] not in visited and not self.__cells[j][current_x].isEmpty():
                    visited.append(self.__cells[j][current_x])
                    path.append(self.__cells[j][current_x])
                    if self.__findPath(False, path, visited, start_x, start_y, current_x, j):
                        return True
                    else:
                        path.pop()
        else:
            if current_y == start_y and len(path) % 2 == 0 and len(path) > 2:
                return True
            for i in range(self.__cols):
                if self.__cells[current_y][i] not in visited and not self.__cells[current_y][i].isEmpty():
                    visited.append(self.__cells[current_y][i])
                    path.append(self.__cells[current_y][i])
                    if self.__findPath(True, path, visited, start_x, start_y, i, current_y):
                        return True
                    else:
                        path.pop()
        return False

    def buildCycle(self):
        start_x, start_y = self.__findStartCellForCycle()
        path = [self.__cells[start_y][start_x]]
        visited = [self.__cells[start_y][start_x]]
        column_result = self.__findPath(True, path, visited, start_x, start_y, start_x, start_y)
        if not column_result:
            path = [self.__cells[start_y][start_x]]
            visited = [self.__cells[start_y][start_x]]
            row_result = self.__findPath(False, path, visited, start_x, start_y, start_x, start_y)
            if not row_result:
                return False
        theta = None
        for i in range(len(path)):
            if i % 2 > 0:
                if not theta:
                    theta = path[i].getValue()
                if path[i].getValue() < theta:
                    theta = path[i].getValue()
        for i in range(len(path)):
            if i % 2 == 0:
                if path[i].isEmpty():
                    path[i].setValue(theta)
                else:
                    path[i].setValue(path[i].getValue() + theta)
            else:
                new_value = None if path[i].getValue() - theta == 0 else path[i].getValue() - theta
                path[i].setValue(new_value)
        return True

    def getOptimalSchema(self):
        schema = []
        total_price = 0
        for i in range(self.__rows):
            for j in range(self.__cols):
                if not self.__cells[i][j].isEmpty() and self.__cells[i][j].getValue() != 0:
                    schema.append(
                        f'You should take {self.__cells[i][j].getValue()} amount of product from {i + 1} provider and deliver it to the {j + 1} consumer!')
                    total_price += self.__cells[i][j].getValue() * self.__cells[i][j].getPrice()
        return schema, total_price
