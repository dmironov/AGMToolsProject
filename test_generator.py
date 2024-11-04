#------------------------------------------------------------------------------#
#   DELAY FAULT TEST GENERATOR
#
#   This is a Python script that generates extended test table,
#   simulates it and generates Delay Fault Table and SAF Fault Table
#   for the test pairs.
#   
#   Files:      agmlibrary.py, test_generator.py, npsimul.exe
#   Copyrights: Dmitri Mironov, 2013-2024
#   Contacts:   dmm.mironov@gmail.com
#
#------------------------------------------------------------------------------#

import time
import os
import agmlibrary

enable_logging = False                      #enable debug logging messages in shell window
disable_statistics = True                   #TRUE - write to file enabled, FALSE - write to file disabled

def gather_statistics (in_data, stat_array):
#gathers all statistics about the agm file

    del stat_array[0:len(stat_array)]

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

    stat_array = [int(each_element) for each_element in stat_array]

    in_data.seek(0)
    return (stat_array)

def map_table(in_data, agm_data, enable_logging):
#function that makes correct mapping to input test table

    del mapped_table[0:len(mapped_table)]
    del int_global_index[0:len(int_global_index)]
    
    for inputs in range(0, stat_array[3]):
        for each_line in agm_data:
            if not each_line.find("V = "+str(inputs)+" ") == -1:
                if not each_line.find(":") == -1:
                    #find the local and the global indexes of the node line
                    each_line = each_line.lstrip()
                    int_global_index.append(agmlibrary.save_element(2, each_line, ":", "   "))
                
        agm_data.seek(0)       
    if enable_logging: print(int_global_index)
    
    for each_fault_vector in table:
        temp_mapped_table = list()
        for each_element in int_global_index:
            temp_mapped_table.append(each_fault_vector[each_element])
        
        mapped_table.append(temp_mapped_table)
        del temp_mapped_table
    
    if enable_logging: print(int_global_index)

def collect_data(in_data, enable_logging):
#creating 3 lists with patterns, test tables and faults
    
    del patterns[0:len(patterns)]
    del table[0:len(table)]
    del faults[0:len(faults)]

    global coverage
    vectors = 0                            #nr of test vectors in the tst files
    vectors_tmp = 0                        #same as previous, but for local index purpose
    coverage = ""
    
    for each_line in in_data:
        #reading nr of vectors in tst
        if not each_line.find(".VECTORS") == -1:
            vectors = agmlibrary.save_element(0, each_line, ".VECTORS ", "\n")
            if enable_logging: print("Nr. of vectors found", vectors)
        
        if not each_line.find(".PATTERNS") == -1:
            #saving test patterns to new list
            vectors_tmp = vectors
            for each_line in in_data:
                if each_line == "\n": continue
                if vectors_tmp == 0: break
                patterns.append(list(each_line))
                vectors_tmp -= 1
                
        if not each_line.find(".TABLE") == -1:
            #saving test table to new list
            vectors_tmp = vectors
            for each_line in in_data:
                if each_line == "\n": continue
                if vectors_tmp == 0: break
                table.append(list(each_line))
                vectors_tmp -= 1
                
        if not each_line.find(".FAULTS") == -1:
            #saving faults to new list
            for each_line in in_data:
                if each_line == "\n": continue
                faults.append(list(each_line))
                break

        if not each_line.find(".COVERAGE") == -1:
            #saving faults to new list
            for each_line in in_data:
                if each_line == "\n": continue
                coverage = each_line
                break
    
    #remove "\n" symbol at the end of each list        
    for each_element in patterns:
        if isinstance(each_element, list): each_element.pop()
    
    for each_element in table:
        if isinstance(each_element, list): each_element.pop()          
        
    for each_element in faults:
        if isinstance(each_element, list): each_element.pop()
        

