from krittika.compute.vector.vector_os import VectorOS
from krittika.compute.vector.vector_ws import VectorWS
from krittika.compute.mat_mul.systolic_mat_mul_os import SystolicMatMulOS
from krittika.compute.mat_mul.systolic_mat_mul_ws import SystolicMatMulWS
from krittika.compute.mat_mul.systolic_mat_mul_is import SystolicMatMulIS


class ComputeNode:
    def __init__(self):
        self.selected_compute_node = SystolicMatMulOS()

        self.params_set = False

    def set_params(self, config):
        print('WIP')

