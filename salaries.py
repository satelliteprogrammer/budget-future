import datetime as dt
import matplotlib.pyplot as plt

from irs import IRS, RETENTION


class IRSNotAvailable(Exception):
    pass


def irs(salary, num_people=1) -> float:
    """Returns the taxed amount for the specified salary according to this year's IRS
    brackets.

    Args:
        salary: Taxable income.
        num_people (int, optional): Number of people. Defaults to 1.

    Raises:
        IRSNotAvailable: Raised when the required year isn't available.

    Returns:
        float: Taxed value.
    """
    current = False
    year = int(dt.datetime.now().strftime("%Y"))
    while not current:
        if current := (year in IRS):
            irs = IRS[year]
        else:
            year -= 1
            if year < IRS.keys()[-1]:
                raise IRSNotAvailable

    tax = 0
    salary /= num_people

    previous_ceiling = 0
    for ceiling, ptax in irs:
        if salary > ceiling:
            tax += (ceiling - previous_ceiling) * ptax
        else:
            tax += (salary - previous_ceiling) * ptax
            break
        previous_ceiling = ceiling

    tax *= num_people
    return round(tax, 2)


class Income:
    SS = 4104
    ss_tax = 0.11

    def __init__(self, salary=0, n_months=12, bonus=[], taxfree=0, n_people=1):
        self.income = salary * n_months + sum(bonus)
        self.salary = salary
        self.bonus = bonus
        self.ss = self.income * self.ss_tax
        self.taxfree = taxfree
        self.n_people = n_people

        self.year = int(dt.datetime.now().strftime("%Y")) + 1

    def gross(self):
        return round(self.income, 2)

    def net(self):
        if self.SS * self.n_people > self.ss:
            collectable = self.income - self.SS * self.n_people
        else:
            collectable = self.income - self.ss
        tax = irs(collectable, self.n_people)

        return round(self.income - self.ss - tax + self.taxfree, 2)

    def netsalary(self):
        for ceiling, *ptax in RETENTION[self.year]:
            if self.salary < ceiling:
                return round(self.salary * (1 - self.ss_tax - ptax[0]), 2)

    def netbonus(self):
        return [
            round(bonus * (1 - self.ss_tax - ptax[0]), 2)
            for bonus in self.bonus
            for ceiling, *ptax in RETENTION[self.year]
            if bonus < ceiling
        ]


class Graph:
    def __init__(self, income: list, expenses: list, invested=[0] * 12):
        assert len(income) == 12
        assert len(expenses) == 12
        assert len(invested) == 12

        net = [i - e - c for i, e, c in zip(income, expenses, invested)]
        accum = net[0]
        self.accum = []
        for i in range(12):
            accum += net[i]
            self.accum.append(accum)

        self.income = income
        self.expenses = [-e for e in expenses]
        self.invested = invested

    def plot(self):
        plt.plot(range(1, 13), self.income, "g", label="Income")
        plt.plot(range(1, 13), self.expenses, "r", label="Expenses")
        if any(self.invested):
            plt.plot(range(1, 13), self.invested, "y", label="Investments")
        plt.plot(range(1, 13), self.accum, "b", label="Accumulative")
        plt.grid()
        plt.legend()
        plt.show()
