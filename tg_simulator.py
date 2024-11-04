#------------------------------------------------------------------------------#
#   TEST GROUP S3BDD SIMULATOR 2013
#
#   This is a Python script testing S3BDD models using test group concept.
#   This does not work with gate-level and SSBDD models.
#   
#   Files:      agmlibrary.py, simlibrary.py, tg_simulator.py 
#   Copyrights: Dmitri Mironov, 2013-2024
#   Contacts:   dmm.mironov@gmail.com
#
#------------------------------------------------------------------------------#

import time
import simlibrary
import agmlibrary

enable_logging = False                      #enable debug logging messages in shell window

def assign_inputs (filename, output_data, enable_logging):
#assigning input values of the circuit

    global inputs, tg_index
    inputs = []                             #input vector values in the array
    tg_index = []                           #list of test group bit indexes

    input_index = 0                         #index of the "X" input, depend on the number of inputs
    current_input = list()                  #input vector values, read from the screen, later written in the inputs[] list
    agm_inps_local = stat_array[3]          #number of inputs in the agm file, used as counter

    del inputs[0:len(inputs)]
    del current_input[0:len(current_input)]

    print()
    print("Select test group variable indexes, at the end press ENTER:")
    output_data.write("TEST GROUP SIMULATION OUTPUT FILE\n\n")
    output_data.write("Inputs of the " +str(filename)+ " Digital Circuit:\n")

    while agm_inps_local > 0:
        print("X" +str(input_index), end=" ")
        output_data.write("X" +str(input_index)+ " ")
        input_index += 1
        agm_inps_local -= 1

    print("\n")

    while True:
        current_input = input()
        if current_input.isdigit():
            tg_index.append(current_input)
        else: break
    
    #creating list of test group bit indexes
    tg_index = [int(each_element) for each_element in tg_index]
    if enable_logging: print("TV indexes are:", tg_index)

    output_data.write("\n\nTV (Test Variables):\n")
    for each_item in tg_index: output_data.write("X" +str(each_item)+ " ")

    output_data.write("\n\nOutput Values:\n")

def calc_spare_inputs(in_data, enable_logging):
#calculates values for spare inputs (does not belong to TG) of the test vector

    int_var_index = 0                   #index value of the simulated node "V = XXX"
    zero_successor = 0                  #zero_successor found
    one_successor = 0                   #one_successor found
    inputs_printed = list()             #list of inputs with "X" values, which is printed out in the output

    #creating empty test-vector
    run = [inputs.append(None) for run in range (0, stat_array[3])]
    run = [inputs_printed.append(None) for run in range (0, stat_array[3])]

    for each_line in in_data:
        #find the variable index of the node
        if not each_line.find("V = ") == -1:
            #assign the binary value to the node
            int_var_index = agmlibrary.save_element(0, each_line, "V = ", ' "')

            if (int_var_index < stat_array[3]) and (int_var_index not in tg_index):
                #go to "zero" successor of the node
                if not each_line.find(") ( ") == -1:
                    zero_successor = agmlibrary.save_element(0, each_line, ") ( ", " ")

                #go to "one" successor of the node
                if not each_line.find(") V") == -1:
                    (line_data, successor_data) = each_line.split(") V", 1)
                    one_successor = agmlibrary.save_element(3, line_data, ") ( ", " ")

                #comparing successors and assigning input value
                if (zero_successor == 0) and (one_successor == 0):
                    inputs[int_var_index] = 0
                    inputs_printed[int_var_index] = "X"
                    continue
                elif zero_successor == 0:
                    inputs[int_var_index] = 1
                    inputs_printed[int_var_index] = "X"
                    continue
                elif one_successor == 0:
                    inputs[int_var_index] = 0
                    inputs_printed[int_var_index] = "X"
                    continue
                elif zero_successor < one_successor:
                    inputs[int_var_index] = 0
                    inputs_printed[int_var_index] = "X"
                elif one_successor < zero_successor:
                    inputs[int_var_index] = 1
                    inputs_printed[int_var_index] = "X"

    return inputs_printed

                
def calc_test_vector (output_data):
#create new test vector
        
    global run_index            #counter for generating test groups

    inputs_printed = calc_spare_inputs(in_data, enable_logging)

    #selected test group generation
    for each_element in tg_index:
        inputs[each_element] = 1
        inputs_printed[each_element] = 1

    if run_index > 0: inputs[tg_index[run_index - 1]] = 0
    if run_index > 0: inputs_printed[tg_index[run_index - 1]] = 0

    output_data.write("\nTest vector ")
    for each_element in inputs_printed: output_data.write(str(each_element))
    output_data.write(" simulation output:\n")                             
    
    run_index += 1
    

