"""
Created on Fri Apr 16 15:23:25 2021

@author: skmandal@wisc.edu, agoksoy@wisc.edu
"""

import os, re, glob, sys, math, shutil
import numpy as np
from noc_simulation_edge_based import noc_simulation_edge_based


def run_simulations(wl_name, num_chips, num_layers, mesh_size_array, scales, quantization_bit, mode, debug_required):
    for mesh_size in mesh_size_array:
        for chip in range(num_chips):
            print('Simulating ' + wl_name + ' for chip ' + str(chip+1))
            trace_exists = os.path.exists('trace_file_' + wl_name + '/trace_file_' + wl_name + '_chip_' + str(chip+1) +'_layer_0_mesh_size_' + str(mesh_size)+ '_bit_' + str(quantization_bit)  + '_scale_' + str(scales[0]) + '.txt')
            if trace_exists:
                dir_name = 'logs_mesh_size_' + str(mesh_size) + '_bit_' + str(quantization_bit)  + '_' + wl_name + '_chip_' + str(chip+1) 
                os.system('mkdir ' + dir_name)
                os.system('mkdir ' + dir_name + '/configs')
                noc_simulation_edge_based(wl_name, num_chips, num_layers, mesh_size, scales, quantization_bit, mode, debug_required)
                os.system('mv logs/comm_latency_' + wl_name + '_chip_' + str(chip+1) + '_mesh_' + str(mesh_size) + '_each_layer.csv ' + dir_name)
                os.system('mv logs/comm_power_' + wl_name + '_chip_' + str(chip+1) + '_mesh_' + str(mesh_size) + '_each_layer.csv ' + dir_name)
                os.system('mv logs/comm_energy_' + wl_name + '_chip_' + str(chip+1) + '_mesh_' + str(mesh_size) + '_each_layer.csv ' + dir_name)
                os.system('mv logs/comm_area_' + wl_name + '_chip_' + str(chip+1) + '_mesh_' + str(mesh_size) + '.csv ' + dir_name)
                os.system('mv logs/' + wl_name + '_chip_' + str(chip+1) + '_layer_*_mesh_' + str(mesh_size) + '.log ' + dir_name)
                os.system('mv logs/configs/' + wl_name + '_chip_' + str(chip+1) + '_layer_*_mesh_' + str(mesh_size) + '_config ' + dir_name + '/configs/')
            else:
                if debug_required:
                    print('[ INFO] Trace does not exist for ' + str(wl_name) + ' chip ' + str(chip+1) + ' mesh size ' + str(mesh_size) + ' \n')

