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
                      

def schedule_exams(exams, num_days, num_sections, room_capacities, conflict_table):
    """
    Check whether we can schedule all exams in the given number of days
    """

    # Assign exam to a slot for each day
    num_rooms = len(room_capacities)
    schedule_exams = [[[] for _ in range(num_sections)] for _ in range(num_days)]
    schedule_rooms = [[[] for _ in range(num_sections)] for _ in range(num_days)]


    def is_valid(exam_index, day, section, room):
        """
        Check if we can schedule exam at index exam_index in day and section at room
        """
        # Check capacity
        if exams[exam_index][1] > room_capacities[room]:
            return False
        
        # Check room is not used
        if room in schedule_rooms[day][section]:
            return False
        
        # Check conflict
        for scheduled_exam in schedule_exams[day][section]:
            if conflict_table.get((exams[exam_index][0], scheduled_exam[0]), 0) == 1:
                return False
            
        return True

        

    def backtrack(exam_index):
        """
        Check if we can schedule exam at index exam_index
        """
        if exam_index == len(exams):
            return True
        
        for day in range(num_days):
            for section in range(num_sections):
                for room in range(num_rooms):
                    # Check if we can schedule exam at index exam_index in day and section
                    if is_valid(exam_index, day, section, room):
                        schedule_exams[day][section].append(exams[exam_index])
                        schedule_rooms[day][section].append(room)
                        if backtrack(exam_index + 1):
                            return True
                        schedule_exams[day][section].pop()
                        schedule_rooms[day][section].pop()

        return False
    
    if backtrack(0):
        return schedule_exams, schedule_rooms
    return None, None



if __name__ == "__main__":
    n, m, d, c, conflicts = read_data()
    conflict_table = build_conflict_table(n, conflicts)

    exams = [(i + 1, d[i]) for i in range(n)]

    scheduled_exams = None
    scheduled_rooms = None

    for num_days in range(1, n + 1):
        scheduled_exams, scheduled_rooms = schedule_exams(exams, num_days, 4, c, conflict_table)
        if scheduled_exams is not None:
            break

    final_answer = [[] for _ in range(n)]
    for day in range(num_days):
        for section in range(4):
            for i, exam in enumerate(scheduled_exams[day][section]):
                final_answer[exam[0] - 1] = ((exam[0], section + 1, scheduled_rooms[day][section][i] + 1))


    # Print solution
    for i in range(n):
        print(f"{final_answer[i][0]} {final_answer[i][1]} {final_answer[i][2]}")