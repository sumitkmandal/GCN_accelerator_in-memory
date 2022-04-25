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
from generate_trace_files import generate_trace_files
from generate_trace_files_inside_ce import generate_trace_files_inside_ce
from run_simulations import run_simulations 


wl_name = 'cora' #'cora' #'citeseer' #'pubmed'  #'ext_cora' #'nell'

if wl_name == 'cora':
    num_gnn_nodes = 2708 #2708 # 3327 #19717 #19793 #65755
    num_features_each_layer = [1433, 16] #[1433, 16] #[3703, 16] #[500, 16] #[8710, 16] #[5414, 16]
    scales = [1000,10]#20#10
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
mesh_size_array = [4]
debug_required = 1
mode = ''
num_inside_routers = 30

dir_name = './booksim_' + wl_name

if (os.path.isdir(dir_name)):
    shutil.rmtree(dir_name)


#inter-ce communication

print('Starting simulation for inter-CE communication')
generate_trace_files(wl_name, num_gnn_nodes, num_features_each_layer, num_layers, scales, num_chips, quantization_bit, bus_width, mesh_size_array)
print('Trace generation completed')

os.chdir(dir_name)
os.system('cp ../booksim .') #copying booksim
os.system('chmod +x booksim') #providing permission

os.system('cp ../mesh_config_trace_based .') #copying booksim
os.system('cp ../techfile.txt .') #copying booksim
run_simulations(wl_name, num_chips, num_layers, mesh_size_array, scales, quantization_bit, mode, debug_required)
os.chdir('..')


#intra-ce communication

print('Starting simulation for intra-CE communication')
generate_trace_files_inside_ce(wl_name, num_gnn_nodes, num_features_each_layer, num_layers, scales, num_chips, quantization_bit, bus_width, mesh_size_array, num_inside_routers)
print('Trace generation completed')
os.chdir(dir_name)


wl_name_high = wl_name + '_high'

run_simulations(wl_name_high, num_chips, num_layers, mesh_size_array, scales, quantization_bit, mode, debug_required)

wl_name_low = wl_name + '_low'

run_simulations(wl_name_low, num_chips, num_layers, mesh_size_array, scales, quantization_bit, mode, debug_required)

os.chdir('..')
 

