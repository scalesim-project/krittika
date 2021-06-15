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
        self.op_inmat2 = dummy_matrix
        self.op_inmat1 = dummy_matrix
        self.op_outmat = dummy_matrix

        # Flags
        self.params_set = False
        self.operands_valid = False

    #
    def set_params(self, num_units=1):

        assert num_units > 0, 'Invalid number of units'
        self.num_units = num_units
        config_vec = self.compute_unit_cfg.get_default_conf_as_list()
        config_vec[1] = int(self.num_units)
        config_vec[2] = 1
        config_vec[9] = 'ws'
        self.compute_unit_cfg.update_from_list(config_vec)

        self.params_set = True

    #
    def set_operands(self,
                     op_inmat2=dummy_matrix,
                     op_inmat1=dummy_matrix,
                     op_outmat=dummy_matrix):

        assert self.params_set, 'Params are not set'

        self.reset_compute_unit()

        assert op_inmat2.shape[0] == op_inmat1.shape[1], 'Inner dimensions do not match'
        assert op_inmat1.shape[0] == op_outmat.shape[0], \
            'The outer dimensions of matrix and output should match'

        self.op_inmat2 = op_inmat2
        self.op_inmat1 = op_inmat1
        self.op_outmat = op_outmat

        self.compute_unit.set_params(config_obj=self.compute_unit_cfg,
                                     ifmap_op_mat=self.op_inmat1,
                                     filter_op_mat=self.op_inmat2,
                                     ofmap_op_mat=self.op_outmat)

        self.operands_valid = True

    #
    def reset_compute_unit(self):
        self.compute_unit = systolic_compute_ws()

        self.op_inmat2 = dummy_matrix
        self.op_inmat1 = dummy_matrix
        self.op_outmat = dummy_matrix

        self.operands_valid = False

    #
    def create_mat_operand_demand_matrix(self):
        assert self.operands_valid, 'Set the operands first'
        self.compute_unit.create_ifmap_demand_mat()

    #
    def create_vec_operand_demand_matrix(self):
        assert self.operands_valid, 'Set the operands first'
        self.compute_unit.create_filter_demand_mat()

    #
    def create_out_operand_demand_matrix(self):
        assert self.operands_valid, 'Set the operands first'
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
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_ifmap_prefetch_mat()

    #
    def get_vec_operand_fetch_matrix(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_filter_prefetch_mat()

    #
    def get_fetch_matrices(self):
        inp_vec_fetch_mat = self.get_vec_operand_fetch_matrix()
        inp_mat_fetch_mat = self.get_mat_operand_fetch_matrix()

        return inp_vec_fetch_mat, inp_mat_fetch_mat

    #
    def get_avg_mapping_efficiency(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_avg_mapping_efficiency()

    #
    def get_avg_compute_utilization(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_avg_compute_utilization()

    #
    def get_mat_reads(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_ifmap_requests()

    #
    def get_vec_reads(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_filter_requests()

    #
    def get_outmat_writes(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_ofmap_requests()
