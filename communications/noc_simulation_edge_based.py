#!/usr/bin/python
# python run_booksim.py <directory to injection file>


import os, re, glob, sys, math
import numpy as np


def noc_simulation_edge_based(wl_name, num_chips, num_layers, mesh_size, scales, quantization_bit, mode, debug_required):


    os.system('chmod +x booksim')

    # trace_file_dir = 'trace_file_' + wl_name + '_' + mode    
    trace_file_dir = 'trace_file_' + wl_name    
    
    # Get a list of all files in directory
    files = glob.glob(trace_file_dir + '/*txt')
    
    # Initialize file counter
    file_counter = 0
    
    # Create directory to store config files
    os.system('mkdir -p ./logs/configs')
    
    total_area = 0


    prev_latency = '100'
    prev_area = '1'
    prev_power = '10'
    
    # Perform simulation for each layer    
    # Iterate over all files
    for chip in range(num_chips):
        for layer_idx in range(0, num_layers):
        #for file in files :
        
        
            print('Analyzing communication performance for layer ' + str(layer_idx+1) + '\n')
            #print(str(scales[layer_idx])) 
            # trace file
            #file_name = 'trace_file_' + mode + '_' +  wl_name + '_layer_' + str(layer_idx) + '_mesh_size_' + str(mesh_size)+ '_bit_' + str(quantization_bit)  + '_scale_' + str(scale) + '.txt'
            #file_name = 'trace_file_' + wl_name + '_layer_' + str(layer_idx) + '_mesh_size_' + str(mesh_size)+ '_bit_' + str(quantization_bit)  + '_scale_' + str(scales[layer_idx]) + '.txt'
            file_name = 'trace_file_' + wl_name + '_chip_' + str(chip+1) +'_layer_' + str(layer_idx) + '_mesh_size_' + str(mesh_size)+ '_bit_' + str(quantization_bit)  + '_scale_' + str(scales[layer_idx]) + '.txt'
        
            # Open read file handle of config file
            fp = open('./mesh_config_trace_based', 'r')
            #fp = open('./cmesh_config_trace_based', 'r')
        
            # Set path to config file
            config_file = './logs/configs/' + wl_name + '_chip_' + str(chip+1) + '_layer_' + str(layer_idx) + '_mesh_' + str(mesh_size) + '_config'
            #config_file = './logs/configs/layer_' + str(layer_idx) + '_cmesh_config'
        
            # Open write file handle for config file
            outfile = open(config_file, 'w')
        
            # Iterate over file and set size of mesh in config file
            for line in fp :
                
                line = line.strip()
                # For inside CE commented
                # Search for pattern
                matchobj = re.match(r'^k=', line)
                
                # Set size of mesh if line in file corresponds to mesh size
                
                if matchobj :
                    line = 'k=' + str(mesh_size) + ';'
        
                # Write config to file
                outfile.write(line + '\n')
        
            # Close file handles
            fp.close()
            outfile.close()
        
            # Set path to log file for upward trace files
            log_file = './logs/' + wl_name + '_chip_' + str(chip+1) + '_layer_' + str(layer_idx) + '_mesh_' + str(mesh_size) + '.log'
        
            # Copy trace file
            os.system('cp ' + trace_file_dir + '/' + file_name + ' ./trace_file.txt')
        
            # Run Booksim with config file and save log
            booksim_command = './booksim ' + config_file + ' > ' + log_file
            os.system(booksim_command)
        
            # Grep for packet latency average from log file
            #latency = os.popen('grep "Packet latency average" ' + log_file + ' | tail -1 | awk \'{print $5}\'').read().strip()
            latency = os.popen('grep "Trace is finished in" ' + log_file + ' | tail -1 | awk \'{print $5}\'').read().strip()

            if latency == '':
                latency = prev_latency
            
            if (debug_required == 1):
                print('[ INFO] Communication latency for layer ' + str(layer_idx+1) + ' is ' + str(int(float(latency))*scales[layer_idx]) + ' cycles\n')
        
            power = os.popen('grep "Total Power" ' + log_file + ' | tail -1 | awk \'{print $4}\'').read().strip()

            if (power == ''):
                power = prev_power

        
            if (debug_required == 1):
                print('[ INFO] Communication power for layer ' + str(layer_idx+1) + ' is ' + power +'\n')
        
        
            area = os.popen('grep "Total Area" ' + log_file + ' | tail -1 | awk \'{print $4}\'').read().strip()

          
            if (area == ''):
                area = prev_area


        
            energy = int(float(latency))*scales[layer_idx]*float(power)*1e-12
        
            total_area = total_area + float(area)
        
            outfile_latency = open('logs/comm_latency_' + wl_name + '_chip_' + str(chip+1) + '_mesh_' + str(mesh_size) + '_each_layer.csv', 'a')
            outfile_latency.write(str(int(float(latency))*scales[layer_idx]*1e-9) + '\n')
            outfile_latency.close()
        
            outfile_power = open('logs/comm_power_' + wl_name + '_chip_' + str(chip+1) + '_mesh_' + str(mesh_size) + '_each_layer.csv', 'a')
            outfile_power.write(str(float(power)*1e-3) + '\n')
            outfile_power.close()
        
        
            outfile_energy = open('logs/comm_energy_' + wl_name + '_chip_' + str(chip+1) + '_mesh_' + str(mesh_size) + '_each_layer.csv', 'a')
            outfile_energy.write(str(energy) + '\n')
            outfile_energy.close()

            prev_area = area
            prev_latency = latency
            prev_power = power
        
        noc_area = total_area*1e-6/(num_layers-1)
            
        if (debug_required == 1):
            print('[ INFO] NoC area: ' + str(noc_area) +'\n')
        
        
        outfile_area = open('logs/comm_area_' + wl_name + '_chip_' + str(chip+1) + '_mesh_' + str(mesh_size) + '.csv', 'a')
        outfile_area.write(str(noc_area) + '\n')
        outfile_area.close()

    
