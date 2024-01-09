from ortools.linear_solver import pywraplp
import math

# def read_data(file_name):
#     data = {}

#     with open(file_name, 'r') as f:
#         if f == None:
#             print('File not found')
#             return None

#         data["num_subjects"], data["num_rooms"] = [int(x) for x in f.readline().split()]
#         data["num_students_per_subject"] = [int(x) for x in f.readline().split()]
#         data["num_seats_per_room"] = [int(x) for x in f.readline().split()]
#         data["num_pairs"] = int(f.readline())
#         data["conflicts"] = []
#         for _ in range(data["num_pairs"]):
#             s1, s2 = [int(x) for x in f.readline().split()]
#             data["conflicts"].append((s1 - 1, s2 - 1))

#     return data

def read_data():
    data = {}

    data["num_subjects"], data["num_rooms"] = [int(x) for x in input().split()]
    data["num_students_per_subject"] = [int(x) for x in input().split()]
    data["num_seats_per_room"] = [int(x) for x in input().split()]
    data["num_pairs"] = int(input())
    data["conflicts"] = []
    for _ in range(data["num_pairs"]):
        s1, s2 = [int(x) for x in input().split()]
        data["conflicts"].append((s1 - 1, s2 - 1))

    return data



STATUS_DICT = {
    pywraplp.Solver.OPTIMAL: "OPTIMAL",
    pywraplp.Solver.FEASIBLE: "FEASIBLE",
    pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
    pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
    pywraplp.Solver.ABNORMAL: "ABNORMAL",
    pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
}


def solve_with_mip(num_subjects: int, num_rooms: int, nums_student_per_subject: int,
                   num_seats_per_room: int, subject_pairs: int,
                   num_sections_per_day: int = 4,
                   ):

    num_days = math.ceil(num_subjects / num_sections_per_day)
    max_sum_sections = num_subjects

    solver = pywraplp.Solver('Scheduling', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    x = {}

    for subject in range(num_subjects):
        for room in range(num_rooms):
            for section_id in range(max_sum_sections):
                x[(subject, room, section_id)] = solver.IntVar(0, 1, 'x[%i, %i, %i]' % (subject, room, section_id))

    y = solver.IntVar(0, max_sum_sections, 'y')

    # Ràng buộc: Môn thi nào cũng phải được xếp lịch
    for subject in range(num_subjects):
        temp = []

        for room in range(num_rooms):
            c = solver.Sum([x[(subject, room, section_id)] for section_id in range(max_sum_sections)])
            temp.append(c)

        solver.Add(solver.Sum(temp) == 1)

        # Mỗi phòng chỉ được dùng tối đa cho 1 môn thi vào mỗi kíp
    for room in range(num_rooms):
        for section_id in range(max_sum_sections):
            solver.Add(solver.Sum([x[(subject, room, section_id)]
                                   for subject in range(num_subjects)]) <= 1)

    # Phòng thi phải chứa đủ số học sinh của môn thi
    for subject in range(num_subjects):
        for room in range(num_rooms):
            solver.Add(solver.Sum([x[(subject, room, section_id)] * nums_student_per_subject[subject]
                                   for section_id in range(max_sum_sections)]) <= num_seats_per_room[room])

    # 2 môn thi conflict không thể thi cùng kíp
    for section_id in range(max_sum_sections):
        for subject1, subject2 in subject_pairs:
            solver.Add(solver.Sum([x[(subject1, room, section_id)] + x[(subject2, room, section_id)]
                                   for room in range(num_rooms)]) <= 1)

    # y là số kíp thi
    for subject in range(num_subjects):
        for room in range(num_rooms):
            for section_id in range(max_sum_sections):
                solver.Add(y >= x[(subject, room, section_id)] * section_id)

    solver.Minimize(y)

    status = solver.Solve()

    solution = []

    # print('Objective value =', solver.Objective().Value())
    for subject in range(num_subjects):
        for room in range(num_rooms):
            for section_id in range(max_sum_sections):
                if x[(subject, room, section_id)].solution_value() > 0:
                    print(f"{subject + 1} {section_id + 1} {room + 1}")

                    solution.append(
                        (subject, room, section_id // num_sections_per_day, section_id % num_sections_per_day))

    solution.sort(key=lambda x: x[2] * num_sections_per_day + x[3])

    solution_str = ''
    solution_str += "subjects,number_student,rooms,num_seat,day,section" + "\n"
    for subjects, room, day, section in solution:
        solution_str += str(subjects) + "," + str(nums_student_per_subject[subjects]) + "," + str(room) + "," + \
                        str(num_seats_per_room[room]) + "," + str(day) + "," + str(section) + "\n"

    return (solution_str, status)


if __name__ == '__main__':

    data = read_data()
    solution_str, status = solve_with_mip(data["num_subjects"], data["num_rooms"], data["num_students_per_subject"],
                                          data["num_seats_per_room"], data["conflicts"])