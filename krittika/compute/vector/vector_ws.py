import numpy as np
from scalesim.scale_config import scale_config
from scalesim.compute.systolic_compute_ws import systolic_compute_ws

# Treat this as a macro for initialization
dummy_matrix = np.ones((1, 1)) * -1


class VectorWS:
    def __init__(self):
        # Compute Unit
        self.num_units = 1
        self.compute_unit_cfg = scale_config()
        self.compute_unit = systolic_compute_ws()

        # Operand matrices
        self.vector_np = dummy_matrix
        self.matrix_np = dummy_matrix
        self.vec_out_np = dummy_matrix

        # Flags
        self.params_set = False

    #
    def set_params(self, num_units=1,
                   op_mat_vec=dummy_matrix,
                   op_mat_inmat=dummy_matrix,
                   op_mat_outvec=dummy_matrix):

        assert num_units > 0, 'Invalid number of units'
        self.num_units = num_units
        config_vec = self.compute_unit_cfg.get_default_conf_as_list()
        config_vec[1] = int(self.num_units)
        config_vec[2] = 1
        config_vec[9] = 'ws'
        self.compute_unit_cfg.update_from_list(config_vec)

        if len(op_mat_vec.shape) == 1:
            op_mat_vec = op_mat_vec.reshape((op_mat_vec.shape[0], 1))

        assert op_mat_vec.shape[0] == op_mat_inmat.shape[1], 'Inner dimensions do not match'
        assert op_mat_inmat.shape[0] == op_mat_outvec.shape[0], \
            'The outer dimensions of matrix and output should match'
        assert op_mat_outvec.shape[1] == 1, 'The output should be a vector'

        self.vector_np = op_mat_vec
        self.matrix_np = op_mat_inmat
        self.vec_out_np = op_mat_outvec

        self.compute_unit.set_params(config_obj=self.compute_unit_cfg,
                                     ifmap_op_mat=op_mat_inmat,
                                     filter_op_mat=op_mat_vec,
                                     ofmap_op_mat=op_mat_outvec)

        self.params_set = True

    #
    def create_mat_operand_demand_matrix(self):
        assert self.params_set, 'Set the parameters first'
        self.compute_unit.create_ifmap_demand_mat()

    #
    def create_vec_operand_demand_matrix(self):
        assert self.params_set, 'Set the parameters first'
        self.compute_unit.create_filter_demand_mat()

    #
    def create_out_operand_demand_matrix(self):
        assert self.params_set, 'Set the parameters first'
        self.compute_unit.create_ofmap_demand_mat()

    #
    def create_all_operand_demand_matrix(self):
        self.create_mat_operand_demand_matrix()
        self.create_vec_operand_demand_matrix()
        self.create_out_operand_demand_matrix()

    #
    def get_mat_operand_demand_matrix(self):
        return self.compute_unit.get_ifmap_demand_mat()

    #
    def get_vec_operand_demand_matrix(self):
        return self.compute_unit.get_filter_demand_mat()

    #
    def get_out_operand_demand_matrix(self):
        return self.compute_unit.get_ofmap_demand_mat()

    #
    def get_demand_matrices(self):
        inp_vec_demand_mat = self.get_vec_operand_demand_matrix()
        inp_mat_demand_mat = self.get_mat_operand_demand_matrix()
        out_vec_demand_mat = self.get_out_operand_demand_matrix()

        return inp_vec_demand_mat, inp_mat_demand_mat, out_vec_demand_mat

    #
    def get_mat_operand_fetch_matrix(self):
        assert self.params_set, 'Set the parameters first'
        return self.compute_unit.get_ifmap_prefetch_mat()

    #
    def get_vec_operand_fetch_matrix(self):
        assert self.params_set, 'Set the parameters first'
        return self.compute_unit.get_filter_prefetch_mat()

    #
    def get_fetch_matrices(self):
        inp_vec_fetch_mat = self.get_vec_operand_fetch_matrix()
        inp_mat_fetch_mat = self.get_mat_operand_fetch_matrix()

        return inp_vec_fetch_mat, inp_mat_fetch_mat

    #
    def get_avg_mapping_efficiency(self):
        assert self.params_set, 'Set the parameters first'
        return self.compute_unit.get_avg_mapping_efficiency()

    #
    def get_avg_compute_utilization(self):
        assert self.params_set, 'Set the parameters first'
        return self.compute_unit.get_avg_compute_utilization()

    #
    def get_mat_reads(self):
        assert self.params_set, 'Set the parameters first'
        return self.compute_unit.get_ifmap_requests()

    #
    def get_vec_reads(self):
        assert self.params_set, 'Set the parameters first'
        return self.compute_unit.get_filter_requests()

    #
    def get_ofmap_writes(self):
        assert self.params_set, 'Set the parameters first'
        return self.compute_unit.get_ofmap_requests()
