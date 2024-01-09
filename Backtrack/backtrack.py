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
    """
    Build a conflict table so we can check if two classes are conflicting in O(1)

    conflict_table[(i, j)] = 1 if class i and class j are conflicting
    """
    conflict_table = dict()
    for i, j in conflicts:
        conflict_table[(i, j)] = 1
        conflict_table[(j, i)] = 1

    for i in range(1, n + 1):
        conflict_table[(i, i)] = 1
        
    return conflict_table
                      

def schedule_exams(n, m, d, c, conflict_table):
    global best_objective, best_schedule_room, best_schedule_section

    scheduled_room = [0 for _ in range(n)]
    schedule_section = [0 for _ in range(n)]
    best_schedule_room = []
    best_schedule_section = []
    best_objective = (n - 1) // 4 + 2

    def is_valid(subject_index, section, room):
        # branch and bound
        if section // 4 + 1 >= best_objective:
            return False

        # check capacity
        if d[subject_index] > c[room]:
            return False
        
        # check room is not used at the same time
        for subject in range(subject_index):
            if scheduled_room[subject] == room and schedule_section[subject] == section:
                return False
            
        # check conflict
        for subject in range(subject_index):
            if conflict_table.get((subject + 1, subject_index + 1), 0) == 1:
                if schedule_section[subject] == section:
                    return False
                
        return True

    def solution_found():
        global best_objective, best_schedule_room, best_schedule_section
        max_section = max(schedule_section)
        if max_section < best_objective:
            best_objective = max_section // 4 + 1
            best_schedule_room = [room for room in scheduled_room]
            best_schedule_section = [section for section in schedule_section]


    def backtrack(subject_index):
        for section in range(n):
            for room in range(m):
                if is_valid(subject_index, section, room):
                    scheduled_room[subject_index] = room
                    schedule_section[subject_index] = section
                    
                    if subject_index == n - 1:
                        solution_found()
                    else:
                        backtrack(subject_index + 1)

    backtrack(0)

    final_answer = []
    for i in range(n):
        final_answer.append((i + 1, best_schedule_section[i] + 1, best_schedule_room[i] + 1))

    return final_answer


if __name__ == "__main__":
    n, m, d, c, conflicts = read_data()
    conflict_table = build_conflict_table(n, conflicts)

    final_answer = schedule_exams(n, m, d, c, conflict_table)

    # Print solution
    for i in range(n):
        print(f"{final_answer[i][0]} {final_answer[i][1]} {final_answer[i][2]}")