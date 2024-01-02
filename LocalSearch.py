import numpy as np
import random
import copy
import time
data_file = "./data_80_20_(2).txt"

#WORK FLOW:
#--GREEDY SOLVE:
#----Sort subject list by number of students and room by number of places in descending order
#----Each iteration,traverses all unscheduled subjects and match them with largest available room, satisfying it doesn't conflict with others

#--LOCAL SEARCH: Optimization --> Find feasible solution given total of timeslots
#--GOAL: Given total of timeslots k, check whether it's possible to schedule a timetable satisfying all constraints with k timeslots.
#----Init solution using GREEDY SOLVE from x timeslots x: 1 --> k, unscheduled subjects will be grouped into the unassign set
#----Relies on searching in the vicinity to find valid solutions
#--------SA_based_local_search: Based on nearby solutions and examining them using the idea of the Simulated Annealing algorithm
#--------swap_two_section: Perturb current solution to overcome local optima


#Used to sort subject list by number of students and room by number of places in descending order
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

#Read data from txt file
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

        #Build constrant matrix, [i][j] = 1 iff subject i can't be arrage with subject j in the same timeslot
        matrix_constrain = np.zeros((number_subject+1, number_subject+1))
        for iter in constrain:
            i = index_map[iter[0] - 1]
            j = index_map[iter[1] - 1]
            matrix_constrain[i][j] = 1
            matrix_constrain[j][i] = 1

        return number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain, matrix_constrain,index_map



#Gen greedy solution
def greedy_solve(number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain,
                     matrix_constrain):
    # Solve
    solve = []
    kip = 0
    subject_checked = np.zeros((number_subject,))

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

                        if matrix_constrain[iter_sub][i] == 1:
                            conflict[i] = 1

                    # ADD CONFLICT
                    this_kip.append(index_map[iter_sub] + 1)
                    iter_room += 1
                    iter_sub += 1

                else:
                    iter_sub += 1
        solve.append(this_kip)

    return kip, solve

start = time.time()
number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain, matrix_constrain, index_map = read_data(data_file)
# print(student_per_subject)
# print(place_per_room)
# print(matrix_constrain)
kip, solve = greedy_solve(number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain, matrix_constrain)
end = time.time()
print("-------------------------------------------------GREEDY RESULT--------------------------------------------------------")
print(f"Number of timeslots: {kip}")
for i, timeslot in enumerate(solve, start=1):
    print(f'Timeslot{i}: {timeslot}')

print(f"Run time:{end - start}")
#Init solution using GREEDY SOLVE from x timeslots x: 1 --> k
def init_solution_greedy(k, number_subject, student_per_subject, number_room, place_per_room, matrix_constrain):
  solution = []
  subject_checked = np.zeros((number_subject,))

  for i in range(k):
    conflict = np.zeros((number_subject,), dtype=int)
    kip_sol = []
    room_index = 0
    for sub_index in range(number_subject):
      if((subject_checked[sub_index] == 1) or (conflict[sub_index] == 1)):
        continue
      else:
        if(student_per_subject[sub_index] <= place_per_room[room_index]):
          # ADD THIS SUBJECT
          kip_sol.append(sub_index)

          # CHECKED
          subject_checked[sub_index] = 1

          # ADD CONFLICT
          for i in range(number_subject):
            if matrix_constrain[sub_index][i] == 1:
              conflict[i] = 1

          # INCREASE
          room_index += 1
          if(room_index >= number_room): break

    # ADD KIP's SOLUTION
    solution.append(kip_sol)

  unassign = []
  for i in range(number_subject):
    if subject_checked[i] == 0:
      unassign.append(i)

  return solution, unassign

def generate_conflict(sub_list, matrix_constrain):
   conflict = np.zeros((len(matrix_constrain),), dtype=int)
   for sub_index in sub_list:
     for i in range(len(matrix_constrain)):
        if matrix_constrain[sub_index][i] == 1:
          conflict[i] = 1
   return conflict

#Matching subject with largest possible room
def max_match(list_subject, student_per_subject, number_room, place_per_room):
  sub_index = 0
  room_index = 0
  sub_len = len(list_subject)
  room_len = number_room
  accept_sub = []
  reject_sub = []

  while((sub_index < sub_len) and (room_index < room_len)):
    if(student_per_subject[list_subject[sub_index]] <= place_per_room[room_index]):
      accept_sub.append(list_subject[sub_index])
      sub_index += 1
      room_index += 1
    else:
      reject_sub.append(list_subject[sub_index])
      sub_index += 1

  while(sub_index < sub_len):
    reject_sub.append(list_subject[sub_index])
    sub_index += 1

  return accept_sub, reject_sub

