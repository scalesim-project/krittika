import math

from scalesim.compute.operand_matrix import operand_matrix

from krittika.config.krittika_config import KrittikaConfig
from krittika.schedule_manager import PartitionManager
from krittika.compute.compute_node import ComputeNode


class SingleLayerSim:
    '''
        The objective of this class is to:
        1. Read the operand matrices
        2. Get the schedule from the scheduler class object
        3. Partition the operand matrix
        4. Run the partitioned operand matrix for compute
        5. Run the generated demands from each compute element
    '''
    def __init__(self):

        # Member objects
        self.op_mat_obj = operand_matrix()
        self.partitioner_obj = PartitionManager()
        self.config_obj = KrittikaConfig()

        # Variables determining state
        self.layer_id = 0
        self.num_input_part = 0
        self.num_filter_part = 0
        self.compute_node_list = []

        # Flags
        self.params_set = False
        self.compute_done = False
        self.mem_traces_done = False

    #
    def set_params(self,
                   config_obj=KrittikaConfig(),
                   op_mat_obj=operand_matrix(),
                   partitioner_obj=PartitionManager(),
                   layer_id=0):

        self.config_obj = config_obj
        self.op_mat_obj = op_mat_obj
        self.partitioner_obj = partitioner_obj

        self.layer_id = layer_id

        self.params_set = True

    #
    def run(self):
        self.num_input_part, self.num_filter_part = self.partitioner_obj.get_layer_partitions(layer_id=self.layer_id)

        self.compute_node_list =  []

        self.run_compute_all_parts()
        self.run_mem_sim_all_parts()

    #
    def run_compute_all_parts(self):
        ifmap_matrix, filter_matrix, ofmap_matrix = self.op_mat_obj.get_all_operand_matrix()
        compute_unit, opt_dataflow = self.partitioner_obj.get_opt_compute_params(layer_id=self.layer_id)

        input_rows_per_part = math.ceil(ifmap_matrix.shape[0] / self.num_input_part)
        filter_cols_per_part = math.ceil(filter_matrix.shape[1] / self.num_filter_part)

        for inp_part in range(self.num_input_part):
            ifmap_row_start = inp_part * input_rows_per_part
            ifmap_row_end = min(ifmap_row_start + input_rows_per_part, ifmap_matrix.shape[0])

            ifmap_part = ifmap_matrix[ifmap_row_start:ifmap_row_end,:]

            for filt_part in range(self.num_filter_part):

                filt_col_start = filt_part * filter_cols_per_part
                filt_col_end = min(filt_col_start + filter_cols_per_part, filter_matrix.shape[1])

                filter_part = filter_matrix[:, filt_col_start: filt_col_end]
                ofmap_part = ofmap_matrix[ifmap_row_start: ifmap_row_end, filt_col_start:filt_col_end]

                this_part_compute_node = ComputeNode()
                this_part_compute_node.set_params(config=self.config_obj,
                                                  compute_unit=compute_unit,
                                                  dataflow=opt_dataflow)

                this_part_compute_node.set_operands(ifmap_opmat=ifmap_part,
                                                    filter_opmat=filter_part,
                                                    ofmap_opmat=ofmap_part)

                this_part_compute_node.calc_demand_matrices()

                self.compute_node_list += [this_part_compute_node]

        self.compute_done = True

    #
    def run_mem_sim_all_parts(self):
        assert self.compute_done

        print('WIP')