def simulate_outputs (in_data, output_data, enable_logging):
#simulating the outputs

    node_value = 0              #binary value of the node
    next_node_index = 0         #local index of the next node line to be simulated
    int_var_index = 0           #index value of the simulated node "V = XXX"
    int_local_index = 0         #local index of the node line
    i = 0                       #temp help index

    #creating new test vector before each simulation cycle
    calc_test_vector (output_data)
    if enable_logging: print("Test vector", run_index, "simulation started...OK!")

    #allocate the number of additional inputs and calculate its values
    indx_of_add_inputs = stat_array[1] - (stat_array[3] + stat_array[5])
    if enable_logging: print("Start S3BDD additional output simulation...OK!")
    while indx_of_add_inputs > 0:
        inputs.append(simlibrary.calculate_additional_inputs (in_data, inputs, stat_array, len_index_array, beg_index_array, temp, i, enable_logging))
        i += 1
        indx_of_add_inputs -= 1
        
    if enable_logging: print("Start S3BDD output simulation...OK!\n")

    for each_line in in_data:
        #find the output graph
        if not each_line.find("_o__") == -1:
            output_name = agmlibrary.save_element(0, each_line, ' "', '"')

            for each_line in in_data:
                #find the variable index of the node
                if not each_line.find("V = ") == -1:
                    #assign the binary value to the node
                    int_var_index = agmlibrary.save_element(0, each_line, "V = ", ' "')
                    node_value = inputs[int_var_index]

                    if not each_line.find(":") == -1:
                        #find the local index of the node line
                        int_local_index = agmlibrary.save_element(1, each_line, ":", " ")

                    #apply inversion rule
                    node_value = simlibrary.invert_value(each_line, node_value, enable_logging)

                    if next_node_index == int_local_index:
                        #start node simulation
                        if enable_logging: print("Simulated node V =", int_var_index, "value is:", node_value)
                        next_node_index = simlibrary.simulate_node(each_line, next_node_index, node_value, enable_logging)
                        
                        if next_node_index == 0:
                            #"null" node is found, assign graph output value
                            if enable_logging: print("Output", output_name, "=", node_value, "calculated...OK!\n")
                            output_data.write(output_name + " = " + str(node_value))
                            output_data.write("\n")
                            break
                    
    in_data.seek(0)
    del inputs[0:len(inputs)]
    del temp[0:len(temp)]
            
#Here the simulator code begins

stat_array = []         #0 - Nods, 1 - Vars, 2 - Grps, 3 - Inps, 4 - Cons, 5 - Outs
len_index_array = []    #len indexes of the agm file
beg_index_array = []    #beg indexes of the agm file
temp = []               #temp array of already simulated additional inputs

prun = "y"              #variable to repeat the execution of the script

while True:
    if prun == "y":
        try:

            #internal index for cacl_test_vector function
            run_index = 0 

            filename = input("Please enter model name (example: ""iscas85/c17""):")
            in_data = open(filename+".agm", "rt")                          #open source file to read from

            output_data = open("output.txt", "w+")                  #open output file to write to
            temp_data = open("temp", "w+")                          #temporary data file (optional)
            
            (stat_array, len_index_array, beg_index_array) = agmlibrary.gather_statistics(in_data, stat_array, len_index_array, beg_index_array)
            print("AGM statistics gathered...OK!")

            assign_inputs(filename, output_data, enable_logging)
            
            print("\nStarting simulation... Please wait!\n")
            start_time = time.time()
            run = [simulate_outputs(in_data, output_data, enable_logging) for run in range(0, len(tg_index) + 1)]

            sim_time = time.time() - start_time

            print("Simulation finished at", sim_time, "seconds")
            output_data.write("\nSimulation finished at " +str(sim_time)+ " seconds")
            print("Result saved to output.txt!")
            output_data.write("\nSimulated on " +str(time.asctime(time.localtime(time.time()))))

            agmlibrary.close_files(in_data, output_data, temp_data)

            if input("Print result (y/n)?") == "y": agmlibrary.print_file_on_screen ("output.txt", output_data)
            prun = input("Continue (y/n)?")
                
        except IOError: print("File does not exist!")

    elif prun == "n": break