def build_ext_table(in_data, tst_filename, output_data, enable_logging):
#building extended test pattern table

    del new_patterns[0:len(new_patterns)]
    del main_vector_indexes[0:len(main_vector_indexes)]
    del add_vector_nr[0:len(add_vector_nr)]
    del new_tst_group_list[0:len(new_tst_group_list)]

    input_index = 0                         #index of the "X" input, depend on the number of inputs
    agm_inps_local = stat_array[3]          #number of inputs in the agm file, used as counter
    
    output_data.write("DELAY FAULT TEST GENERATION OUTPUT FILE\n\n")
    output_data.write("Inputs of the " +str(in_data)+ " Digital Circuit:\n")

    while agm_inps_local > 0:
        #print("X" +str(input_index), end=" ")
        output_data.write("X" +str(input_index)+ " ")
        input_index += 1
        agm_inps_local -= 1    
     
    output_data.write("\n\n")
    output_data.write(str(len(patterns))+ " test vectors found in "+str(tst_filename)+".tst\n\n")
    output_data.write("Extended test pattern table:\n")
    output_data.write("----------------------------\n\n") 

    temp = list()                           #temp list to store each extended test vector
    
    #replace "dont-care" bits in input test vectors with "0"
    for each_element in patterns:
        if isinstance(each_element, list):
            for each_bit in each_element:
                if each_bit == "x": each_element[each_element.index(each_bit)] = "0"
              
    insert_start_vector = 1
    nr_of_pairs = 0
    nr_of_no_pairs = 0

    #generate new test vectors
    for each_element in mapped_table:

        insert_start_vector = 1             #watchdog for saving MAIN vector to extended table
        agm_inps_local = stat_array[3]      #watchdog for going through only tested nodes
        local_index = 0                     #index - bit index for each line in test table
        nr_of_pairs = 0                     #counter of test pairs for each test vector
        if isinstance(each_element, list):           
            for each_bit in each_element:
                #check only first bits that correspond to inputs
                if agm_inps_local > 0:
                    #if the input is not tested for any fault, then continue next cycle
                    if each_bit == "X": 
                        agm_inps_local -= 1
                    else:
                        #save MAIN test vector to extended table
                        if insert_start_vector:
                            new_patterns.append(patterns[mapped_table.index(each_element)])
                            main_vector_indexes.append(len(new_patterns))
                            if disable_statistics: output_data.write("T" +str(mapped_table.index(each_element))+ ":\n")
                            for bit in patterns[mapped_table.index(each_element)]: 
                                if bit != "L" and bit != "H" and bit != "l" and bit != "h":
                                    if disable_statistics: output_data.write(str(bit))     
                            if disable_statistics: output_data.write("\n")
                            nr_of_no_pairs += 1
                            new_tst_group_list.append(mapped_table.index(each_element))
                        
                        #save MAIN test vector to temporary list
                        temp.extend(patterns[mapped_table.index(each_element)])

                        #generate new extended test vector
                        if temp[local_index] == "1": temp[local_index] = "0"
                        elif temp[local_index] == "0": temp[local_index] = "1"

                        #add new extended test vector to stack
                        new_patterns.append(list(temp))
                        for bit in temp: 
                            if bit != "L" and bit != "H" and bit != "l" and bit != "h":
                                if disable_statistics: output_data.write(str(bit))
                        if disable_statistics: output_data.write("\n")
                        nr_of_pairs += 1

                        del temp[0:len(temp)]       #clear temporary list
                        agm_inps_local -= 1         #decrement number of inputs
                        insert_start_vector = 0     #reset watchdog, until new MAIN vector is processed                       

                        
                    local_index += 1
                    
        if insert_start_vector == 0:
            if disable_statistics: output_data.write(str(nr_of_pairs)+ " test pair(s) generated for T"+str(mapped_table.index(each_element))+ "\n\n")
            add_vector_nr.append(nr_of_pairs)                    
                    
    if disable_statistics: output_data.write("\nNo test pair(s) for "+str(len(patterns) - nr_of_no_pairs)+ " test vector(s)\n")
    output_data.write("----------------------------\n\n") 


