# GCN_accelerator_in-memory
A simulation framework for in-memory computing (IMC)-based GCN accelerator


Performance evaluation of the communication

Code structure:

noc_simulation.py

    		|
  
 		|-> generate_trace_files (generate trace_files for inter-CE communication)
  
 		|
  
 		|-> run_simulations (simulation for inter-CE communication)
  
 		|		|
  
		|		|-> noc_simulation_edge_based (execute booksim)
  
		|
  
		|-> generate trace_files_inside_ce (generate trace_files for inter-CE communication)
  
		|
  
  		|-> run_simulations (simulation for intra-CE communication)
  
  		|		|
  
		|		|-> noc_simulation_edge_based (execute booksim)
  
  
  
  Input file:
  
  1. Connection patterns must be in workloads/ directory.
  2. Filename format is <dataset_name>.csv
  3. The file contains multiple rows. The first column of each row denotes a GCN node. The subsequent columns denote the nodes it is connected with.
     
     
  Input parameters:
  
  wl_name = <dataset_name>
  
  mesh_size_array = [<n>]
	
  quantization_bit = <q>
	
  num_chips = <c> (to be decided based on on-chip resources)
	
  num_inside_routers = 30 (incorporated in [1])
	
  scales = [x,y] (Used to accelerate simulation. Higher will accelerate more but degrade the estimation accuracy.)
	
  Note: add new workload if it is not existing. Corresponding num_gnn_nodes, num_features_each_layer needs to be added
	
  
     
     
  Outpute file structure:
  
  booksim_<dataset_name>
    |
    |-> logs_mesh_size_<n>_bit_<q>_<dataset_name>_chip_<c> (inter-CE communication performance)
    |
    |       |-> comm_area* (inter-CE NoC area in mm^2)
    |       |-> comm_energy* (inter-CE NoC energy per layer in J)
    |       |-> comm_latency* (inter-CE NoC latency per layer in ns assuming 1 GHz clock frequency)
    |
    |-> logs_mesh_size_<n>_bit_<q>_<dataset_name>_high_chip_<c> (intra-CE communication performance with CE having highest connections)
    |
    |       |-> same as above
    |
    |-> logs_mesh_size_<n>_bit_<q>_<dataset_name>_low_chip_<c> (intra-CE communication performance with CE having highest connections)
    |
    |       |-> same as above  
  
  Output data:
  
  1. Inter-CE communication performance are considered as it is.
	
  2. Intra-CE communication performance for each CE are obtained by averaging *_high and *_low performance. To get the total Intra-CE communication performance, energy and area needs to multiplied by num_inside_routers (30 in this case).
	
  3. Finally, Inter-CE and Intra-CE performance need to be added to obtain total communication performance.
  

Performance evaluation of the communication
Coming Soon.

  
If you are using the simulator, please cite the following publication:
	
[1] S. K. Mandal, G. Krishnan, A. Alper Goksoy, G. R. Nair, Y. Cao and U. Y. Ogras, "COIN: Communication-Aware In-Memory Acceleration for Graph Convolutional Networks," in IEEE Journal on Emerging and Selected Topics in Circuits and Systems, doi: 10.1109/JETCAS.2022.3169899.
