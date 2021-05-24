import numpy as np

from krittika.compute.compute_node import ComputeNode


class SingleLayerComputeSim:
    def __init__(self):
        print('WIP')
        self.input1_op_mat = np.ones((1,1))
        self.input2_op_mat = np.ones((1,1))
        self.output = np.ones((1,1))

        self.num_nodes_to_use = 1
        self.node_compute_units = []    # Eg, vec, matmul, or scalar (to be added later)
        self.node_dataflows = []

        self.node_compute_objects_list = []     # List of compute nodes

        self.opmats_valid = False
        self.runs_ready = False

    def set_params(self):
        print('WIP')

    #
    def run_single_layer_distribute(self):
        # The operand matrices are partitioned here
        # For each partition:
        #
        print('WIP')

    def run_single_layer_one_part(self,
                                  node_id=0,
                                  input_op1_part=None,
                                  input_op2_part=None,
                                  output_op_part=None):
        # Get the operand matrix part
        # From the schedule chose dataflow, compute unit, and operand matrix
        # Run the generation of demand and fetch matrices
        dataflow = self.node_dataflows[node_id]
        compute_object = self.node_compute_objects_list