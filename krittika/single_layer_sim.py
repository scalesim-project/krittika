import math
import os.path

from scalesim.compute.operand_matrix import operand_matrix
from scalesim.memory.double_buffered_scratchpad_mem import double_buffered_scratchpad

from krittika.krittika_config import KrittikaConfig
from krittika.partition_manager import PartitionManager
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
        self.all_node_mem_objects = []

        #
        self.log_top_path = './'

        # Reports: Per core
        self.total_cycles_list = []
        self.stall_cycles_list = []
        self.overall_util_list = []
        self.mapping_eff_list = []
        self.compute_util_list = []

        self.ifmap_sram_reads_list = []
        self.filter_sram_reads_list = []
        self.ofmap_sram_writes_list = []
        self.avg_ifmap_sram_bw_list = []
        self.avg_filter_sram_bw_list = []
        self.avg_ofmap_sram_bw_list = []

        self.ifmap_sram_start_cycle_list = []
        self.ifmap_sram_stop_cycle_list = []
        self.filter_sram_start_cycle_list = []
        self.filter_sram_stop_cycle_list = []
        self.ofmap_sram_start_cycle_list = []
        self.ofmap_sram_stop_cycle_list = []

        self.ifmap_dram_start_cycle_list = []
        self.ifmap_dram_stop_cycle_list = []
        self.filter_dram_start_cycle_list = []
        self.filter_dram_stop_cycle_list = []
        self.ofmap_dram_start_cycle_list = []
        self.ofmap_dram_stop_cycle_list = []

        self.ifmap_dram_reads_list = []
        self.filter_dram_reads_list = []
        self.ofmap_dram_reads_list = []

        self.avg_ifmap_dram_bw_list = []
        self.avg_filter_dram_bw_list = []
        self.avg_ofmap_dram_bw_list = []

        # Flags
        self.verbose = True
        self.params_set = False
        self.compute_done = False
        self.mem_traces_done = False
        self.report_metrics_ready = False

    #
    def set_params(self,
                   config_obj=KrittikaConfig(),
                   op_mat_obj=operand_matrix(),
                   partitioner_obj=PartitionManager(),
                   layer_id=0,
                   verbosity=True,
                   log_top_path='./'):

        self.verbose = verbosity
        self.log_top_path = log_top_path

        self.config_obj = config_obj
        self.op_mat_obj = op_mat_obj
        self.partitioner_obj = partitioner_obj

        self.layer_id = layer_id

        self.params_set = True

    #
    def run(self):
        self.num_input_part, self.num_filter_part = self.partitioner_obj.get_layer_partitions(layer_id=self.layer_id)

        self.compute_node_list = []

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

        bandwidth_mode = self.config_obj.get_bandwidth_use_mode()
        per_core_ifmap_buf_size, per_core_fitler_buf_size, per_core_ofmap_buf_size \
            = self.config_obj.get_per_unit_sram_sizes_kb() * 1024

        per_core_ifmap_bw, per_core_filter_bw, per_core_ofmap_bw\
            = self.config_obj.get_interface_bandwidths()

        for compute_node in self.compute_node_list:

            this_part_mem = double_buffered_scratchpad()
            this_part_mem.set_params(verbose=self.verbose,
                                     estimate_bandwidth_mode=bandwidth_mode,
                                     ifmap_buf_size_bytes=per_core_ifmap_buf_size,
                                     filter_buf_size_bytes=per_core_fitler_buf_size,
                                     ofmap_buf_size_bytes=per_core_ofmap_buf_size,
                                     ifmap_backing_buf_bw=per_core_ifmap_bw,
                                     filter_backing_buf_bw=per_core_filter_bw,
                                     ofmap_backing_buf_bw=per_core_ofmap_bw
                                     )

            # Demand mat
            this_node_ifmap_demand_mat, this_node_filter_demand_mat, this_node_ofmap_demand_mat \
                = compute_node.get_demand_matrices()

            this_node_ifmap_fetch_mat, this_node_filter_fetch_mat = compute_node.get_fetch_matrices()

            this_part_mem.set_read_buf_prefetch_matrices(ifmap_prefetch_mat=this_node_ifmap_fetch_mat,
                                                         filter_prefetch_mat=this_node_filter_fetch_mat
                                                         )
            this_part_mem.service_memory_requests(this_node_ifmap_demand_mat,
                                                  this_node_filter_demand_mat,
                                                  this_node_ofmap_demand_mat)

            self.all_node_mem_objects += [this_part_mem]

        self.mem_traces_done = True

    #
    def gather_report_items_across_cores(self):
        assert self.compute_done and self.mem_traces_done

        for core_id in range(len(self.compute_node_list)):
            compute_system = self.compute_node_list[core_id]
            memory_system = self.all_node_mem_objects[core_id]

            # Compute report
            num_compute = compute_system.get_num_compute()
            num_mac_unit = compute_system.get_num_mac_unit()
            total_cycles = memory_system.get_total_compute_cycles()
            stall_cycles = memory_system.get_stall_cycles()
            overall_util = (num_compute * 100) / total_cycles * num_mac_unit
            mapping_eff = compute_system.get_avg_mapping_efficiency() * 100
            compute_util = compute_system.get_avg_compute_utilization() * 100

            self.total_cycles_list += [total_cycles]
            self.stall_cycles_list += [stall_cycles]
            self.overall_util_list += [overall_util]
            self.mapping_eff_list += [mapping_eff]
            self.compute_util_list += [compute_util]

            # BW report
            ifmap_sram_reads = compute_system.get_ifmap_requests()
            filter_sram_reads = compute_system.get_filter_requests()
            ofmap_sram_writes = compute_system.get_ofmap_requests()
            avg_ifmap_sram_bw = ifmap_sram_reads / total_cycles
            avg_filter_sram_bw = filter_sram_reads / total_cycles
            avg_ofmap_sram_bw = ofmap_sram_writes / total_cycles

            self.ifmap_sram_reads_list += [ifmap_sram_reads]
            self.filter_sram_reads_list += [filter_sram_reads]
            self.ofmap_sram_writes_list += [ofmap_sram_writes]
            self.avg_ifmap_sram_bw_list += [avg_ifmap_sram_bw]
            self.avg_filter_sram_bw_list += [avg_filter_sram_bw]
            self.avg_ofmap_sram_bw_list += [avg_ofmap_sram_bw]

            # Detail report
            ifmap_sram_start_cycle, ifmap_sram_stop_cycle = memory_system.get_ifmap_sram_start_stop_cycles()
            filter_sram_start_cycle, filter_sram_stop_cycle = memory_system.get_filter_sram_start_stop_cycles()
            ofmap_sram_start_cycle, ofmap_sram_stop_cycle = memory_system.get_ofmap_sram_start_stop_cycles()

            ifmap_dram_start_cycle, ifmap_dram_stop_cycle, ifmap_dram_reads = memory_system.get_ifmap_dram_details()
            filter_dram_start_cycle, filter_dram_stop_cycle, filter_dram_reads = memory_system.get_filter_dram_details()
            ofmap_dram_start_cycle, ofmap_dram_stop_cycle, ofmap_dram_writes = memory_system.get_ofmap_dram_details()

            self.ifmap_sram_start_cycle_list += [ifmap_sram_start_cycle]
            self.ifmap_sram_stop_cycle_list += [ifmap_sram_stop_cycle]
            self.filter_sram_start_cycle_list += [filter_sram_start_cycle]
            self.filter_sram_stop_cycle_list += [filter_sram_stop_cycle]
            self.ofmap_sram_start_cycle_list += [ofmap_sram_start_cycle]
            self.ofmap_sram_stop_cycle_list += [ofmap_sram_stop_cycle]

            self.ifmap_dram_start_cycle_list += [ifmap_dram_start_cycle]
            self.ifmap_dram_stop_cycle_list += [ifmap_dram_stop_cycle]
            self.filter_dram_start_cycle_list += [filter_dram_start_cycle]
            self.filter_dram_stop_cycle_list += [filter_dram_stop_cycle]
            self.ofmap_dram_start_cycle_list += [ofmap_dram_start_cycle]
            self.ofmap_dram_stop_cycle_list += [ofmap_dram_stop_cycle]

            self.ifmap_dram_reads_list += [ifmap_dram_reads]
            self.filter_dram_reads_list += [filter_dram_reads]
            self.ofmap_dram_reads_list += [ofmap_dram_writes]

            # BW calc for DRAM access
            avg_ifmap_dram_bw = ifmap_dram_reads / (ifmap_dram_stop_cycle - ifmap_dram_start_cycle + 1)
            avg_filter_dram_bw = filter_dram_reads / (filter_dram_stop_cycle - filter_dram_start_cycle + 1)
            avg_ofmap_dram_bw = ofmap_dram_writes / (ofmap_dram_stop_cycle - ofmap_dram_start_cycle + 1)

            self.avg_ifmap_dram_bw_list += [avg_ifmap_dram_bw]
            self.avg_filter_dram_bw_list += [avg_filter_dram_bw]
            self.avg_ofmap_dram_bw_list += [avg_ofmap_dram_bw]

        self.report_metrics_ready = True

    #
    def save_traces(self):
        assert self.mem_traces_done
        self.build_trace_log_dirs()

        for part_idx in range(len(self.all_node_mem_objects)):
            trace_dir_name = self.log_top_path + \
                             '/traces/layer' + str(self.layer_id) + \
                             '/core' + str(part_idx)

            ifmap_sram_filename = trace_dir_name + '/IFMAP_SRAM_TRACE.csv'
            filter_sram_filename = trace_dir_name + '/FILTER_SRAM_TRACE.csv'
            ofmap_sram_filename = trace_dir_name + '/OFMAP_SRAM_TRACE.csv'

            ifmap_dram_filename = trace_dir_name + '/IFMAP_DRAM_TRACE.csv'
            filter_dram_filename = trace_dir_name + '/FILTER_DRAM_TRACE.csv'
            ofmap_dram_filename = trace_dir_name + '/OFMAP_DRAM_TRACE.csv'

            memory_system = self.all_node_mem_objects[part_idx]
            memory_system.print_ifmap_sram_trace(ifmap_sram_filename)
            memory_system.print_ifmap_dram_trace(ifmap_dram_filename)
            memory_system.print_filter_sram_trace(filter_sram_filename)
            memory_system.print_filter_dram_trace(filter_dram_filename)
            memory_system.print_ofmap_sram_trace(ofmap_sram_filename)
            memory_system.print_ofmap_dram_trace(ofmap_dram_filename)

#
    def build_trace_log_dirs(self):
        self.check_and_build(self.log_top_path)

        l1_dir = self.log_top_path + '/traces'
        self.check_and_build(l1_dir)

        l2_dir = l1_dir + '/layer' + str(self.layer_id)
        self.check_and_build(l2_dir)

        for core_id in range(len(self.compute_node_list)):
            this_core_dir = l2_dir + '/core' + str(core_id)
            self.check_and_build(this_core_dir)


    @staticmethod
    def check_and_build(dirname):
        if not os.path.isdir(dirname):
            cmd = 'mkdir ' + dirname
            os.system(cmd)






