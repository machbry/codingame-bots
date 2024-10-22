from bots.chemical_equation_balancing.balancer import balance_chemical_equation

chemical_equation_repr = input()

# Write an answer using print
# print(f"{unbalanced}", file=sys.stderr, flush=True)

print(f"{balance_chemical_equation(chemical_equation_repr)}")
