import pytest

from bots.chemical_equation_balancing.assets import Molecule, Formula, ChemicalEquation, Context


@pytest.mark.parametrize("molecule_repr, elements_expected", [
    ("H2", {"H": 2}),
    ("NaOH", {"Na": 1, "O": 1, "H": 1}),
    ("H2CO3", {"H": 2, "C": 1, "O": 3}),
    ("S", {"S": 1}),
])
def test_molecule(molecule_repr, elements_expected):
    molecule = Molecule(molecule_repr)

    assert molecule.elements == elements_expected


@pytest.mark.parametrize("formula_repr, molecules_expected", [
    ("H2 + O2", [Molecule("H2", 1), Molecule("O2", 1)]),
    ("Na2CO3 + H2O", [Molecule("Na2CO3", 1), Molecule("H2O", 1)]),
    ("H2SO4 + NO2 + H2O", [Molecule("H2SO4", 1), Molecule("NO2", 1), Molecule("H2O", 1)]),
    ("H20", [Molecule("H20", 1)]),
    ("2H2 + O2", [Molecule("H2", 2), Molecule("O2", 1)]),
    ("3Na2CO3 + 4H2O", [Molecule("Na2CO3", 3), Molecule("H2O", 4)]),
    ("2H2SO4 + 15NO2 + H2O", [Molecule("H2SO4", 2), Molecule("NO2", 15), Molecule("H2O", 1)]),
    ("3H20", [Molecule("H20", 3)]),
])
def test_formula(formula_repr, molecules_expected):
    formula = Formula(formula_repr)

    assert formula.molecules == molecules_expected


@pytest.mark.parametrize("chemical_equation_repr", [
    "S + HNO3 -> H2SO4 + NO2 + H2O",
    "S + 6HNO3 -> H2SO4 + 6NO2 + 2H2O",
    "ABCD -> A2B2 + C2D2"
])
def test_chemical_equation(chemical_equation_repr):
    chemical_equation = ChemicalEquation(chemical_equation_repr)

    assert str(chemical_equation) == chemical_equation_repr
