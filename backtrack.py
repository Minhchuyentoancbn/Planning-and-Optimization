# Backtracking algorithm for scheduling exams

def read_data():
    n, m = list(map(int, input().split()))
    d = list(map(int, input().split()))  # Number of students per class
    assert len(d) == n, "Number of classes does not match"
    c = list(map(int, input().split()))  # Capacity of rooms
    assert len(c) == m, "Number of rooms does not match"
    k = int(input())  # Number of pairs of conflicting classes
    conflicts = []
    for _ in range(k):
        conflicts.append(list(map(int, input().split())))

    return n, m, d, c, conflicts

def build_conflict_table(n, conflicts):
    conflict_table = [[0 for _ in range(n)] for _ in range(n)]
    for i, j in conflicts:
        conflict_table[i - 1][j - 1] = 1
        conflict_table[j - 1][i - 1] = 1
    for i in range(n):
        conflict_table[i][i] = 1
    return conflict_table


def solution():
    global best_num_days
    # Compute number of days needed for this solution
    # For all assigned that use slot 1, compute the number of days
    room_slot_assigned = [[0 for _ in range(4)] for _ in range(m)]
    for i in range(n):
        room = schedule_class[i]
        slot = schedule_slot[i]
        room_slot_assigned[room][slot - 1] += 1

    schedule_day = max([max(room_slot_assigned[i]) for i in range(m)])


    # schedule_day = max(num_days_slot)

    if best_num_days > schedule_day:
        best_num_days = schedule_day
        # Copy solution
        for i in range(n):
            best_schedule_class[i] = schedule_class[i]
            best_schedule_slot[i] = schedule_slot[i]


def is_feasible(exam_index, room, slot):
    # Check if exam_index can be assigned to room and slot
    # Check if there is a conflict
    for i in range(exam_index):
        if conflict_table[exam_index][i] == 1 and schedule_slot[i] == slot:
            return False

    return True


def try_schedule(exam_index):
    # print(f"Exam index: {exam_index}")
    for room in range(m):
        if d[exam_index] > c[room]:
            continue
        for slot in range(1, 5):
            if not is_feasible(exam_index, room, slot):
                continue
            schedule_class[exam_index] = room
            schedule_slot[exam_index] = slot
            if exam_index == n - 1:
                solution()
            else:
                try_schedule(exam_index + 1)
    return

                      

if __name__ == "__main__":
    n, m, d, c, conflicts = read_data()
    conflict_table = build_conflict_table(n, conflicts)
    best_num_days = n
    best_schedule_class = [None for _ in range(n)]  # Class assigned to each exam
    best_schedule_slot = [None for _ in range(n)]   # Time slot assigned to each exam, 1, 2, 3, 4

    schedule_class = [None for _ in range(n)]  # Class assigned to each exam
    schedule_slot = [None for _ in range(n)]   # Time slot assigned to each exam, 1, 2, 3, 4

    try_schedule(0)
    # Print solution
    for i in range(1, n + 1):
        print(f'{i} {best_schedule_slot[i]} { best_schedule_class[i] + 1}')








