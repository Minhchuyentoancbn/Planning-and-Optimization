import numpy as np
import random

def generate_data(
    num_subjects: int, 
    num_rooms: int, 
    num_conflits: int = None, 
    file_name: str = None,
    num_sections_per_day: int = 4, 
    min_students_per_subject: int = 20, 
    max_students_per_subject: int = 40, 
    random_rate: float = 0.5, 
    most_strict: bool = False,
    valid_solution: bool = True, 
    debug: bool = False
):
    """
    Generate data for exam scheduling problem with constraints.

    This geneated data is valid data, which means that it is possible to find a solution for this data.
    If you want to gnereate data with more conflicts, you can set most_strict = True
    If you wnat to generate data that is not solved, you can set valid_solution = False

    Parameters
    ----------
    num_subjects : int
        number of subjects

    num_rooms : int
        number of rooms

    num_conflits : int, optional
        number of conflicts, by default None

    file_name : str, optional
        file name to save input and solutuion data, by default None

    num_sections_per_day : int, optional
        number of sections per day, by default 4

    min_students_per_subject : int, optional
        min number of students per subject, by default 20

    max_students_per_subject : int, optional
        max number of students per subject, by default 40

    random_rate : float, optional
        random rate to generate data, by default 0.5

    most_strict : bool, optional
        generate more conlicts data, by default False

    valid_solution : bool, optional
        is generated data solved, by default True

    debug : bool, optional
        debug mode to print debug information, by default False
    """

    if num_conflits is None and most_strict:
        num_conflits = num_subjects * (num_subjects - 1) // 2
    elif num_conflits is None:
        num_conflits = random.randint(0, num_subjects * (num_subjects - 1) // 2)
        
    if (valid_solution == False):
        num_conflits = num_subjects * (num_subjects - 1) // 2

    data = {}
    data["random_rate"] = random_rate
    data["num_sections_per_day"] = num_sections_per_day
    data["num_subjects"] = num_subjects
    data["subjects"] = [i for i in range(data["num_subjects"])]

    # Generate number of students per subject
    data["num_students_per_subject"] = [random.randint(min_students_per_subject, max_students_per_subject) 
                                        for _ in range(data["num_subjects"])]
    
    # Generate number of rooms and capacity per room
    min_capacity_per_room = min(data["num_students_per_subject"])
    max_capacity_per_room = max(data["num_students_per_subject"]) + 10
    data["num_rooms"] = num_rooms
    data["num_capacity_per_room"] = [random.randint(min_capacity_per_room, max_capacity_per_room)
                                     for _ in range(data["num_rooms"])]
    # Make sure that there is at least one room that can contain all students
    while (max(data["num_capacity_per_room"]) < max(data["num_students_per_subject"])):  
        data["num_capacity_per_room"] = [random.randint(min_capacity_per_room, max_capacity_per_room)
                                     for _ in range(data["num_rooms"])]
    
    # Assign subject to each section per days    
    num_sections = 0
    subject_count = 0
    day_count = 0 
    assigned = []
    section_mapper = {}
    assigned_subjects = []
    random_rate_decay = random_rate / data["num_rooms"]
    random_rate -= random_rate_decay
    while (subject_count < data["num_subjects"]):
        if debug:
            print("subject_count = {}".format(subject_count))
        
        # Sort room by capacity
        room_pair = [(room, capacity) for room, capacity in enumerate(data["num_capacity_per_room"])]
        room_pair.sort(key=lambda x: x[1], reverse=False)
        
        for (room, capacity) in room_pair:
            if debug:
                print("================================")
                print("room = {}, capacity = {}".format(room, capacity))
                print("assigned_subjects = {}".format(assigned_subjects))
                print(f"capacity of each room: {data['num_capacity_per_room']}")
                print(f"number of students per subject: {data['num_students_per_subject']}")
                print([num_student_per_subject if (num_student_per_subject <= capacity and s not in assigned_subjects) 
                                    else 0 for s, num_student_per_subject in enumerate(data["num_students_per_subject"])])
            
            
            # Find subject max to fit in room           
            subject = np.argmax([num_student_per_subject if (num_student_per_subject <= capacity and s not in assigned_subjects) 
                                  else 0 for s, num_student_per_subject in enumerate(data["num_students_per_subject"])])

            # Check if subject is valid with capacity
            if (data["num_students_per_subject"][subject] > capacity):
                continue
            
            # Check if subject is already assigned
            if (subject in assigned_subjects):
                continue

            if debug:
                print("random_rate = {}".format(random_rate))

            # Skip this room
            if (random.random() < random_rate):
                random_rate -= random_rate_decay
                continue
                
            assigned_subjects.append(subject)
            assigned.append((subject, room, day_count, num_sections))
            section_mapper[subject] = day_count * data["num_sections_per_day"] + num_sections
            subject_count += 1
            if (subject_count == data["num_subjects"]):
                break
        
        num_sections += 1

        # Reset num_sections
        if (num_sections == num_sections_per_day):
            random_rate = data["random_rate"]
            num_sections = 0
            day_count += 1   

    if debug:
        print("assigned = {}".format(assigned))
        print(section_mapper)
    
    # Generate conflicts
    data["conflict_list"] = []
    count_conflict = 0
    subjects_list = [i for i in range(data["num_subjects"])]
    random.shuffle(subjects_list)    
    
    for i in subjects_list:
        for j in subjects_list:
            if (i == j):
                continue
            try:
                data["conflict_list"].index((j, i))
                continue
            except ValueError:
                pass
            
            if (section_mapper[i] != section_mapper[j]):
                data["conflict_list"].append((i + 1, j + 1)) # 1-based index
                count_conflict += 1
                if (count_conflict == num_conflits):
                    break
        if (count_conflict == num_conflits):
            break
    
    
    data["num_conflicts"] = len(data["conflict_list"])
    
    # Save input data to file
    tuple_to_string = lambda x : " ".join(str(value) for value in x) if random.Random().random() < 0.5 else " ".join(str(value) for value in reversed(x))
    conflicts_arr = list(map(tuple_to_string, data["conflict_list"]))
    random.shuffle(conflicts_arr)
    
    input_str = ''
    input_str += str(data["num_subjects"]) + "\n" \
        + " ".join(list(map(str, data["num_students_per_subject"]))) \
        + "\n" + str(data["num_rooms"]) + "\n" \
        + " ".join(list(map(str, data["num_capacity_per_room"]))) \
        + "\n" + str( data["num_conflicts"]) + "\n" \
        + "\n".join(conflicts_arr)    

    if (valid_solution):
        with open("data/" + file_name + ".txt", "w+") as f:
            f.write(input_str)
    else:
        pass
    
    # Save solution to file
    solution_str = ''        
    solution_str += "subjects,number_student,rooms,num_seat,day,section" + "\n"
    for subjects, room, day, section in assigned:
        solution_str += str(subjects + 1) + "," + str(data["num_students_per_subject"][subjects]) + "," + str(room + 1) + "," + \
            str(data["num_capacity_per_room"][room]) + "," + str(day + 1) + "," + str(section + 1) + "\n"
    
    if (valid_solution):
        with open("data/" + file_name + "_solution.csv", "w+") as f:
            f.write(solution_str)
    else:
        pass


if __name__ == "__main__":
    
    # Config for 
    configs = [
        (10, 2), 
        (16, 3), 
        (20, 4),
        (30, 6), 
        (40, 8), 
        (50, 10),
        (60, 12), 
        (70, 16), 
        (80, 20),
        (200, 20)
    ]

    for _, config in enumerate(configs):
        for i in range (5):
            num_subjects, num_rooms = config
            generate_data(num_subjects, num_rooms, 
                          file_name = "data_{}_{}_({})".format(num_subjects, num_rooms, i), 
                          random_rate=0.5)