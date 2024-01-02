from ortools.sat.python import cp_model

class AllSolutionsCallback(cp_model.CpSolverSolutionCallback):
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


    def get_solutions(self):
        return self.__solutions

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
# s[i] = start slot of course i
s = [model.NewIntVar(1, N, "s[%i]" % i) for i in range(0, N)]
# y[i][j] = 1 if course i is in room j
y = [[model.NewIntVar(0, 1, "y[%i][%i]" % (i, j)) for j in range(M)] for i in range(N)]
timeslot = model.NewIntVar(1, N, "timeslot")

# Constraints
# Constraint 1: Conflict courses must be in different time slots
for i, j in conflict:
    model.Add(s[i] != s[j])

# Constraint 2: Optimize the timeslot
for i in range(N):
    model.Add(timeslot >= s[i])

# Constraint 3: Capacity of room must be greater than or equal to the number of students
for i in range(N):
    for j in range(M):
        model.Add(y[i][j] * d[i] <= c[j])

# Constraint 4: 2 courses in the same timeslot must be in different rooms
for i in range(N):
    for j in range(N):
        if i == j:
            continue
        for k in range(M):
            b = model.NewBoolVar("b[%i][%i]" % (i, j))
            model.Add(s[i] == s[j]).OnlyEnforceIf(b)
            model.Add(s[i] != s[j]).OnlyEnforceIf(b.Not())
            model.Add(y[i][k] + y[j][k] <= 1).OnlyEnforceIf(b)

# Constraint 5: Each course must be in exactly one room
for i in range(N):
    model.Add(sum([y[i][j] for j in range(M)]) == 1)

# Constraint 6: Each room must be used in at most one timeslot
model.Add(timeslot == 4)

# Objective function (Minimize the timeslot)
# model.Minimize(timeslot)

# Create the solver
solver = cp_model.CpSolver()

# Use the AllSolutionsCallback to find all solutions
all_solutions_callback = AllSolutionsCallback(s,y,timeslot)
solver.SearchForAllSolutions(model, all_solutions_callback)

# Print all solutions
for solution in all_solutions_callback.get_solutions():
    print(solution)
