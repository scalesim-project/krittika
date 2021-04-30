import numpy as np

from krittika.compute.compute_node import ComputeNode


class ScaledOutComputeUnit:
    def __init__(self):
        self.num_compute_nodes = 1
        self.compute_node_obj_list = []

        self.grid_rows = 1
        self.grid_cols = 1
        self.layout_mat = np.ones((1,1)) * -1

        self.compute_node_op = 'vector'
        self.compute_node_df = 'os'

        self.params_set = False

    #
    def set_params(self, total_nodes=1,
                   grid_rows=1, grid_cols=1,
                   compute_node_op='vector', compute_node_df='os'):
        self.num_compute_nodes = total_nodes

        self.grid_rows = grid_rows
        self.grid_cols = grid_cols

        self.compute_node_op = compute_node_op
        self.compute_node_df = compute_node_df

        self.params_set = True

        self.create_compute_node_obj_list()
        self.update_layout_mat()

    #
    def create_compute_node_obj_list(self):
        assert self.params_set

        for _ in range(self.num_compute_nodes):
            new_compute_node = ComputeNode()

