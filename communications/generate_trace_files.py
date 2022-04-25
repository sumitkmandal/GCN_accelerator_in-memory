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


def generate_trace_files(wl_name, num_gnn_nodes, num_features_each_layer, num_layers, scales, num_chips, quantization_bit, bus_width, mesh_size_array):

    connection_filename = './workloads/' + wl_name + '.csv'
    dir_name = './booksim_' + wl_name + '/trace_file_' + wl_name
    
    os.makedirs(dir_name, exist_ok = True)
       
        
    for mesh_size in mesh_size_array:
    
        for layer_idx in range(0, num_layers):    
            num_routers = mesh_size*mesh_size
            num_nodes_per_router = np.ceil(num_gnn_nodes/num_routers)
            num_features = num_features_each_layer[layer_idx]
            scale_layer = scales[layer_idx]
    
            for chip in range(num_chips):
                trace_file = np.array([[0,0,0]])
                timestamps_last = np.zeros([1, num_routers], dtype='int')
                # Calculating each router's communcation with another router based on the nodes assigned to that tile
                connections_array = open(connection_filename)
                packets_to = np.zeros((num_routers, num_routers))
                for router in range(num_routers):
                    for node in range(int(num_nodes_per_router)):
                        connections_line = connections_array.readline().rstrip('\n').split(',')
                        for edge_to in range(len(connections_line)):
                            if edge_to == 0:
                                continue
                            if int(int(connections_line[edge_to]) / num_nodes_per_router) < (chip+1)*num_routers and int(int(connections_line[edge_to]) / num_nodes_per_router) >= chip*num_routers :
                                packets_to[router][ int(int(connections_line[edge_to]) / num_nodes_per_router) % num_routers ] += 1
            
                num_packets = np.ceil(num_features*quantization_bit * packets_to/(bus_width*scale_layer))
                for src_router in range (0, num_routers):
                    for dest_router in range (0, num_routers):
                    
                        if (dest_router != src_router):
                        
                            timestamp = timestamps_last[0][src_router]
                            
                            for pack_idx in range (0, int(num_packets[src_router][dest_router])):
                                trace_file = np.append(trace_file, [[src_router, dest_router, timestamp]], axis=0)
                                timestamp = timestamp + 1
                            
                            timestamps_last[0][src_router] = timestamp
                
                trace_file = np.delete(trace_file, 0, 0)
                trace_file = trace_file[np.argsort(trace_file[:,2])]
                # trace_file = trace_file[np.argsort(trace_file[:,0])]      
                np.savetxt(dir_name + '/trace_file_' + wl_name + '_chip_' + str(chip+1) + '_layer_'+ str(layer_idx) + '_mesh_size_' + str(mesh_size) + '_bit_' + str(quantization_bit) + '_scale_' + str(scale_layer) + '.txt', trace_file, fmt='%i')
