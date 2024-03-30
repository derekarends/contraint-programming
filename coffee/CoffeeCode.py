from ortools.sat.python import cp_model

capacity_in_supplier = {'supplier1': 150, 'supplier2': 50, 'supplier3': 100}
shipping_cost_from_supplier_to_roastery = {
    ('supplier1', 'roastery1'): 5,
    ('supplier1', 'roastery2'): 4,
    ('supplier2', 'roastery1'): 6,
    ('supplier2', 'roastery2'): 3,
    ('supplier3', 'roastery1'): 2,
    ('supplier3', 'roastery2'): 7
}
roasting_cost_light = {'roastery1': 3, 'roastery2': 5}
roasting_cost_dark = {'roastery1': 5, 'roastery2': 6}
shipping_cost_from_roastery_to_cafe = {
    ('roastery1', 'cafe1'): 5,
    ('roastery1', 'cafe2'): 3,
    ('roastery1', 'cafe3'): 6,
    ('roastery2', 'cafe1'): 4,
    ('roastery2', 'cafe2'): 5,
    ('roastery2', 'cafe3'): 2
}
light_coffee_needed_for_cafe = {'cafe1': 20, 'cafe2': 30, 'cafe3': 40}
dark_coffee_needed_for_cafe = {'cafe1': 20, 'cafe2': 20, 'cafe3': 100}

model = cp_model.CpModel()

# Define Variables
delivery = {}
for key in shipping_cost_from_supplier_to_roastery.keys():
    delivery[key] = model.NewIntVar(0, cp_model.INT32_MAX, f"delivery_{key}")

light_vars = {}
for key in shipping_cost_from_roastery_to_cafe.keys():
    light_vars[key] = model.NewIntVar(0, cp_model.INT32_MAX, f"light_{key}")

dark_vars = {}
for key in shipping_cost_from_roastery_to_cafe.keys():
    dark_vars[key] = model.NewIntVar(0, cp_model.INT32_MAX, f"dark_{key}")

# Add expressions
roasters = list(set(i[1] for i in shipping_cost_from_supplier_to_roastery.keys()))
for r in roasters:
    expr = (sum(delivery[i] for i in shipping_cost_from_supplier_to_roastery if i[1] == r) ==
            sum(light_vars[j] + dark_vars[j] for j in shipping_cost_from_roastery_to_cafe if j[0] == r))
    model.Add(expr)

suppliers = list(set(i[0] for i in shipping_cost_from_supplier_to_roastery.keys()))
for s in suppliers:
    expr = sum(delivery[i] for i in shipping_cost_from_supplier_to_roastery if i[0] == s) <= capacity_in_supplier[s]
    model.Add(expr)

cafes = list(set(i[1] for i in shipping_cost_from_roastery_to_cafe.keys()))
for c in cafes:
    expr = sum(light_vars[j] for j in shipping_cost_from_roastery_to_cafe if j[1] == c) >= light_coffee_needed_for_cafe[
        c]
    model.Add(expr)

    expr = sum(dark_vars[j] for j in shipping_cost_from_roastery_to_cafe if j[1] == c) >= dark_coffee_needed_for_cafe[c]
    model.Add(expr)

# What do you want to optimize for?
optimize = (sum(delivery[i] * shipping_cost_from_supplier_to_roastery[i] for i in shipping_cost_from_supplier_to_roastery) +
            sum(roasting_cost_light[r] * light_vars[r, c] + roasting_cost_dark[r] * dark_vars[r, c] for r, c in shipping_cost_from_roastery_to_cafe) +
            sum((light_vars[j] + dark_vars[j]) * shipping_cost_from_roastery_to_cafe[j] for j in shipping_cost_from_roastery_to_cafe))

model.minimize(optimize)

# Get solver
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Check if solving was successful
if status == cp_model.OPTIMAL:
    print("Optimal solution found.")
    # Access objective value
    print("Objective value:", solver.ObjectiveValue())
    # Access individual shipping costs
    for s, expr_list in delivery.items():
        print(f"Delivery to Roaster {s}: {solver.Value(expr_list)}")
    for s, expr_list in light_vars.items():
        print(f"Delivery light to cafe {s}: {solver.Value(expr_list)}")
    for s, expr_list in dark_vars.items():
        print(f"Delivery dark to cafe {s}: {solver.Value(expr_list)}")
else:
    print("No solution found.")