#Calculate difference between 2 moves
def delta_st(list1, list2, number_subject, student_per_subject, number_room, place_per_room, matrix_constrain):
  student_list1 = 0
  student_list2 = 0
  degree_list1 = 0
  degree_list2 = 0

  for i in range(len(list1)):
    student_list1 += student_per_subject[list1[i]]
    student_list2 += student_per_subject[list2[i]]

    degree_list1 += np.sum(matrix_constrain[list1[i]])
    degree_list2 += np.sum(matrix_constrain[list2[i]])

  return student_list1 - student_list2 + degree_list1 - degree_list2

#Each move in local search
def naive_move_local_search(t1, t2, r1, sol, unassign, number_subject, student_per_subject, number_room, place_per_room,
                            matrix_constrain):
    # Keep copy
    sol_copy = copy.deepcopy(sol)
    unassign_copy = copy.deepcopy(unassign)

    # RANDOM SELECT ELEMENT
    r2 = random.randint(0, len(sol[r1]) - 1)
    remove_sub = sol[r1][r2]

    # REMOVE RANDOM ELEMENT
    sol[r1].remove(remove_sub)
    conflict = generate_conflict(sol[r1], matrix_constrain)  # [0,0,1,0,1,1,0,1]

    # BUILD NEW LIST
    for sub_index in unassign:
        if conflict[sub_index] == 1:
            continue
        else:
            sol[r1].append(sub_index)
            unassign.remove(sub_index)

            for i in range(number_subject):
                if matrix_constrain[sub_index][i] == 1:
                    conflict[i] = 1

    # USING MAX_MATCH ON NEW LIST
    accept_sub, reject_sub = max_match(sol[r1], student_per_subject, number_room, place_per_room)

    # UPDATE AFTER USING MAX_MATCH
    sol[r1] = accept_sub
    unassign = unassign + reject_sub
    unassign.append(remove_sub)

    # Accept the new solution?
    delta = len(sol[r1]) - len(sol_copy[r1])
    if delta == 0:
        this_delta_st = delta_st(sol[r1], sol_copy[r1], number_subject, student_per_subject, number_room,
                                 place_per_room, matrix_constrain)
    r = random.uniform(0, 1)
    if (
            delta > 0):  # or ((delta<0) and (r < math.exp(delta/t1))): # or ((delta==0) and (this_delta_st>=0)) or ((delta==0) and (this_delta_st<0) and (r < math.exp(this_delta_st/t2))):
        return sol, unassign
    else:
        return sol_copy, unassign_copy

#Swap two step to find better sol
def swap_two_section(sol, unassign, number_subject, student_per_subject, number_room, place_per_room, matrix_constrain,
                     checkpoint=0):
    clone_sol = copy.deepcopy(sol)
    clone_unassign = copy.deepcopy(unassign)

    len_sol = len(sol)
    # RANDOM SELECT 2 PERIODS
    p1 = random.randint(0, len_sol - 1)
    p2 = p1
    while (p2 == p1):
        p2 = random.randint(0, len_sol - 1)

    r = random.randint(0, len(sol[p1]) - 1)
    remove = sol[p1][r]

    # conflict
    conflict_with_remove = matrix_constrain[remove]
    sol[p1].remove(remove)

    remove_set_2 = []  # set in periods 2 conflict with remove element
    for sub in sol[p2]:
        if conflict_with_remove[sub] == 1:
            # sol[p2].remove(sub)
            remove_set_2.append(sub)
    for sub in remove_set_2:
        sol[p2].remove(sub)

    sol[p2].append(remove)
    conflict_period_1 = generate_conflict(sol[p1], matrix_constrain)  # conflict after remove element

    # if remove in conflict break --> return clone
    for sub in remove_set_2:
        if conflict_period_1[sub] == 1:
            return clone_sol, clone_unassign, checkpoint

    sol[p1] = sol[p1] + remove_set_2

    acc1, rej1 = max_match(sol[p1], student_per_subject, number_room, place_per_room)
    acc2, rej2 = max_match(sol[p2], student_per_subject, number_room, place_per_room)
    acc1_cp = copy.deepcopy(acc1)
    acc2_cp = copy.deepcopy(acc2)

    if ((len(rej1) > 0) or (len(rej2) > 0)):
        return clone_sol, clone_unassign, checkpoint

    conflict_set1 = generate_conflict(sol[p1], matrix_constrain)
    conflict_set2 = generate_conflict(sol[p2], matrix_constrain)

    unassign_remove = []
    for sub in unassign:
        if conflict_set1[sub] == 0:
            unassign_remove.append(sub)
            sol[p1].append(sub)
            for i in range(number_subject):
                if matrix_constrain[sub][i] == 1:
                    conflict_set1[i] = 1

        elif conflict_set2[sub] == 0:
            unassign_remove.append(sub)
            sol[p2].append(sub)
            for i in range(number_subject):
                if matrix_constrain[sub][i] == 1:
                    conflict_set2[i] = 1

    for sub in unassign_remove:
        unassign.remove(sub)

    acc1, rej1 = max_match(sol[p1], student_per_subject, number_room, place_per_room)
    acc2, rej2 = max_match(sol[p2], student_per_subject, number_room, place_per_room)

    sol[p1] = acc1
    sol[p2] = acc2

    unassign = unassign + rej1 + rej2
    unassign = np.unique(unassign).tolist()

    improve = len(clone_unassign) - len(unassign)
    if (improve > checkpoint):
        return sol, unassign, improve

    return clone_sol, clone_unassign, checkpoint

