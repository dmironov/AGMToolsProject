#------------------------------------------------------------------------------#
#   AGM S3BDD SIMULATOR 2013
#
#   This is a Python script that simulates S3BDD models.
#   This does not work with gate-level and SSBDD models.
#   
#   Files:      agmlibrary.py, simlibrary.py, simulator.py 
#   Copyrights: Dmitri Mironov, 2013-2024
#   Contacts:   dmm.mironov@gmail.com
#
#------------------------------------------------------------------------------#

import time
import simlibrary
import agmlibrary

enable_logging = False                      #enable debug logging messages in shell window

def assign_inputs (filename, output_data):
#assigning input values of the circuit

    global inputs
    inputs = []                             #input vector values in the array

    input_index = 0                         #index of the "X" input, depend on the number of inputs
    current_input = list()                  #input vector values, read from the screen, later written in the inputs[] list
    agm_inps_local = stat_array[3]          #number of inputs in the agm file, used as counter

    del inputs[0:len(inputs)]
    del current_input[0:len(current_input)]

    print()
    print("Please Enter", stat_array[3],"bit Input Test Vector (without spaces!):")
    output_data.write("Input Test Vector of the " +str(filename)+ " Digital Circuit:\n\n")

    while agm_inps_local > 0:
        print("X" +str(input_index), end=" ")
        output_data.write("X" +str(input_index)+ " ")
        input_index += 1
        agm_inps_local -= 1

    output_data.write("\n")
    current_input = input("\n")
    inputs.extend(current_input)
    
    inputs = [int(each_element) for each_element in inputs]

    for each_item in inputs:
        output_data.write(str(each_item))

    output_data.write("\n\nOutput Values:\n\n")
    
def simulate_outputs (in_data, output_data, enable_logging):
#simulating the outputs

    node_value = 0              #binary value of the node
    next_node_index = 0         #local index of the next node line to be simulated
    int_var_index = 0           #index value of the simulated node "V = XXX"
    int_local_index = 0         #local index of the node line
    i = 0                       #temp help index

    #allocate the number of additional inputs and calculate its values
    indx_of_add_inputs = stat_array[1] - (stat_array[3] + stat_array[5])
    print("Start S3BDD additional output simulation...\n")
    while indx_of_add_inputs > 0:
        inputs.append(simlibrary.calculate_additional_inputs (in_data, inputs, stat_array, len_index_array, beg_index_array, temp, i, enable_logging))
        i += 1
        indx_of_add_inputs -= 1
        
    print("Start S3BDD output simulation...\n")

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
            
#Here the simulator code begins

stat_array = []         #0 - Nods, 1 - Vars, 2 - Grps, 3 - Inps, 4 - Cons, 5 - Outs
len_index_array = []    #len indexes of the agm file
beg_index_array = []    #beg indexes of the agm file
temp = []               #temp array of already simulated additional inputs

prun = "y"              #variable to repeat the execution of the script

while True:
    if prun == "y":
        try:

            filename = input("Please enter model name (example: ""iscas85/c17""):")
            in_data = open(filename+".agm", "rt")                          #open source file to read from

            output_data = open("output.txt", "w+")                  #open output file to write to
            temp_data = open("temp", "w+")                          #temporary data file (optional)
            
            (stat_array, len_index_array, beg_index_array) = agmlibrary.gather_statistics(in_data, stat_array, len_index_array, beg_index_array)
            print("AGM statistics gathered...OK!")

            assign_inputs(filename, output_data)
            
            print("\nStarting simulation... Please wait!\n")
            start_time = time.time()
            simulate_outputs(in_data, output_data, enable_logging)

            sim_time = time.time() - start_time

            print("Simulation finished at", sim_time, "seconds")
            output_data.write("\nSimulation finished at " +str(sim_time)+ " seconds")
            print("Result saved to output.txt!")
            output_data.write("\nSimulated on " +str(time.asctime(time.localtime(time.time()))))
            prun = input("Continue (y/n)?")

            agmlibrary.close_files(in_data, output_data, temp_data)
                
        except IOError: print("File does not exist!")

    elif prun == "n": break
