import pytest

from bots.chemical_equation_balancing.balancer import balance_chemical_equation


@pytest.mark.parametrize("unbalanced_equation, balanced_equation_expected", [
    ("H2 + O2 -> H2O", "2H2 + O2 -> 2H2O"),
    ("CO2 + H2O -> C6H12O6 + O2", "6CO2 + 6H2O -> C6H12O6 + 6O2"),
    ("NaOH + H2CO3 -> Na2CO3 + H2O", "2NaOH + H2CO3 -> Na2CO3 + 2H2O"),
    ("C2H2 + O2 -> CO2 + H2O", "2C2H2 + 5O2 -> 4CO2 + 2H2O"),
    ("Rb + HNO3 -> RbNO3 + H2", "2Rb + 2HNO3 -> 2RbNO3 + H2"),
    ("Pt + HNO3 + HCl -> H2PtCl6 + NO2 + H2O", "Pt + 4HNO3 + 6HCl -> H2PtCl6 + 4NO2 + 4H2O"),
    ("S + HNO3 -> H2SO4 + NO2 + H2O", "S + 6HNO3 -> H2SO4 + 6NO2 + 2H2O"),
    ("ABCD -> A2B2 + C2D2", "2ABCD -> A2B2 + C2D2"),
    ("FeCl3 + HF -> FeF3 + HCl", "FeCl3 + 3HF -> FeF3 + 3HCl"),
])
def test_balance_chemical_equation(unbalanced_equation, balanced_equation_expected):
    balanced_equation = balance_chemical_equation(unbalanced_equation)

    assert balanced_equation == balanced_equation_expected

