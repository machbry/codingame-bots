import numpy as np

from scipy.linalg import null_space

from bots.chemical_equation_balancing.assets import ChemicalEquation


def balance_chemical_equation(chemical_equation_repr: str) -> str:

    chemical_equation = ChemicalEquation(chemical_equation_repr)
    equation_matrix = chemical_equation.elements_molecules_matrix

    equation_coefficients_raw = np.abs(null_space(equation_matrix))
    min_coefficient = np.min(equation_coefficients_raw)

    k = 1
    all_coefficients_integer = False

    while k <= 100 and not all_coefficients_integer:
        equation_coefficients_scaled = k * equation_coefficients_raw * (1 / min_coefficient)
        all_coefficients_integer = np.abs(np.round(equation_coefficients_scaled, 100) - np.round(equation_coefficients_scaled)).sum() < 1 / 100
        k += 1

    equation_coefficients = np.round(equation_coefficients_scaled).astype(int)

    for i, molecule in enumerate(chemical_equation.all_molecules):
        molecule.coefficient = equation_coefficients[i][0]

    return str(chemical_equation)
