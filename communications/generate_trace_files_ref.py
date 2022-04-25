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


wl_name = 'cora' #'cora' #'citeseer' #'pubmed'  #'ext_cora' #'nell'

if wl_name == 'cora':
    num_gnn_nodes = 2708 #2708 # 3327 #19717 #19793 #65755
    num_features_each_layer = [1433, 16] #[1433, 16] #[3703, 16] #[500, 16] #[8710, 16] #[5414, 16]
    scales = [100,1]#20#10
    num_chips = 1 #20#45#3
elif wl_name == 'citeseer':
    num_gnn_nodes = 3327 #2708 # 3327 #19717 #19793 #65755
    num_features_each_layer = [3703, 16] #[1433, 16] #[3703, 16] #[500, 16] #[8710, 16] #[5414, 16]
    scales = [100,1]#20#10
    num_chips = 1 #20#45#3
elif wl_name == 'pubmed':
    num_gnn_nodes = 19717 #2708 # 3327 #19717 #19793 #65755
    num_features_each_layer = [500, 16] #[1433, 16] #[3703, 16] #[500, 16] #[8710, 16] #[5414, 16]
    scales = [20,1]#20#10
    num_chips = 3 #20#45#3    
elif wl_name == 'ext_cora':
    num_gnn_nodes = 19793 #2708 # 3327 #19717 #19793 #65755
    num_features_each_layer = [8710, 16] #[1433, 16] #[3703, 16] #[500, 16] #[8710, 16] #[5414, 16]
    scales = [100,1]#20#10
    num_chips = 20 #20#45#3    
elif wl_name == 'nell':
    num_gnn_nodes = 65755 #2708 # 3327 #19717 #19793 #65755
    num_features_each_layer = [5414, 16] #[1433, 16] #[3703, 16] #[500, 16] #[8710, 16] #[5414, 16]
    scales = [10,1]#20#10
    num_chips = 45 #20#45#3   

num_gnn_nodes = np.ceil(num_gnn_nodes/num_chips)
num_layers = len(num_features_each_layer)

quantization_bit = 4
bus_width = 32

dir_name = './booksim_' + wl_name + '/trace_file_' + wl_name + '_ref'

os.makedirs(dir_name + '_e_to_v', exist_ok = True)
os.makedirs(dir_name + '_v_to_e', exist_ok = True)
   
    
# mesh_size_array = [4, 5, 6, 7, 8, 9, 10]
# mesh_size_array = [5,6,7]
mesh_size_array = [4]

num_vertex_ce = 12
num_edge_ce = 4

for mesh_size in mesh_size_array:

    for layer_idx in range(0, num_layers):    
        num_routers = mesh_size*mesh_size
        num_nodes_per_router = np.ceil(num_gnn_nodes/(num_routers-4))
        num_features = num_features_each_layer[layer_idx]
        scale_layer = scales[layer_idx]

        for chip in range(num_chips):
            trace_file = np.array([[0,0,0]])
            timestamps_last = np.zeros([1, num_routers], dtype='int')
            # Calculating each router's communcation with another router based on the nodes assigned to that tile
            # connections_array = open(connection_filename)
            num_packets_e_to_v = np.zeros((num_routers, num_routers))
            num_packets_v_to_e = np.zeros((num_routers, num_routers))
            if layer_idx != 2:
                packets_e_to_v = np.ceil((num_gnn_nodes * num_features * quantization_bit) / (num_vertex_ce * num_edge_ce * bus_width * scale_layer))
                packets_v_to_e = np.ceil((num_gnn_nodes * num_features * quantization_bit) / (num_vertex_ce * bus_width * scale_layer))
            else:
                packets_v_to_e = np.ceil((num_gnn_nodes * num_features * quantization_bit) / (num_vertex_ce * bus_width * scale_layer))
            if layer_idx != 2:
                for router in range(0, num_routers):
                    if router < 8 or router >= 12:
                        num_packets_v_to_e[router][8:12] = packets_v_to_e 
                    else:
                        num_packets_e_to_v[router][0:8] = packets_e_to_v                     
                        num_packets_e_to_v[router][12:16] = packets_e_to_v    
            else:
                for router in range(0, num_routers):
                    if router < 8 or router >= 12:
                        num_packets_v_to_e[router][8:12] = packets_v_to_e               
            if layer_idx != 2:
                for src_router in range (0, num_routers):
                    for dest_router in range (0, num_routers):
                    
                        if (dest_router != src_router):
                        
                            timestamp = timestamps_last[0][src_router]
                            
                            for pack_idx in range (0, int(num_packets_e_to_v[src_router][dest_router])):
                                trace_file = np.append(trace_file, [[src_router, dest_router, timestamp]], axis=0)
                                timestamp = timestamp + 1
                            # print(timestamp)
                            timestamps_last[0][src_router] = timestamp
                trace_file = np.delete(trace_file, 0, 0)
                trace_file = trace_file[np.argsort(trace_file[:,2])]
                np.savetxt(dir_name + '_e_to_v/trace_file_' + wl_name + '_ref_e_to_v_chip_' + str(chip+1) + '_layer_'+ str(layer_idx) + '_mesh_size_' + str(mesh_size) + '_bit_' + str(quantization_bit) + '_scale_' + str(scale_layer) + '.txt', trace_file, fmt='%i')
                trace_file = np.array([[0,0,0]])
                timestamps_last = np.zeros([1, num_routers], dtype='int')
            # timestamps_last[0] = np.max(timestamps_last[0])
            for src_router in range (0, num_routers):
                for dest_router in range (0, num_routers):
                
                    if (dest_router != src_router):
                    
                        timestamp = timestamps_last[0][src_router]
                        
                        for pack_idx in range (0, int(num_packets_v_to_e[src_router][dest_router])):
                            trace_file = np.append(trace_file, [[src_router, dest_router, timestamp]], axis=0)
                            timestamp = timestamp + 1
                        
                        timestamps_last[0][src_router] = timestamp
                        
            trace_file = np.delete(trace_file, 0, 0)
            trace_file = trace_file[np.argsort(trace_file[:,2])]
            # trace_file = trace_file[np.argsort(trace_file[:,0])]      
            np.savetxt(dir_name + '_v_to_e/trace_file_' + wl_name + '_ref_v_to_e_chip_' + str(chip+1) + '_layer_'+ str(layer_idx) + '_mesh_size_' + str(mesh_size) + '_bit_' + str(quantization_bit) + '_scale_' + str(scale_layer) + '.txt', trace_file, fmt='%i')
