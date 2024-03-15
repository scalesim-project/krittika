import numpy as np
import math
from krittika.config.krittika_config import KrittikaConfig


# Treat this as a macro for initialization
dummy_matrix = np.ones((1, 1)) * -1


class simd:
    def __init__(self):
        # Compute Unit
        self.simd_length = 1
        self.config_obj = KrittikaConfig()
        self.topology_obj = None
        self.simd_op = "RELU"
        self.avg_mapping_efficiency = 0


        # Operand matrix
        self.op_matrix = dummy_matrix

        # Flags
        self.params_set = False
        self.operands_valid = False

    #
    def set_params(self, num_units=1, simd_op = "RELU"):

        assert num_units > 0, 'Invalid number of units'
        self.simd_length = num_units
        self.simd_op = simd_op

        self.params_set = True

    #
    def set_operands(self, op_matrix=dummy_matrix):

        assert self.params_set, 'Params are not set'

        assert op_matrix.shape[0] > 0, 'Input vector cannot be None'

        self.op_matrix = op_matrix
        self.operands_valid = True
    
    #
    def calc_simd_unit(self):
        assert self.operands_valid, 'Set the operands first'
        op_matrix_size = self.op_matrix.shape[0] * self.op_matrix.shape[1]

        cycles_per_op = 1
        if self.simd_op == "RELU":
            cycles_per_op = 5

        self.avg_mapping_efficiency = ((op_matrix_size // self.simd_length) * self.simd_length + op_matrix_size \
                                       % self.simd_length) / (math.ceil(op_matrix_size / self.simd_length) * self.simd_length)
        self.compute_cycles = math.ceil(op_matrix_size / self.simd_length) * cycles_per_op
        
    #
    def get_avg_mapping_efficiency(self):
        assert self.operands_valid, 'Set the operands first'
        return self.avg_mapping_efficiency

    #
    def get_avg_compute_utilization(self):
        assert self.operands_valid, 'Set the operands first'
        return self.avg_mapping_efficiency

    
    def get_compute_cycles(self):
        assert self.operands_valid, 'Set the operands first'
        return self.compute_cycles