import numpy as np

data_file = "./example_input0.txt"

def get_map(lst):
    sorted_lst = sorted(lst, reverse=True)

    index_map = {}
    occurrence_count = {}
    for index, element in enumerate(lst):
        if element in occurrence_count:
            occurrence_count[element] += 1
            index_map[index] = sorted_lst.index(element) + occurrence_count[element] - 1
        else:
            occurrence_count[element] = 1
            index_map[index] = sorted_lst.index(element)
    return index_map, sorted_lst

# Read data from txt file
def read_data(data_file_name):
    with open(data_file_name, "r") as f:
        r = f.readlines()
        read = [int(u) for u in r[0][:-1].split(" ")]

        number_subject = int(read[0])
        student_per_subject = [int(u) for u in r[1][:-1].split(" ")]
        number_room = int(read[1])
        place_per_room = [int(u) for u in r[2][:-1].split(" ")]
        number_constrain = int(r[3])

        index_map, student_per_subject = get_map(student_per_subject)
        student_per_subject = np.asarray(student_per_subject)

        place_per_room.sort(reverse=True)
        place_per_room = np.asarray(place_per_room)

        if (r[-1][-1] != '\n'):
            r[-1] += "\n"

        constrain = []
        for i in range(number_constrain):
            each_constrain = [int(u) for u in r[4 + i][:-1].split(" ")]
            constrain.append(each_constrain)

        # Build constraint matrix, [i][j] = 1 iff subject i can't be arranged with subject j in the same timeslot
        matrix_constrain = np.zeros((number_subject + 1, number_subject + 1))
        for iter in constrain:
            i = index_map[iter[0] - 1]
            j = index_map[iter[1] - 1]
            matrix_constrain[i][j] = 1
            matrix_constrain[j][i] = 1

        return number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain, matrix_constrain, index_map

def greedy_solve(number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain,
                     matrix_constrain, index_map):
    # Solve
    solve = []
    kip = 0
    subject_checked = np.zeros((number_subject,))
    start_slot = np.zeros((number_subject,))
    room_assigned = np.zeros((number_subject,))

    while (np.sum(subject_checked) < number_subject):
        kip += 1
        this_kip = []
        iter_room = 0
        iter_sub = 0
        conflict = np.zeros((number_subject,), dtype=int)
        while ((iter_sub < number_subject) and (iter_room < number_room)):
            if (subject_checked[iter_sub] == 1) or (conflict[iter_sub] == 1):  # already checked
                iter_sub += 1
                continue
            else:  # unchecked
                if (place_per_room[iter_room] >= student_per_subject[iter_sub]):  # fit the room -> checked
                    subject_checked[iter_sub] = 1

                    # TO-DO ADD CONFLICT

                    for i in range(number_subject):
                        if conflict[i] == 1 or subject_checked[i] == 1:
                            continue  # Skip subjects already in conflict or checked
                        if matrix_constrain[index_map[iter_sub]][index_map[i]] == 1:
                            conflict[i] = 1


                    # ADD CONFLICT
                    this_kip.append([index_map[iter_sub] + 1, kip, iter_room + 1])  # Adding 1 to convert to 1-indexed
                    start_slot[iter_sub] = kip
                    room_assigned[iter_sub] = iter_room + 1
                    iter_room += 1
                    iter_sub += 1

                else:
                    iter_sub += 1
        solve.extend(this_kip)

    return start_slot, room_assigned, solve

# Output in the specified format
def print_solution(start_slot, room_assigned, solve):
    sorted_solve = sorted(solve, key=lambda x: x[0])
    for item in sorted_solve:
        print(f"{item[0]} {int(start_slot[item[0]-1])} {int(room_assigned[item[0]-1])}")

# Replace with your actual input file name
number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain, matrix_constrain, index_map = read_data(data_file)
start_slot, room_assigned, solve = greedy_solve(number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain, matrix_constrain, index_map)
print_solution(start_slot, room_assigned, solve)
