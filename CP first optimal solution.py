#PYTHON 
from ortools.sat.python import cp_model


# Create the CP model
model = cp_model.CpModel()

# Input data
N, M = map(int, input().split())
d = list(map(int, input().split()))
c = list(map(int, input().split()))
K = int(input())

conflict = []
P = []

for k in range(K):
    i, j = map(int, input().split())
    conflict.append((i - 1, j - 1))
    conflict.append((j - 1, i - 1))

# Decision variables
s = [model.NewIntVar(0, N - 1, "s[%i]" % i) for i in range(N)]
y = [[model.NewIntVar(0, 1, "y[%i][%i]" % (i, j)) for j in range(M)] for i in range(N)]
timeslot = model.NewIntVar(0, N - 1, "timeslot")

# Constraints
for i, j in conflict:
    model.Add(s[i] != s[j])

for i in range(N):
    model.Add(timeslot >= s[i])

for i in range(N):
    model.Add(sum(y[i][j] * c[j] for j in range(M)) >= d[i])

for i in range(N):
    for j in range(N):
        if i == j:
            continue
        for k in range(M):
            b = model.NewBoolVar("b[%i][%i]" % (i, j))
            model.Add(s[i] == s[j]).OnlyEnforceIf(b)
            model.Add(s[i] != s[j]).OnlyEnforceIf(b.Not())
            model.Add(y[i][k] + y[j][k] <= 1).OnlyEnforceIf(b)

for i in range(N):
    model.Add(sum([y[i][j] for j in range(M)]) == 1)

# Objective function (Minimize the timeslot)
model.Minimize(timeslot)


# Create a solver
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    timeslot=[]
    for i in range(N):
        timeslot.append(solver.Value(s[i]))
    room=[]
    for i in range(N):
        for j in range(M):
            if solver.Value(y[i][j]) == 1:
                room.append(j)
    for i in range(N):
        print(i+1,timeslot[i]+1,room[i]+1)
else:
    print("No solution found.")