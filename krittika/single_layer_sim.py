from scalesim.scale_config import scale_config
from scalesim.topology_utils import topologies
from scalesim.compute.operand_matrix import operand_matrix
from krittika.compute.scaled_out_compute_unit import ScaledOutComputeUnit


class SingleLayerSim:
    def __init__(self):
        self.compute_unit_obj = ScaledOutComputeUnit()
        self.memory_unit_obj = MemoryUnit()
        self.operand_matrix_obj = operand_matrix()

        self.topo_obj = topologies()
        self.layer_id = 1

        self.inmat1_prefetches_per_part = []
        self.inmat2_prefetches_per_part = []

        self.inmat1_demands_per_part = []
        self.inmat2_demands_per_part = []
        self.outmat_demands_per_part = []

    #
    def set_params(self, layer_id, topo_obj, compute_unit, memory_unit):

        self.layer_id = layer_id
        self.topo_obj = topo_obj

        opmat_config = scale_config()
        opmat_config.force_valid()
        self.operand_matrix_obj.set_params(topoutil_obj=self.topo_obj, layer_id=layer_id, config_obj=opmat_config)

        self.compute_unit_obj = compute_unit
        self.memory_unit_obj = memory_unit

    #
    def run(self):

        input_mat1, input_mat2, output_mat = self.operand_matrix_obj.get_all_operand_matrix()
        self.compute_unit_obj.update_operand_matrices(input_mat1, input_mat2, output_mat)
        pf1, pf2 = self.compute_unit_obj.get_prefetch_matrices()
        d1, d2, d3 = self.compute_unit_obj.get_demand_matrices()

        self.inmat1_prefetches_per_part = pf1
        self.inmat2_prefetches_per_part = pf2

        self.memory_unit_obj.update_prefetch_mat_scaled_out(inmat1_prefetches_scaled_out=pf1,
                                                            inmat2_prefetchs_scaled_out=pf2)

        self.inmat1_demands_per_part = d1
        self.inmat2_demands_per_part = d2
        self.outmat_demands_per_part = d3

        self.memory_unit_obj.service_requests_scaled_out(inmat1_requests_scaled_out=d1,
                                                         inmat2_requests_scaled_out=d2,
                                                         outmat_requests_scaled_out=d3)