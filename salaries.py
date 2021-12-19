from decimal import Decimal
from typing import List
import datetime as dt
import matplotlib.pyplot as plt

from irs import IRS, RETENTION


class IRSNotAvailable(Exception):
    pass


def irs(salary: Decimal, num_people=1) -> Decimal:
    """Returns the taxed amount for the specified salary according to this year's IRS
    brackets.

    Args:
        salary (d): Taxable income.
        num_people (int, optional): Number of people. Defaults to 1.

    Raises:
        IRSNotAvailable: Raised when the required year isn't available.

    Returns:
        d: Taxed value.
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

    tax = Decimal("0")
    salary /= num_people

    previous_ceiling = 0
    for ceiling, ptax in irs:
        if salary > ceiling:
            tax += Decimal(ceiling - previous_ceiling) * ptax
        else:
            tax += Decimal(salary - previous_ceiling) * ptax
            break
        previous_ceiling = ceiling

    tax *= num_people
    return tax.quantize(Decimal("0.01"))


class Income:
    SS = 4104
    ss_tax = Decimal("0.11")

    def __init__(self, salary=0, n_months=12, bonus=[], taxfree=0, n_people=1):
        self.income = Decimal(salary) * n_months + Decimal(sum(bonus))
        self.salary = Decimal(salary)
        self.bonus = [Decimal(b) for b in bonus]
        self.ss = self.income * self.ss_tax
        self.taxfree = Decimal(taxfree)
        self.n_people = n_people

        self.year = int(dt.datetime.now().strftime("%Y")) + 1

    def gross(self):
        return self.income

    def net(self):
        if self.SS * self.n_people > self.ss:
            collectable = self.income - self.SS * self.n_people
        else:
            collectable = self.income - self.ss
        tax = irs(collectable, self.n_people)

        return (self.income - self.ss - tax + self.taxfree).quantize(Decimal("0.01"))

    def netsalary(self):
        for ceiling, *ptax in RETENTION[self.year]:
            if self.salary < ceiling:
                return (self.salary * (1 - self.ss_tax - ptax[0])).quantize(
                    Decimal("0.01")
                )

    def netbonus(self):
        return [
            (bonus * (1 - self.ss_tax - ptax[0])).quantize(Decimal("0.01"))
            for bonus in self.bonus
            for ceiling, *ptax in RETENTION[self.year]
            if bonus < ceiling
        ]


class Graph:
    def __init__(
        self, income: List[Decimal], expenses: List[Decimal], invested=[0] * 12
    ):
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
