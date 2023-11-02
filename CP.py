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


# Define a solution printer to print all solutions
class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, s, y, timeslot):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__s = s
        self.__y = y
        self.__timeslot = timeslot
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        room = []
        for j in range(M):
            for i in range(N):
                if self.Value(self.__y[i][j]) == 1:
                    room.append(j)
        print(f"Solution {self.__solution_count}:")
        for i in range(N):
            print(
                f"Course {i + 1} - Start Slot: {self.Value(self.__s[i])%4+1}, Room: {room[i] + 1}"
            )
        print(f"Timeslot: {self.Value(self.__timeslot)}")
        print()

    def solution_count(self):
        return self.__solution_count


# Create a solver
solver = cp_model.CpSolver()
solution_printer = VarArraySolutionPrinter(s, y, timeslot)

# Enumerate all solutions
solver.parameters.enumerate_all_solutions = True

# Solve
status = solver.Solve(model, solution_printer)
day = round(solver.Value(timeslot))

# Print the results
print(f"Status = {solver.StatusName(status)}")
print(f"Number of solutions found: {solution_printer.solution_count()}")
