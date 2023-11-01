# Backtracking algorithm for scheduling exams
best_num_days = 1000000000
best_schedule_class = None
best_schedule_slot = None
schedule_class = None
schedule_slot = None

def read_data():
    """
    Read data from stdin
    """
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
    global best_num_days, current_schedule_day
    # Compute number of days needed for this solution
    # For all assigned that use slot 1, compute the number of days

    if best_num_days > current_schedule_day:
        best_num_days = current_schedule_day
        # Copy solution
        for i in range(n):
            best_schedule_class[i] = schedule_class[i]
            best_schedule_slot[i] = schedule_slot[i]


def is_feasible(exam_index, room, slot):
    """
    Check if exam_index can be assigned to room and slot
    """
    global best_num_days, room_slot_assigned
    # Branch and bound on number of days
    if room_slot_assigned[room][slot - 1] + 1 >= best_num_days:
        return False

    # Check if there is a conflict
    for i in range(exam_index):
        if conflict_table[exam_index][i] == 1 and schedule_slot[i] == slot:
            return False

    return True


def try_schedule(exam_index):
    global best_num_days, current_schedule_day
    for room in range(m):
        # Check capacity
        if d[exam_index] > c[room]:
            continue
        for slot in range(1, 5):
            if not is_feasible(exam_index, room, slot):
                continue
            schedule_class[exam_index] = room
            schedule_slot[exam_index] = slot
            room_slot_assigned[room][slot - 1] += 1
            old_schedule_day = current_schedule_day
            current_schedule_day = max(current_schedule_day, room_slot_assigned[room][slot - 1])
            if exam_index == n - 1:
                solution()
            else:
                try_schedule(exam_index + 1)

            # Backtrack
            room_slot_assigned[room][slot - 1] -= 1
            current_schedule_day = old_schedule_day
    return

                      

if __name__ == "__main__":
    n, m, d, c, conflicts = read_data()
    conflict_table = build_conflict_table(n, conflicts)
    best_schedule_class = [None for _ in range(n)]  # Class assigned to each exam
    best_schedule_slot = [None for _ in range(n)]   # Time slot assigned to each exam, 1, 2, 3, 4

    schedule_class = [None for _ in range(n)]  # Class assigned to each exam
    schedule_slot = [None for _ in range(n)]   # Time slot assigned to each exam, 1, 2, 3, 4

    room_slot_assigned = [[0 for _ in range(4)] for _ in range(m)]
    current_schedule_day = 0

    try_schedule(0)
    # Print solution
    for i in range(n):
        print(f'{i + 1} {best_schedule_slot[i]} { best_schedule_class[i] + 1}')