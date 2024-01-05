'''
This is the (general) coding for our final project, which consumes several csvs
with the same number of rows. Each row represents an variale, each col represents
a factor. The first row and the first col are their corresponding names.
varible LIN defines the linearly of our project. If LIN == 1, our program is linear.
If LIN != 1, every variable is binary.
'''

## Variables start with lowercase letters are local.
# is linear?
LIN = 0
# {name of factor: [(≤: -1, ≥: 1), RHS]}
Constraints = {"FG":[1, 980], "3P":[1, 260], "2P":[1,730], "FT":[1, 380], 
               "ORB":[1, 300], "DRB":[1, 760], "TRB":[1,1160], "AST":[1, 660], 
               "STL":[1, 190], "BLK":[1, 110], "TOV":[1,325], "PF":[1, 420], 
               "PTS":[1, 2580]}

Positions = {}

# Uncertainty set
## We assume r = 0.25 * RHS for each factor
E = {}
for i in Constraints:
    E[i] = Constraints[i][1] * 0.2

# consraint csv
consraint_csv = "Players_with_Salary.csv"

# objective csv
objective_csv = "Salary.csv"

# import Gurobipy
from gurobipy import *
import gurobipy as gp
import math

# define a model m
m = Model("robust_final_project")

# imort csv
import csv

'''
Our general sketch:
    add each row of csv as a variable
    add each selected col of csv as a constraint
'''

# Set NonConvex parameter to 2
m.setParam("NonConvex", 2)

# create a dictonary of variables
Var = {}
with open(consraint_csv, encoding='UTF8') as csvfile_r:
    Data = {}
    ## the first row of csv file
    csvreader = csv.reader(csvfile_r)
    Factors = next(csvreader)
    ## read the whold csv and meanwhile create variables
    for row in csvreader:
        if row == []:
            None
        else:
            name = row[0]
            if LIN == 0:
                variable = m.addVar(vtype = gp.GRB.BINARY, name = name)
            else:
                variable = m.addVar(name = name)
            Var[name] = variable
            Data[name] = row

# find the cols each element in Constraint lives
Selected_col = {}
selected_factors = list(Constraints.keys())   ## this is local
i = 0
while i < len(Factors):
    factor = Factors[i]     ## this is local
    if factor in selected_factors:
        Selected_col[factor] = i
    i += 1
print("-----constraint file opened-----")

# limit the number of players
m.addConstr(quicksum(Var[i] for i in Var)<=20, name = "max number of players")
# calculate Norm 
Norm = m.addVar(name = "Norm")
## Since variables are all binary, Norm * Norm == sum(x_i) for all i
m.addConstr(Norm * Norm - quicksum(Var[i] for i in Var) == 0, name = "Define Norm")

# run optimization
for factor in list(Constraints.keys()):
    col = Selected_col[factor]
    m.addConstr(
        -1 * quicksum(Data[i][col] * Var[i] for i in list(Data.keys()) if Data[i][col] != "") 
        * Constraints[factor][0] 
        +1 * Constraints[factor][0] * E[factor] * Norm
        <= -1 * Constraints[factor][0] * Constraints[factor][1], name = factor)

# position constraints
for pos in Positions:
    Names = Positions[pos]
    m.addConstr(quicksum(Var[i] for i in Names) <= 3, name = name)   
    m.addConstr(2 <= quicksum(Var[i] for i in Names), name = name) 

# create objective function file

Obj = {}
with open(objective_csv, encoding='UTF8') as csvfile_r:
    csvreader = csv.reader(csvfile_r)
    next(csvreader)
    i = 1
    for row in csvreader:
        if row[1] != "":
            Obj[row[0]] = row[1]
            i += 1
print("-----objective file opened-----")   

# add objective fucntions
m.setObjective(quicksum(Var[i] * Obj[i] for i in list(Var.keys())), GRB.MINIMIZE)

m.optimize()
m.printAttr("X")


# return LP file of m
m.write("robust_m.lp")