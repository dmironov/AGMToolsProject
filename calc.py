#------------------------------------------------------------------------------#
#   S3BDD minimum number of nodes calculator
#
#   This is a Python script that calculates minimum number of nodes in S3BDD.
#    
#   Files: calc.py 
#   Copyrights: Dmitri Mironov, 2013
#   Contacts: mironov@smail.ee
#
#------------------------------------------------------------------------------#

import time
from itertools import groupby

def save_element (reverse_flag, each_line, string_before, string_after):
#finds the target element between two strings and returns it as a string or integer

    if reverse_flag == 0:
        (trash_data, needed_data) = each_line.split(string_before, 1)
        (target, trash_data2) = needed_data.split(string_after, 1)

    elif reverse_flag == 1:
        (needed_data, trash_data) = each_line.split(string_before, 1)
        (trash_data2, target) = needed_data.split(string_after, 1)

    elif reverse_flag == 2:
        (needed_data, trash_data) = each_line.split(string_before, 1)
        (target, trash_data2) = needed_data.split(string_after, 1)

    elif reverse_flag == 3:
        (trash_data, needed_data) = each_line.split(string_before, 1)
        (trash_data2, target) = needed_data.split(string_after, 1)

    if target.isdigit():
        return int(target)
    else:
        return str(target)

def gather_statistics (in_data, stat_array, len_index_array, beg_index_array):
#gathers all statistics about the agm file

    del stat_array[0:len(stat_array)]
    del len_index_array[0:len(len_index_array)]
    del beg_index_array[0:len(beg_index_array)]    

    for each_line in in_data:
        if not each_line.find("STAT#") == -1:
            #gathering agm file statistics
            stat_array = each_line.strip().split(" ")
            
            stat_array.remove("STAT#")
            stat_array.remove(stat_array[0])
            stat_array.remove(stat_array[0])
            stat_array.remove(stat_array[0])
            stat_array.remove("Nods,")
            stat_array.remove(stat_array[1])
            stat_array.remove("Vars,")
            stat_array.remove(stat_array[2])
            stat_array.remove("Grps,")
            stat_array.remove(stat_array[3])
            stat_array.remove("Inps,")
            stat_array.remove(stat_array[4])
            stat_array.remove("Cons,")
            stat_array.remove(stat_array[5])
            stat_array.remove("Outs")
            
        if not each_line.find("BEG =") == -1:
            #save beginning values to the list
            beg_index_array.append(save_element(0, each_line, "BEG =   ", ", LEN ="))
        
    
        if not each_line.find("LEN =") == -1:
            #save lenght values to the list
            len_index_array.append(save_element(0, each_line, "LEN =   ", " -")) 
        

    stat_array = [int(each_element) for each_element in stat_array]

    in_data.seek(0)
    return (stat_array, len_index_array, beg_index_array)

def calc_variables(in_data):
    
    S0 = 0
    k = list()
    k_s3bdd = list()
    temp_k = list()
    inputs_with_branches = 0
    int_var_index = 0
    fanout_list = list()
    
    for each_line in in_data:

        if not each_line.find("0:  (____)	(	0	0)") == -1:
            int_var_index = save_element(0, each_line, "V = ", '     "')
            
            #collect inputs with fan-outs
            if int_var_index < stat_array[3]:
                inputs_with_branches += 1
        
        if not each_line.find("V = ") == -1:
            int_var_index = save_element(0, each_line, "V = ", '     "')
            
            #collect all branches in the circuit
            if int_var_index >= stat_array[3]:
                fanout_list.append(int_var_index)
                            
    
    #calculate S0
    S0 = stat_array[3] - inputs_with_branches
    
    #sort branches, save k to temp_k
    fanout_list.sort()
    temp_k.extend([len(list(group)) for key, group in groupby(fanout_list)])
    
    #remove element in k, if k=1
    for each_element in temp_k:
        if not each_element == 1:
            k.append(each_element)
    
    #calculate (k-1)
    k_s3bdd.extend(k)
    for each_element in k_s3bdd: k_s3bdd[k_s3bdd.index(each_element)] -= 1
    
    print("\nNumber of nodes in netlist:", stat_array[0])
    print("Number of nodes in SSBDD:", stat_array[3] + sum(k))
    print("Lower bound of the number of nodes in S3BDD:", (stat_array[3] - (stat_array[5]-1)) + sum(k_s3bdd))
    print()
    

#Here the patcher code begins

stat_array = []         #0 - Nods, 1 - Vars, 2 - Grps, 3 - Inps, 4 - Cons, 5 - Outs
len_index_array = []    #len indexes of the agm file
beg_index_array = []    #beg indexes of the agm file

prun = "y"              #variable to repeat the execution of the script

while True:
    if prun == "y":
        try:

            filename = input("Please enter agm input file name:")
            in_data = open(filename+".agm", "rt")                              #open source file to read from

            print("Processing... Please wait!")
            start_time = time.time()
            
            (stat_array, len_index_array, beg_index_array) = gather_statistics(in_data, stat_array, len_index_array, beg_index_array)
            print("AGM statistics gathered...OK!")
                       
            calc_variables(in_data)

            print("Execution time", time.time() - start_time, "seconds")
            prun = input("Continue (y/n)?")

            in_data.close()
                
        except IOError:
            print("File does not exist!")

    elif prun == "n":
        break
