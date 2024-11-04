#------------------------------------------------------------------------------------------------------------------#
#   SIM LIBRARY
#
#   simulate_node: successor router in the node
#   invert_value: apply inversion rule, if the node value is inverted
#   calculate_additional_inputs: calculates value of additional input of S3BDD
#
#   Copyrights: Dmitri Mironov, 2013-2024
#   Contacts:   dmm.mironov@gmail.com
#
#------------------------------------------------------------------------------------------------------------------#

import agmlibrary
import sys

def simulate_node (each_line, next_node_index, node_value, enable_logging):
#successor router in the node

    if node_value == 0:
        #go to "zero" successor of the node
        if not each_line.find(") ( ") == -1:
            #assign next node line to be simulated
            next_node_index = agmlibrary.save_element(0, each_line, ") ( ", " ")

    elif node_value == 1:
        #go to "one" successor of the node
        if not each_line.find(") V") == -1:
            (line_data, successor_data) = each_line.split(") V", 1)
                                                                    
            #assign next node line to be simulated
            next_node_index = agmlibrary.save_element(3, line_data, ") ( ", " ")

    if enable_logging: print("Next node index is:", next_node_index)
    return next_node_index


def invert_value (each_line, node_value, enable_logging):
#apply inversion rule, if the node value is inverted

    if not each_line.find("I__") == -1:
        if node_value == 0:
            node_value = 1
            if enable_logging: print("Inversion detected 0 -> 1")
        elif node_value == 1:
            node_value = 0
            if enable_logging: print("Inversion detected 1 -> 0")

    return node_value

def calculate_additional_inputs (in_data, inputs, stat_array, len_index_array, beg_index_array, temp, i, enable_logging):

    node_value = 0                  #binary value of the node
    next_node_index = None          #local index of the next node line to be simulated
    int_var_index = 0               #index value of the simulated node "V = XXX"
    int_local_index = 0             #local index of the node line
    int_global_index = 0            #global index of the node line
    len_index = len_index_array[i]  #local index of the length of the simulated graph

    sys.setrecursionlimit(10000)

    for each_line in in_data:
        #find the output graph
        if not each_line.find("_o__") == -1:
            for each_line in in_data:
                #find the variable index of the node
                if not each_line.find("V = ") == -1:
                    #find the index of the simulated node
                    int_var_index = agmlibrary.save_element(0, each_line, "V = ", ' "')

                    if not each_line.find(":") == -1:
                        #find the local and the global indexes of the node line
                        int_global_index = agmlibrary.save_element(2, each_line, ":", " ")
                        int_local_index = agmlibrary.save_element(1, each_line, ":", " ")

                    if beg_index_array[i] == int_global_index:
                        #detect begenning of the additional input
                        if enable_logging: print("Additional input found! V =", len(inputs))
                        next_node_index = int_local_index
                        
                    if next_node_index == int_local_index:
                        #assign the binary value to the node
                        if int_var_index > len(inputs) - 1:
                            if int_var_index in temp:
                                node_value = temp[temp.index(int_var_index) + 1]
                                if enable_logging: print("Found earlier simulated node", temp[temp.index(int_var_index)], temp[temp.index(int_var_index) + 1] )
                            else:
                                node_value = calculate_additional_inputs (in_data, inputs, stat_array, len_index_array, beg_index_array, temp, int_var_index - stat_array[3], enable_logging)
                                temp.append(int_var_index)
                                temp.append(node_value)
                        else:
                            node_value = inputs[int_var_index]

                        #apply inversion rule
                        node_value = invert_value(each_line, node_value, enable_logging)
                        #start node simulation
                        if enable_logging: print("Simulated node V =", int_var_index, "value is:", node_value)
                        next_node_index = simulate_node(each_line, next_node_index, node_value, enable_logging)
                        len_index -= 1
                            
                        if len_index == 0:
                            #length of the graph exceeded, break and return graph output value
                            if enable_logging: print("Additional input V =", len(inputs),"calculated value is", node_value, "\n")
                            break
    in_data.seek(0)
    return node_value
