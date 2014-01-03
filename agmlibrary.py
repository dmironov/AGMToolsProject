#--------------------------------------------------------------------------------------------------#
#   AGM LIBRARY
#
#   print_file_on_screen: reads out the file and prints it on the screen (debug only)
#   close_files: close input, output and temp files. Removes temp file
#   save_element: finds the target element between two strings and returns it as a string or integer
#   gather_statistics: gathers all statistics about the agm file
#
#   Copyrights: Dmitri Mironov, 2013
#   Contacts:   mironov@smail.ee
#
#--------------------------------------------------------------------------------------------------#

import os

def print_file_on_screen (filename, in_data):
#function that prints out contents of the file on the screen
    
    in_data = open(filename, "rt")

    print()
    print("===================================================")
    print("The file", filename, "will be printed out below:")
    print("===================================================")
    print()

    text = in_data.read()
    print(text)

    in_data.seek(0)
    in_data.close()


def close_files (in_data, output_data, temp_data):
#close all files when program is finished

    in_data.close()
    output_data.close()
    temp_data.close()
    os.remove("temp")


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
            stat_array.remove("Nods,")
            stat_array.remove("Vars,")
            stat_array.remove("Grps,")
            stat_array.remove("Inps,")
            stat_array.remove("Cons,")
            stat_array.remove("Outs")


        if not each_line.find("BEG =") == -1:
            #save beginning values to the list
            beg_index_array.append(save_element(0, each_line, "BEG = ", ", LEN ="))       

        if not each_line.find("LEN =") == -1:
            #save lenght values to the list
            len_index_array.append(save_element(0, each_line, "LEN = ", " -"))

    stat_array = [int(each_element) for each_element in stat_array]

    in_data.seek(0)
    return (stat_array, len_index_array, beg_index_array)