def print_sim_result(result):
#function prints pairs of result tables after simulation

    j = 0
    for each_index in main_vector_indexes:
        for each_element in result:
            if result.index(each_element) == (each_index - 1):
                for i in range(1, add_vector_nr[j] + 1):
                        
                    output_data.write("T" +str(new_tst_group_list[j])+ "," +str(i)+ ":\t\t")
                    if isinstance (each_element, list):
                        for each_bit in each_element: output_data.write(str(each_bit))
                    output_data.write("\n")
                    output_data.write("T" +str(new_tst_group_list[j])+ "," +str(i)+ ":\t\t")
                    if isinstance (result[result.index(each_element) + i], list):
                        for each_bit in result[result.index(each_element) + i]: output_data.write(str(each_bit))
                    output_data.write("\n\n")                    

                j += 1
                if j == len(add_vector_nr): break      

def run_npsimul(filename, output_data):
#function runs the npsimul application

    global coverage

    #creating new tst file for npsimul simulator
    new_tst_data = open(filename+".tst", "w")

    new_tst_data.write("\n\n")
    new_tst_data.write(".VECTORS " +str(len(new_patterns)))
    new_tst_data.write("\n\n")
    new_tst_data.write(".PATTERNS")
    new_tst_data.write("\n")
    
    for each_element in new_patterns:
        new_tst_data.write("\n")
        if isinstance(each_element, list):
            for each_bit in each_element:
                if each_bit != "L" and each_bit != "H" and each_bit != "l" and each_bit != "h":
                    new_tst_data.write(str(each_bit))
                
    
    new_tst_data.close()

    #running npsimul.exe application
    try: os.system("external_tools\\npsimul.exe " +filename)
    except: pass
    
    #copying new test table to output log
    new_tst_data = open(filename+".tst", "rt")
    
    collect_data(new_tst_data, enable_logging)
    
    if disable_statistics: output_data.write("Extended test pattern table (after simulation):\n")
    if disable_statistics: output_data.write("----------------------------\n")
    
    if disable_statistics: print_sim_result(patterns)     
    
    if disable_statistics: output_data.write("\nExtended fault simulation table:\n")
    if disable_statistics: output_data.write("Indexes for inputs: "+str(int_global_index)+"\n")
    if disable_statistics: output_data.write("----------------------------\n")
    
    #TBD - this operation is failing!!!
    if disable_statistics: print_sim_result(table)
    
    output_data.write("COVERAGE: " +coverage+ "\n")
    new_tst_data.close()
    
def delay_fault_table(filename, output_data, enable_logging):
#function generates delay fault table
    
    delay_faults = list()
    delay_coverage = list()

    for i in range(len(patterns[0])):
        delay_coverage.append(False)
    
    if enable_logging: print(main_vector_indexes, add_vector_nr)
    
    if disable_statistics: output_data.write("\n")
    if disable_statistics: output_data.write("Delay fault table:\n")
    if disable_statistics: output_data.write("----------------------------\n\n")    
    
    j = 0
    for each_index in main_vector_indexes:
        for each_element in patterns:
            if patterns.index(each_element) == (each_index - 1):
                for i in range(1, add_vector_nr[j] + 1):
                    if enable_logging: print(i, j, each_element, patterns[patterns.index(each_element) + i])
                    if isinstance(each_element, list):
                        n = 0
                        for each_bit in each_element:
                            if enable_logging: print(each_bit, patterns[patterns.index(each_element) + i][n])
                            if (each_bit == "0" and patterns[patterns.index(each_element) + i][n] == "1"):
                                delay_faults.append("D")
                                delay_coverage[n] = True

                            elif (each_bit == "1" and patterns[patterns.index(each_element) + i][n] == "0"):
                                delay_faults.append("D")
                                delay_coverage[n] = True
                                
                            elif (each_bit == "l" and patterns[patterns.index(each_element) + i][n] == "h"):
                                delay_faults.append("D")
                                delay_coverage[n] = True
                            
                            elif (each_bit == "h" and patterns[patterns.index(each_element) + i][n] == "l"):
                                delay_faults.append("D")
                                delay_coverage[n] = True
                            
                            elif (each_bit == "L" and patterns[patterns.index(each_element) + i][n] == "H"):
                                delay_faults.append("D")
                                delay_coverage[n] = True
                            
                            elif (each_bit == "H" and patterns[patterns.index(each_element) + i][n] == "L"):
                                delay_faults.append("D")
                                delay_coverage[n] = True

                            else: delay_faults.append("X")
                            n += 1
                        
                        if disable_statistics: output_data.write("T" +str(new_tst_group_list[j])+ "," +str(i)+ ":\t\t")
                        for each_delay_fault in delay_faults: 
                            if disable_statistics: output_data.write(each_delay_fault)
                        if disable_statistics: output_data.write("\n")
                        del delay_faults[0:len(delay_faults)]

                j += 1
                if j == len(add_vector_nr): break

    tested_delay_faults = 0
    for each_fault in delay_coverage:
        if each_fault:
            tested_delay_faults += 1

    output_data.write("\nCOVERAGE: " +str(len(delay_coverage))+ " / " +str(tested_delay_faults)+ " = " +str(100 / (len(delay_coverage) / tested_delay_faults))+ " %\n")

