import numpy as np
from scalesim.compute.systolic_compute_os import systolic_compute_os


class VectorOS:
    def __init__(self):
        # Compute Unit
        self.num_units = 1
        self.compute_unit = systolic_compute_os()

        # Operand matrices
        self.vector_np = np.ones((1,1)) * -1
        self.matrix_np = np.ones((1,1)) * -1
        self.vector_out_np = np.ones((1,1)) * -1

        # Flags
        self.params_set = False
        self.operands_ready = False