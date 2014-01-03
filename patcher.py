#------------------------------------------------------------------------------#
#   AGM S3BDD PATCHER 2013
#
#   This is a Python script that patches S3BDD models with the correct
#   successor values.
#    
#   Files: agmlibrary.py, patcher.py 
#   Copyrights: Dmitri Mironov, 2013
#   Contacts: mironov@smail.ee
#
#------------------------------------------------------------------------------#

import agmlibrary
import time
import re
import random
    
def replace_successors (in_data, output_data):
#fucntion that generates new successors

    down_successor = right_successor = 0
    null_successor = 0
    max_successor = 0
    max_successor_index = 0
    min_successor_index = 1 
    i = 0

    for each_line in in_data:
        if not each_line.find("LEN =") == -1:
            max_successor = int(len_index_array[i]) - 1
            i += 1

        if not each_line.find("_o_") == -1:
            #restarting successors if the new output graph has been found
            min_successor_index = 1 
            down_successor = 0
            right_successor = 0

        if not each_line.find("V = ") == -1:
            #identifying zeros in node successors
            matchObj = re.match( r'(.*)( 0 0)(\.*)', each_line)

            if matchObj:
                new_line = re.sub(" 0 0", " 0 0", each_line)
            else:
                #changing new node successors
                max_successor_index = min_successor_index + 1

                if max_successor_index >= max_successor:
                    max_successor_index = max_successor

                down_successor = random.randint(min_successor_index, max_successor_index)
                right_successor = random.randint(min_successor_index, max_successor_index)

                if (down_successor != min_successor_index and right_successor != min_successor_index):
                    null_successor = random.randint(1,2)
                    if null_successor == 1:
                        down_successor = min_successor_index
                    else:
                        right_successor = min_successor_index

                if down_successor == right_successor:
                    null_successor = random.randint(1,2)
                    if null_successor == 1:
                        down_successor = 0
                    else:
                        right_successor = 0
                    
                new_line = re.sub(" \d{1,} \d{1,}"," " + str(down_successor) + " " + str(right_successor), each_line)
                min_successor_index += 1

            output_data.write(new_line)

        else:
            output_data.write(each_line)

    in_data.seek(0)
    output_data.seek(0)

#Here the patcher code begins

stat_array = []         #0 - Nods, 1 - Vars, 2 - Grps, 3 - Inps, 4 - Cons, 5 - Outs
len_index_array = []    #len indexes of the agm file
beg_index_array = []    #beg indexes of the agm file

prun = "y"              #variable to repeat the execution of the script

while True:
    if prun == "y":
        try:

            filename = input("Please enter agm input file name:")
            in_data = open(filename, "rt")                              #open source file to read from

            out_filename = input("Please enter agm output file name:") 
            output_data = open(out_filename, "w+")                      #open output file to write to
            temp_data = open("temp", "w+")                              #temporary data (optional)

            print("Processing... Please wait!")
            start_time = time.time()
            
            (stat_array, len_index_array, beg_index_array) = agmlibrary.gather_statistics(in_data, stat_array, len_index_array, beg_index_array)
            print("AGM statistics gathered...OK!")
                       
            replace_successors(in_data, output_data)
            print("Successors updated...OK!")

            print("The file", out_filename, "has been created successfully!")
            print("Execution time", time.time() - start_time, "seconds")
            prun = input("Continue (y/n)?")

            agmlibrary.close_files(in_data, output_data, temp_data)
                
        except IOError:
            print("File does not exist!")

    elif prun == "n":
        break