stat_array = []         #0 - Nods, 1 - Vars, 2 - Grps, 3 - Inps, 4 - Cons, 5 - Outs
patterns = []           #list of test patterns from input tst
table = []              #list of test table from input tst
faults = []             #list of tested faults from input tst
new_patterns = []       #generated list of extended test patterns
main_vector_indexes = []#list of indexes of main vectors in new_patterns
add_vector_nr = []      #number of test pairs in each group in new_patterns
new_tst_group_list = [] #list of indexes for test pairs in Delay fault table
mapped_table = []       #re-arranged input fault table to match indexes with patterns
int_global_index = []   #indexes of inputs in fault table

prun = "y"              #variable to repeat the execution of the script
        
print("================================")
print("Delay Fault Test Generator v1.02")
print("Dmitri Mironov, mironov@smail.ee")
print("================================\n")

while True:
    if prun == "y":
        try:

            filename = input("Please enter model name:")
            #tst_filename = input("Please enter input tst name (example: ""iscas85/c17_in""):")
            in_data = open(filename+".tst", "rt") 
            #in_data = open(tst_filename+".tst", "rt")                          #open source file to read from
            agm_data = open(filename+".agm", "rt")  

            output_data = open(filename+"_out.txt", "w+")                         #open output file to write to     
            
            stat_array = gather_statistics(agm_data, stat_array)
            print("AGM statistics gathered...OK!")         
            
            print("\nProcessing... Please wait!\n")
            start_time = time.time()

            collect_data(in_data, enable_logging)
            map_table(in_data, agm_data, enable_logging)
            build_ext_table(filename, filename, output_data, enable_logging)
            #build_ext_table(filename, tst_filename, output_data, enable_logging)
            print("Extended test table generated... OK!")
            print("Time, used by process:", time.time() - start_time, "seconds\n")
            output_data.write("\nTime, used by process: " +str(time.time() - start_time)+" seconds\n\n\n")
            
            fault_generation_time = time.time()
            
            run_npsimul(filename, output_data)
            print("Fault simulation finished... OK!\n")
            delay_fault_table(filename, output_data, enable_logging)
            print("Delay fault table generated... OK!")
            print("Time, used by process:", time.time() - fault_generation_time, "seconds\n")
            output_data.write("\nTime, used by process: " +str(time.time() - fault_generation_time)+" seconds\n")
            
            sim_time = time.time() - start_time

            print("Total time, used by programm:", sim_time, "seconds")
            output_data.write("\n\nProgramm execution finished at " +str(sim_time)+ " seconds")
            print("Result saved to",filename+"_out.txt!")
            output_data.write("\nRun on " +str(time.asctime(time.localtime(time.time()))))

            in_data.close()
            output_data.close()
            agm_data.close()

            if input("\nPrint result (y/n)?") == "y": agmlibrary.print_file_on_screen (filename+"_out.txt", output_data)
            prun = input("Continue (y/n)?")
                
        except IOError: print("File does not exist!")

    elif prun == "n": break