#Perform SA algorithm
def SA_base_local_search(t1, t2, sol, unassign, number_subject, student_per_subject, number_room, place_per_room,
                         matrix_constrain):
    each_temp = 5
    l = 15

    while ((each_temp > 0) and (len(unassign) > 0)):
        for i in range(l):
            # Generate a random permutation of solution
            len_sol = len(sol)

            # Iteration len periods
            for i in range(len_sol):
                sol, unassign = naive_move_local_search(t1, t2, i, sol, unassign, number_subject, student_per_subject,
                                                        number_room, place_per_room, matrix_constrain)

        t1 = 1 / (1 / t1 + 0.2)
        t2 = 1 / (1 / t2 + 0.09)
        each_temp -= 1

    return sol, unassign, t1, t2

#Find solution with optima k
def k_color(k, number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain, matrix_constrain):
  #Init solution
  sol, unassign = init_solution_greedy(k, number_subject, student_per_subject, number_room, place_per_room, matrix_constrain)
  best_solution = copy.deepcopy(sol)
  best_unassign = copy.deepcopy(unassign)

  #Init parameter
  number_iter = 150
  t1 = 5
  t2 = 30
  m = 10


  while(number_iter > 0):
    #ITERATION
    number_iter -= 1

    # SA based local search
    sol, unassign, t1, t2 = SA_base_local_search(t1, t2, sol, unassign, number_subject, student_per_subject, number_room, place_per_room, matrix_constrain)

    # improvement_pẻturbation
    checkpoint = 0
    for i in range(m):
      sol, unassign, checkpoint  = swap_two_section(sol, unassign, number_subject, student_per_subject, number_room, place_per_room, matrix_constrain, checkpoint)

    # Check best solution
    if(len(unassign) < len(best_unassign)):
      best_solution = copy.deepcopy(sol)
      best_unassign = copy.deepcopy(unassign)

    if(len(best_unassign) == 0):
      break

  if(len(best_unassign) == 0): return True, best_solution
  else: return False, False


def optimize_solve(data_file):
    # READ DATA
    number_subject, student_per_subject, number_room, place_per_room, number_constrain, constrain, matrix_constrain, index_map = read_data(
        data_file)
    # GET GREEDY SOLUTION
    len_greedy, sol = greedy_solve(number_subject, student_per_subject, number_room, place_per_room,
                                       number_constrain, constrain, matrix_constrain)

    # Init k as greedy solution
    k = len_greedy - 1
    print("-------------------------------------------------LOCAL SEARCH--------------------------------------------------------")

    print("len greedy: ", len_greedy)
    final_result = sol

    while (1):
        verify_k_sol, best_solution = k_color(k, number_subject, student_per_subject, number_room, place_per_room,
                                              number_constrain, constrain, matrix_constrain)
        print(f"If number of timeslot = {k}, result = {verify_k_sol}")
        if (verify_k_sol):
            final_result = best_solution
            k -= 1
        else:
            return k + 1, final_result
            break


    return -1
start = time.time()
len_sol, final_solution = optimize_solve(data_file)
end = time.time()
print(f"SA run time: {end - start}")
print("-------------------------------------------------FINAL RESULT--------------------------------------------------------")
print(f"Number of timeslots: {len_sol}")
for i, timeslot in enumerate(final_solution, start=1):
    print(f'Timeslot{i}: {timeslot}')