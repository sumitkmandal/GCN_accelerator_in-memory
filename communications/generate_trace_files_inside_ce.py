# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 15:23:25 2021

@author: skmandal@wisc.edu, agoksoy@wisc.edu
"""

import os
import re
import numpy as np
from datetime import datetime
import shutil
import copy


def generate_trace_files_inside_ce(wl_name, num_gnn_nodes, num_features_each_layer, num_layers, scales, num_chips, quantization_bit, bus_width, mesh_size_array, num_inside_routers):

    connection_filename = './workloads/' + wl_name + '.csv'
    
    dir_name = './booksim_' + wl_name + '/trace_file_' + wl_name
    
    os.makedirs(dir_name + '_low', exist_ok = True)
    os.makedirs(dir_name + '_high', exist_ok = True)
    
    for mesh_size in mesh_size_array:
    
        for layer_idx in range(0, num_layers):    
            num_routers = mesh_size*mesh_size
            num_nodes_per_router = np.ceil(num_gnn_nodes/num_routers)
            num_nodes_inside_ce = np.ceil(num_nodes_per_router/num_inside_routers)
            num_features = num_features_each_layer[layer_idx]
            scale_layer = scales[layer_idx]
    
            for chip in range(num_chips):
                trace_file = np.array([[0,0,0]])
                timestamps_last = np.zeros([1, num_inside_routers], dtype='int')
                # Calculating each router's communcation with another router based on the nodes assigned to that tile
                connections_array = open(connection_filename)
                packets_to = np.zeros((num_routers, 30, 30))            
                for router in range(num_routers):
                    for node in range(int(num_nodes_per_router)):
                        connections_line = connections_array.readline().rstrip('\n').split(',')
                        for edge_to in range(len(connections_line)):
                            if edge_to == 0:
                                if connections_line[edge_to] == '':
                                    break
                                router_from = int(np.ceil(int(connections_line[edge_to]) % num_nodes_per_router) / num_nodes_inside_ce)
                                continue
                            if int(int(connections_line[edge_to]) / num_nodes_per_router) < (chip+1)*num_routers and int(int(connections_line[edge_to]) / num_nodes_per_router) >= chip*num_routers :
                                if int(int(connections_line[edge_to]) / num_nodes_per_router) % num_routers == router:
                                    router_to = int(int(int(connections_line[edge_to]) % num_nodes_per_router) / num_nodes_inside_ce)
                                    packets_to[router][router_from][router_to] += 1
            
                highest_inside_ce = np.argmax(np.sum(np.sum(packets_to,axis=1),axis=1))
                temp_lowest = np.sum(np.sum(packets_to,axis=1),axis=1)
                sorted_packets = np.argsort(temp_lowest)
                if np.sum(temp_lowest) == 0:
                    #if layer_idx ==0:
                        #print(mesh_size, chip+1, '  \t', 0)
                    continue
                lowest_inside_ce = np.where(temp_lowest == np.min(temp_lowest[temp_lowest.nonzero()]))[0][0]
                if temp_lowest[highest_inside_ce] == temp_lowest[lowest_inside_ce]:
                    highest_inside_ce = sorted_packets[-1]
                lowest_id = np.where(np.argsort(temp_lowest) == lowest_inside_ce)[0][0]
                for idx in range(0,lowest_id):
                    sorted_packets = np.delete(sorted_packets,0)
                    lowest_id -= 1
                traces = ['low','high']
                for trace in traces:
                    rerun = True
                    while rerun:
                        if trace == 'low':
                            num_packets = np.ceil(num_features*quantization_bit * packets_to[lowest_inside_ce]/(bus_width*scale_layer))
                        elif trace == 'high':
                            num_packets = np.ceil(num_features*quantization_bit * packets_to[highest_inside_ce]/(bus_width*scale_layer))
                        trace_file = np.array([[0,0,0]])
                        timestamps_last = np.zeros([1, num_inside_routers], dtype='int')                    
                        for src_router in range (0, num_inside_routers):
                            for dest_router in range (0, num_inside_routers):
                            
                                if (dest_router != src_router):
                                
                                    timestamp = timestamps_last[0][src_router]
                                    
                                    for pack_idx in range (0, int(num_packets[src_router][dest_router])):
                                        trace_file = np.append(trace_file, [[src_router, dest_router, timestamp]], axis=0)
                                        timestamp = timestamp + 1
                                    
                                    timestamps_last[0][src_router] = timestamp
                        if np.sum(timestamps_last[0]) == 0:
                            if sorted_packets.size == 1:
                                break
                            if trace == 'low':
                                if sorted_packets.size == 0:
                                    break
                                sorted_packets = np.delete(sorted_packets,lowest_id)
                                lowest_id = 0
                                lowest_inside_ce = sorted_packets[0]
                                rerun = True
                                continue
                            else:
                                if sorted_packets.size == 0:
                                    break
                                sorted_packets = np.delete(sorted_packets,-1)
                                highest_inside_ce = sorted_packets[-1]
                                rerun = True
                                continue                            
                        else:
                            rerun = False
                        trace_file = np.delete(trace_file, 0, 0)
                        trace_file = trace_file[np.argsort(trace_file[:,2])]
                        #if layer_idx == 0 and trace == 'high':
                            #print(mesh_size, chip+1, '  \t', sorted_packets.size)
                        np.savetxt(dir_name + '_' + trace + '/trace_file_' + wl_name + '_' + trace + '_chip_' + str(chip+1) + '_layer_'+ str(layer_idx) + '_mesh_size_' + str(mesh_size) + '_bit_' + str(quantization_bit) + '_scale_' + str(scale_layer) + '.txt', trace_file, fmt='%i')
