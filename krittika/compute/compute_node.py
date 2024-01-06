import numpy as np

from krittika.config.krittika_config import KrittikaConfig
from krittika.compute.vector.vector_os import VectorOS
from krittika.compute.vector.vector_ws import VectorWS
from krittika.compute.mat_mul.systolic_mat_mul_os import SystolicMatMulOS
from krittika.compute.mat_mul.systolic_mat_mul_ws import SystolicMatMulWS
from krittika.compute.mat_mul.systolic_mat_mul_is import SystolicMatMulIS


class ComputeNode:
    def __init__(self):
        # Valid identifiers
        self.valid_compute_units = ['matmul', 'vector']
        self.valid_dataflow = ['os', 'ws', 'is']

        # Member Objects
        self.selected_compute_node = SystolicMatMulOS()
        self.config_obj = KrittikaConfig()

        # State
        self.dataflow = 'os'
        self.compute_unit = 'matmul'

        # Operand_matrices
        self.ifmap_matrix = np.ones((1, 1))
        self.filter_matrix = np.ones((1, 1))
        self.ofmap_matrix = np.ones((1, 1))

        # Flags
        self.params_set = False
        self.operands_valid = False
        self.matrices_valid = False

    #
    def set_params(self,
                   config=KrittikaConfig(),
                   compute_unit='matmul',
                   dataflow='ws'):

        assert compute_unit in self.valid_compute_units
        assert dataflow in self.valid_dataflow

        self.config_obj = config
        self.compute_unit = compute_unit
        self.dataflow = dataflow

        if compute_unit == 'matmul':
            if dataflow == 'os':
                self.selected_compute_node = SystolicMatMulOS()

            elif dataflow == 'ws':
                self.selected_compute_node = SystolicMatMulWS()

            elif dataflow == 'is':
                self.selected_compute_node = SystolicMatMulIS()

            arr_row, arr_col = self.config_obj.get_matmul_dims()
            bw_mode = self.config_obj.get_bandwidth_use_mode()
            bandwidth = self.config_obj.get_interface_bandwidths()[0]
            self.selected_compute_node.set_params(bw_mode = bw_mode, bandwidth = bandwidth, arr_row=arr_row, arr_col=arr_col)

            if self.operands_valid:
                self.selected_compute_node.set_operands(
                    op_outmat=self.ofmap_matrix,
                    op_inmat1=self.ifmap_matrix,
                    op_inmat2=self.filter_matrix
                )

        elif compute_unit == 'vector':
            if dataflow == 'os':
                self.selected_compute_node = VectorOS()
                if self.operands_valid:
                    self.selected_compute_node.set_operands(
                        op_outmat=self.ofmap_matrix,
                        op_inmat1=self.ifmap_matrix,
                        op_inmat2=self.filter_matrix
                    )


            elif dataflow == 'ws':
                self.selected_compute_node = VectorWS()
                if self.operands_valid:
                    self.selected_compute_node.set_operands(
                        op_outmat=self.ofmap_matrix,
                        op_inmat1=self.ifmap_matrix,
                        op_inmat2=self.filter_matrix
                    )

            elif dataflow == 'is':
                self.selected_compute_node = VectorWS()
                if self.operands_valid:
                    self.selected_compute_node.set_operands(
                        op_outmat=self.ofmap_matrix,
                        op_inmat1=self.filter_matrix,
                        op_inmat2=self.ifmap_matrix
                    )

            num_vec_units = self.config_obj.get_vector_dim()
            self.selected_compute_node.set_params(num_vec_units)

        self.params_set = True

    #
    def set_operands(self,
                     ifmap_opmat=np.ones((1,1)),
                     filter_opmat=np.ones((1,1)),
                     ofmap_opmat=np.ones((1,1))
                     ):

        self.ifmap_matrix = ifmap_opmat
        self.filter_matrix = filter_opmat
        self.ofmap_matrix = ofmap_opmat

        self.operands_valid = True

        if self.params_set:
            if self.dataflow == 'is' and self.compute_unit == 'vector':
                self.selected_compute_node.set_operands(
                    op_outmat=self.ofmap_matrix,
                    op_inmat1=self.filter_matrix,
                    op_inmat2=self.ifmap_matrix
                )
            else:
                self.selected_compute_node.set_operands(
                    op_outmat=self.ofmap_matrix,
                    op_inmat1=self.ifmap_matrix,
                    op_inmat2=self.filter_matrix
                )

    #
    def calc_demand_matrices(self):
        assert self.params_set and self.operands_valid
        self.selected_compute_node.create_all_operand_demand_matrix()

        self.matrices_valid = True

    #
    def get_demand_matrices(self):
        if not self.matrices_valid:
            self.calc_demand_matrices()

        return self.selected_compute_node.get_demand_matrices()

    #
    def get_prefetch_matrices(self):
        if not self.matrices_valid:
            self.calc_demand_matrices()

        return self.selected_compute_node.get_fetch_matrices()

    #
    def get_num_compute(self):
        assert self.operands_valid

        num_compute = self.ifmap_matrix.shape[0] * self.ifmap_matrix.shape[1] * self.filter_matrix.shape[1]
        return num_compute

    #
    def get_num_mac_units(self):
        assert self.params_set

        return self.selected_compute_node.get_num_mac()
    
    #
    def get_avg_mapping_efficiency(self):
        assert self.operands_valid

        return self.selected_compute_node.get_avg_mapping_efficiency()

    #
    def get_avg_compute_utilization(self):
        assert self.operands_valid

        return self.selected_compute_node.get_avg_compute_utilization()
    
    #
    def get_ifmap_requests(self):
        assert self.operands_valid

        return self.selected_compute_node.get_mat1_reads()

    #
    def get_filter_requests(self):
        assert self.operands_valid

        return self.selected_compute_node.get_mat2_reads()
    
    #
    def get_ofmap_requests(self):
        assert self.operands_valid

        return self.selected_compute_node.get_outmat_writes()




