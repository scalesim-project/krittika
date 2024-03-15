# Krittika (Pleiades)
Distibuted ML Accelerator simulator

Plans to support
1. Distributed execution of DNN layers
2. Heterogenous cores
3. Multitenant execution

## *Installing the package*
Getting started is simple! Krittika is completely written in python and uses scalesim-v2 in backend.

You can clone the SCALE-Sim(v2) repository using the following command (ssh)

```$ git clone git@github.com:scalesim-project/scale-sim-v2.git```

Alternative, you can also clone using https 

```$ git clone https://github.com/scalesim-project/scale-sim-v2.git```

If you are running for the first time and do not have all the dependencies installed, please install them first using the following command

```$ pip3 install -r <path_to_scale_sim_repot>/requirements.txt```

After cloning, install scalesim from path using the following command. This version will automatically reflect any code changes that you make.

```$ pip3 install -e <path_to_scale_sim_repo_root>```

## *Launching a run*
Krittika can be run by using the krittika-sim.py script from the repository and providing the paths to the architecture configuration file (refer configs/krittika.cfg for example) and the topology descriptor csv file (refer scalesim repo for examples).

```$ python3 krittika-sim.py -c <path_to_config_file> -t <path_to_topology_file>```

Additional optional parameters
1. -p <path_to_partition_file> (Refer partition_manager.py for more info)
2. -o <path_to_the_log_dump_directory> 
3. --verbose <True/False> (Flag to change the verbosity of the run)
4. --savetrace <True/False> (Flag to indicate if the traces should be saved)

## *Topology file*
The topology file is a *CSV* file which decribes the layers of the workload topology. The layers are typically described as convolution/GEMM/activation layer parameters as shown in the example below

![topology file](https://github.com/scalesim-project/krittika/blob/main/documentation/resources/topology%20file.png "topology file")

Conv and GEMM layers follow scalesim topology structure [link](https://scale-sim-project.readthedocs.io/en/latest/topology.html)

The only difference is that there is *no comma* at the end of each layer.

Support for RELU activation is also added and can be used just as shown in the image.
