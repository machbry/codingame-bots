import numpy as np
import re
from dataclasses import dataclass, field
from scipy.linalg import null_space

@dataclass
class Context:
    elements_index: list[str] = field(default_factory=list)

class Molecule:

    def __init__(self, representation: str, coefficient: int=1, reagent_or_product: int=1, context: Context=Context()):
        self.representation = representation
        self.coefficient = coefficient
        self.reagent_or_product = reagent_or_product
        self.context = context
        self.elements: dict[str, int] = {}
        self._init_elements()

    def _init_elements(self):
        matches = re.findall('([A-Z][a-z]*)(\\d*)', self.representation)
        for element, count in matches:
            count = int(count) if count else 1
            if not self.elements.get(element):
                self.elements[element] = 0
            self.elements[element] += count
            if element not in self.context.elements_index:
                self.context.elements_index.append(element)

    def __str__(self):
        if self.coefficient == 1:
            return self.representation
        return f'{self.coefficient}{self.representation}'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.representation == other
        return self.representation == other.representation and self.coefficient == other.coefficient

class Formula:

    def __init__(self, representation: str, reagents_or_products: int=1, context: Context=Context()):
        self.representation = representation
        self.reagents_or_products = reagents_or_products
        self.context = context
        self.molecules: list[Molecule] = []
        self._init_molecules()

    def _init_molecules(self):
        formula_parts = [part.strip() for part in self.representation.split('+')]
        for weighted_molecule in formula_parts:
            match = re.match('(\\d*)\\s*([A-Za-z0-9]+)', weighted_molecule)
            if match:
                coefficient, molecule_repr = match.groups()
                coefficient = int(coefficient) if coefficient else 1
                self.molecules.append(Molecule(representation=molecule_repr, coefficient=coefficient, reagent_or_product=self.reagents_or_products, context=self.context))

    def __str__(self):
        return ' + '.join([str(molecule) for molecule in self.molecules])

    def __repr__(self):
        return str(self)

class ChemicalEquation:

    def __init__(self, representation: str):
        self.context = Context()
        equation_parts = representation.split('->')
        self.reagents = Formula(representation=equation_parts[0].strip(), reagents_or_products=1, context=self.context)
        self.products = Formula(representation=equation_parts[1].strip(), reagents_or_products=-1, context=self.context)

    @property
    def all_molecules(self) -> list[Molecule]:
        return [*self.reagents.molecules, *self.products.molecules]

    @property
    def elements_molecules_matrix(self):
        matrix = []
        for molecule in self.all_molecules:
            molecule_column = [0 for _ in self.context.elements_index]
            for element, count in molecule.elements.items():
                molecule_column[self.context.elements_index.index(element)] = molecule.reagent_or_product * count
            matrix.append(molecule_column)
        return np.array(matrix).T

    def __str__(self):
        return f'{self.reagents} -> {self.products}'

    def __repr__(self):
        return str(self)

def balance_chemical_equation(chemical_equation_repr: str) -> str:
    chemical_equation = ChemicalEquation(chemical_equation_repr)
    equation_matrix = chemical_equation.elements_molecules_matrix
    equation_coefficients_raw = np.abs(null_space(equation_matrix))
    min_coefficient = np.min(equation_coefficients_raw)
    k = 1
    all_coefficients_integer = False
    while k <= 100 and (not all_coefficients_integer):
        equation_coefficients_scaled = k * equation_coefficients_raw * (1 / min_coefficient)
        all_coefficients_integer = np.abs(np.round(equation_coefficients_scaled, 100) - np.round(equation_coefficients_scaled)).sum() < 1 / 100
        k += 1
    equation_coefficients = np.round(equation_coefficients_scaled).astype(int)
    for i, molecule in enumerate(chemical_equation.all_molecules):
        molecule.coefficient = equation_coefficients[i][0]
    return str(chemical_equation)
chemical_equation_repr = input()
print(f'{balance_chemical_equation(chemical_equation_repr)}')