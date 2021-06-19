import numpy as np
from scalesim.scale_config import scale_config
from scalesim.compute.systolic_compute_is import systolic_compute_is

# Treat this as a macro for initialization
dummy_matrix = np.ones((1, 1)) * -1


class SystolicMatMulIS:
    def __init__(self):
        # Compute Unit
        self.arr_row = 1
        self.arr_col = 1
        self.compute_unit_cfg = scale_config()
        self.compute_unit = systolic_compute_is()

        # Operand matrices
        self.inmat1_np = dummy_matrix
        self.inmat2_np = dummy_matrix
        self.outmat_np = dummy_matrix

        # Flags
        self.params_set = False
        self.operands_valid = False

    #
    def set_params(self,
                   arr_row=1, arr_col=1):

        assert arr_row > 0 and arr_col > 0, 'Invalid array dimensions'
        self.arr_row = arr_row
        self.arr_col = arr_col

        config_vec = self.compute_unit_cfg.get_default_conf_as_list()
        config_vec[1] = int(self.arr_row)
        config_vec[2] = int(self.arr_col)
        config_vec[9] = 'is'
        self.compute_unit_cfg.update_from_list(config_vec)

        self.params_set = True

    #
    def set_operands(self,
                     op_inmat1=dummy_matrix,
                     op_inmat2=dummy_matrix,
                     op_outmat=dummy_matrix):

        assert self.params_set, 'Params are not set'

        self.reset_compute_unit()

        assert op_inmat2.shape[0] == op_inmat1.shape[1], 'Inner dimensions do not match'
        assert (op_inmat1.shape[0] == op_outmat.shape[0]) and (op_inmat2.shape[1] == op_outmat.shape[1]), \
            'The outer dimensions of matrix and output should match'

        self.inmat1_np = op_inmat1
        self.inmat2_np = op_inmat2
        self.outmat_np = op_outmat

        self.compute_unit.set_params(config_obj=self.compute_unit_cfg,
                                     ifmap_op_mat=op_inmat1,
                                     filter_op_mat=op_inmat2,
                                     ofmap_op_mat=op_outmat)

        self.operands_valid = True

    #
    def reset_compute_unit(self):
        self.compute_unit = systolic_compute_is()

        self.inmat1_np = dummy_matrix
        self.inmat2_np = dummy_matrix
        self.outmat_np = dummy_matrix

    #
    def create_input_operand_demand_matrices(self):
        assert self.operands_valid, 'Set the operands first'

        self.compute_unit.create_ifmap_demand_mat()
        self.compute_unit.create_filter_demand_mat()

    #
    def create_out_operand_demand_matrix(self):
        assert self.operands_valid, 'Set the operands first'
        self.compute_unit.create_ofmap_demand_mat()

    #
    def create_all_operand_demand_matrix(self):
        self.create_input_operand_demand_matrices()
        self.create_out_operand_demand_matrix()

    #
    def get_mat1_operand_demand_matrix(self):
        return self.compute_unit.get_ifmap_demand_mat()

    #
    def get_mat2_operand_demand_matrix(self):
        return self.compute_unit.get_ifmap_demand_mat()

    #
    def get_out_operand_demand_matrix(self):
        return self.compute_unit.get_ofmap_demand_mat()

    #
    def get_demand_matrices(self):
        inp_mat1_demand_mat = self.get_mat1_operand_demand_matrix()
        inp_mat2_demand_mat = self.get_mat2_operand_demand_matrix()
        out_vec_demand_mat = self.get_out_operand_demand_matrix()

        return inp_mat1_demand_mat, inp_mat2_demand_mat, out_vec_demand_mat

    #
    def get_mat1_operand_fetch_matrix(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_ifmap_prefetch_mat()

    #
    def get_mat2_operand_fetch_matrix(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_ifmap_prefetch_mat()

    #
    def get_fetch_matrices(self):
        inp1_mat_fetch_mat = self.get_mat1_operand_fetch_matrix()
        inp2_mat_fetch_mat = self.get_mat2_operand_fetch_matrix()

        return inp1_mat_fetch_mat, inp2_mat_fetch_mat

    #
    def get_avg_mapping_efficiency(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_avg_mapping_efficiency()

    #
    def get_avg_compute_utilization(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_avg_compute_utilization()

    #
    def get_mat1_reads(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_ifmap_requests()

    #
    def get_mat2_reads(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_filter_requests()

    #
    def get_outmat_writes(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_unit.get_ofmap_requests()

    #
    def get_num_mac(self):
        assert self.params_set
        return self.arr_row * self.arr_col
