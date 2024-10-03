import os
import statistics
import logging

from krittika.workload_manager import WorkloadManager
from scalesim.scale_config import scale_config
from scalesim.compute.operand_matrix import operand_matrix
from krittika.config.krittika_config import KrittikaConfig
from krittika.partition_manager import PartitionManager
from krittika.single_layer_sim import SingleLayerSim


class Simulator:
    def __init__(self):
        # Objects
        self.config_obj = KrittikaConfig()
        self.partition_obj = PartitionManager()
        self.workload_obj = WorkloadManager()

        # State
        self.verbose = True
        self.trace_gen_flag = True
        self.autopartition = False
        self.single_layer_objects_list = []
        self.top_path=None

        # REPORT Structures
        self.total_cycles_report_grid = []
        self.stall_cycles_report_grid = []
        self.overall_utils_report_grid = []
        self.mapping_eff_report_grid = []
        self.cycles_report_avg_items = []
        self.cycles_report_ready = False        
        self.bandwidth_report_avg_items = []
        self.bandwidth_report_ready = False
        self.detailed_report_avg_items = []
        self.detailed_report_ready = False
        
        # Flags
        self.params_valid = False
        self.runs_done = False
        self.reports_dir_ready = False

    def set_params(self,
                   config_filename='',
                   workload_filename='',
                   custom_partition_filename='',
                   reports_dir_path='./',
                   verbose=True,
                   save_traces=True
                   ):
        # Read the user input and files and prepare the objects
        self.config_obj.read_config_from_file(filename=config_filename)

        self.workload_obj = WorkloadManager()
        self.workload_obj.read_topologies(workload_filename=workload_filename)
        
        # print(self.workload_obj.get_simd_operation(0))

        self.partition_obj.set_params(config_obj=self.config_obj,
                                      workload_obj=self.workload_obj
                                      )
        self.autopartition = self.config_obj.is_autopartition()
        if self.autopartition:
            self.partition_obj.create_partition_table()
        else:
            self.partition_obj.read_user_partition_table(filename=custom_partition_filename)

        self.verbose = verbose
        self.trace_gen_flag = save_traces

        # Check whether user input path is valid.
        # If so, use this path to save the reports. Otherwise, use the current working directory.
        full_top_path = os.path.join(os.getcwd(), reports_dir_path)
        full_top_path = os.path.join(full_top_path, '')
        if (os.path.exists(full_top_path)):
            self.top_path = full_top_path
        else:
            logging.warning('Invalid output path, please check your input. Falling back to current working directory.')
            self.top_path = './'

        self.params_valid = True

    #
    def run(self):
        # Orchestrate among the function calls to run simulations
        assert self.params_valid, 'Cannot run simulation without inputs'

        # Run compute simulations for all layers first
        num_layers = self.workload_obj.get_num_layers()

        # Update the offsets to generate operand matrices
        single_arr_config = scale_config()
        conf_list = scale_config.get_default_conf_as_list()
        user_offsets = self.config_obj.get_operand_offsets()
        conf_list[6] = user_offsets[0]
        conf_list[7] = user_offsets[1]
        conf_list[8] = user_offsets[2]
        conf_list[10] = self.config_obj.get_bandwidth_use_mode()
        conf_list.append(self.config_obj.get_interface_bandwidths()[0])
        single_arr_config.update_from_list(conf_list=conf_list)

        for layer_id in range(num_layers):
            if self.verbose:
                print('Running Layer ' + str(layer_id))
            this_layer_op_mat_obj = operand_matrix()
            layer_params = self.workload_obj.get_layer_params(layer_id)
            if (layer_params[0] in ['conv', 'gemm']):
                this_layer_op_mat_obj.set_params(config_obj=single_arr_config,
                                             topoutil_obj=self.workload_obj,
                                             layer_id=layer_id)
                this_layer_op_mat_obj.create_operand_matrices()

                this_layer_sim = SingleLayerSim()
                this_layer_sim.set_params(config_obj=self.config_obj,
                                      op_mat_obj=this_layer_op_mat_obj,
                                      partitioner_obj=self.partition_obj,
                                      layer_id=layer_id,
                                      log_top_path=self.top_path,
                                      verbosity=self.verbose)
                this_layer_sim.run()
                self.single_layer_objects_list += [this_layer_sim]

                if self.verbose:
                    print('SAVING TRACES')
                this_layer_sim.save_traces()
                this_layer_sim.gather_report_items_across_cores()
            elif (layer_params[0] in ['activation']):
                op_matrix = self.single_layer_objects_list[layer_id-1].get_ofmap_operand_matrix()

                this_layer_sim = SingleLayerSim()
                this_layer_sim.set_params(config_obj=self.config_obj,
                                      op_mat_obj=this_layer_op_mat_obj,
                                      partitioner_obj=self.partition_obj,
                                      layer_id=layer_id,
                                      log_top_path=self.top_path,
                                      verbosity=self.verbose)
                this_layer_sim.run_simd_all_parts(operand_matrix=op_matrix, optype = layer_params[1])
                self.single_layer_objects_list += [this_layer_sim]
                
                this_layer_sim.gather_simd_report_items_across_cores()


            

        self.runs_done = True
        self.generate_all_reports()

    def generate_all_reports(self):
        self.create_cycles_report_structures()
        self.create_bandwidth_report_structures()
        self.create_detailed_report_structures()
        self.save_all_cycle_reports()
        self.save_all_bw_reports()
        self.save_all_detailed_reports()


    # Report generation
    def create_cycles_report_structures(self):
        assert self.runs_done

        for lid in range(self.workload_obj.get_num_layers()):
            layer_params = self.workload_obj.get_layer_params(lid)
            if (layer_params[0] in ['conv', 'gemm', 'activation']):
                this_layer_sim_obj = self.single_layer_objects_list[lid]
                total_cycles_list = this_layer_sim_obj.total_cycles_list
                stall_cycles_list = this_layer_sim_obj.stall_cycles_list
                overall_util_list = this_layer_sim_obj.overall_util_list
                mapping_eff_list = this_layer_sim_obj.mapping_eff_list
                compute_util_list = this_layer_sim_obj.compute_util_list
                self.cycles_report_avg_items += [statistics.mean(total_cycles_list)]
                self.cycles_report_avg_items += [statistics.mean(stall_cycles_list)]
                self.cycles_report_avg_items += [statistics.mean(overall_util_list)]
                self.cycles_report_avg_items += [statistics.mean(mapping_eff_list)]
                self.cycles_report_avg_items += [statistics.mean(compute_util_list)]

        self.cycles_report_ready = True


    def create_bandwidth_report_structures(self):
        assert self.runs_done

        for lid in range(self.workload_obj.get_num_layers()):
            layer_params = self.workload_obj.get_layer_params(lid)
            if (layer_params[0] in ['conv', 'gemm']):
                this_layer_sim_obj = self.single_layer_objects_list[lid]
                avg_ifmap_sram_bw_list = this_layer_sim_obj.avg_ifmap_sram_bw_list
                avg_ifmap_dram_bw_list = this_layer_sim_obj.avg_ifmap_dram_bw_list
                avg_filter_sram_bw_list = this_layer_sim_obj.avg_filter_sram_bw_list
                avg_filter_dram_bw_list = this_layer_sim_obj.avg_filter_dram_bw_list
                avg_ofmap_sram_bw_list = this_layer_sim_obj.avg_ofmap_sram_bw_list
                avg_ofmap_dram_bw_list = this_layer_sim_obj.avg_ofmap_dram_bw_list
            
                self.bandwidth_report_avg_items += [statistics.mean(avg_ifmap_sram_bw_list)]
                self.bandwidth_report_avg_items += [statistics.mean(avg_filter_sram_bw_list)]
                self.bandwidth_report_avg_items += [statistics.mean(avg_ofmap_sram_bw_list)]
                self.bandwidth_report_avg_items += [statistics.mean(avg_ifmap_dram_bw_list)]
                self.bandwidth_report_avg_items += [statistics.mean(avg_filter_dram_bw_list)]
                self.bandwidth_report_avg_items += [statistics.mean(avg_ofmap_dram_bw_list)]

        self.bandwidth_report_ready = True



    def create_detailed_report_structures(self):
        assert self.runs_done

        for lid in range(self.workload_obj.get_num_layers()):
            layer_params = self.workload_obj.get_layer_params(lid)
            if (layer_params[0] in ['conv', 'gemm']):
                this_layer_sim_obj = self.single_layer_objects_list[lid]
                ifmap_sram_start_cycle_list = this_layer_sim_obj.ifmap_sram_start_cycle_list
                ifmap_sram_stop_cycle_list = this_layer_sim_obj.ifmap_sram_stop_cycle_list
                ifmap_sram_reads_list = this_layer_sim_obj.ifmap_sram_reads_list
                filter_sram_start_cycle_list = this_layer_sim_obj.filter_sram_start_cycle_list
                filter_sram_stop_cycle_list = this_layer_sim_obj.filter_sram_stop_cycle_list
                filter_sram_reads_list = this_layer_sim_obj.filter_sram_reads_list
                ofmap_sram_start_cycle_list = this_layer_sim_obj.ofmap_sram_start_cycle_list
                ofmap_sram_stop_cycle_list = this_layer_sim_obj.ofmap_sram_stop_cycle_list
                ofmap_sram_writes_list = this_layer_sim_obj.ofmap_sram_writes_list

                ifmap_dram_start_cycle_list = this_layer_sim_obj.ifmap_dram_start_cycle_list
                ifmap_dram_stop_cycle_list = this_layer_sim_obj.ifmap_dram_stop_cycle_list
                ifmap_dram_reads_list = this_layer_sim_obj.ifmap_dram_reads_list
                filter_dram_start_cycle_list = this_layer_sim_obj.filter_dram_start_cycle_list
                filter_dram_stop_cycle_list = this_layer_sim_obj.filter_dram_stop_cycle_list
                filter_dram_reads_list = this_layer_sim_obj.filter_dram_reads_list
                ofmap_dram_start_cycle_list = this_layer_sim_obj.ofmap_dram_start_cycle_list
                ofmap_dram_stop_cycle_list = this_layer_sim_obj.ofmap_dram_stop_cycle_list
                ofmap_dram_writes_list = this_layer_sim_obj.ofmap_dram_writes_list

                self.detailed_report_avg_items += [statistics.mean(ifmap_sram_start_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(ifmap_sram_stop_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(ifmap_sram_reads_list)]
                self.detailed_report_avg_items += [statistics.mean(filter_sram_start_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(filter_sram_stop_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(filter_sram_reads_list)]
                self.detailed_report_avg_items += [statistics.mean(ofmap_sram_start_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(ofmap_sram_stop_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(ofmap_sram_writes_list)]

                self.detailed_report_avg_items += [statistics.mean(ifmap_dram_start_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(ifmap_dram_stop_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(ifmap_dram_reads_list)]
                self.detailed_report_avg_items += [statistics.mean(filter_dram_start_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(filter_dram_stop_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(filter_dram_reads_list)]
                self.detailed_report_avg_items += [statistics.mean(ofmap_dram_start_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(ofmap_dram_stop_cycle_list)]
                self.detailed_report_avg_items += [statistics.mean(ofmap_dram_writes_list)]

           
        self.detailed_report_ready = True

    def save_all_cycle_reports(self):
        assert self.cycles_report_ready
        compute_report_name = self.top_path + 'traces' + '/COMPUTE_REPORT.csv'
        compute_report = open(compute_report_name, 'w+')
        header = 'LayerID, Total Cycles, Stall Cycles, Overall Util %, Mapping Efficiency %, Compute Util %,\n'
        columns = header.count(',') - 1
        compute_report.write(header)

        for lid in range(self.workload_obj.get_num_layers()):
            layer_params = self.workload_obj.get_layer_params(lid)
            if (layer_params[0] in ['conv', 'gemm', 'activation']):
                log = str(lid) +', '
                log += ', '.join([str(x) for x in self.cycles_report_avg_items[lid * columns:lid * columns + 5]])
                log += ',\n'
                compute_report.write(log)

        compute_report.close()


    def save_all_bw_reports(self):
        assert self.bandwidth_report_ready

        bandwidth_report_name = self.top_path + 'traces' + '/BANDWIDTH_REPORT.csv'
        bandwidth_report = open(bandwidth_report_name, 'w+')
        header = 'LayerID, Avg IFMAP SRAM BW, Avg FILTER SRAM BW, Avg OFMAP SRAM BW, '
        header += 'Avg IFMAP DRAM BW, Avg FILTER DRAM BW, Avg OFMAP DRAM BW,\n'
        columns = header.count(',') - 1

        bandwidth_report.write(header)

        for lid in range(self.workload_obj.get_num_layers()):
            layer_params = self.workload_obj.get_layer_params(lid)
            if (layer_params[0] in ['conv', 'gemm']):
                log = str(lid) +', '
                log += ', '.join([str(x) for x in self.bandwidth_report_avg_items[lid * columns:lid * columns + columns]])
                log += ',\n'
                bandwidth_report.write(log)
        
        bandwidth_report.close()



    def save_all_detailed_reports(self):
        assert self.detailed_report_ready

        detailed_report_name = self.top_path + 'traces' + '/DETAILED_ACCESS_REPORT.csv'
        detailed_report = open(detailed_report_name, 'w+')
        header = 'LayerID, '
        header += 'SRAM IFMAP Start Cycle, SRAM IFMAP Stop Cycle, SRAM IFMAP Reads, '
        header += 'SRAM Filter Start Cycle, SRAM Filter Stop Cycle, SRAM Filter Reads, '
        header += 'SRAM OFMAP Start Cycle, SRAM OFMAP Stop Cycle, SRAM OFMAP Writes, '
        header += 'DRAM IFMAP Start Cycle, DRAM IFMAP Stop Cycle, DRAM IFMAP Reads, '
        header += 'DRAM Filter Start Cycle, DRAM Filter Stop Cycle, DRAM Filter Reads, '
        header += 'DRAM OFMAP Start Cycle, DRAM OFMAP Stop Cycle, DRAM OFMAP Writes,\n'
        columns = header.count(',') - 1

        detailed_report.write(header)

        for lid in range(self.workload_obj.get_num_layers()):
            layer_params = self.workload_obj.get_layer_params(lid)
            if (layer_params[0] in ['conv', 'gemm']):
                log = str(lid) +', '
                log += ', '.join([str(x) for x in self.detailed_report_avg_items[lid * columns:lid * columns + columns]])
                log += ',\n'
                detailed_report.write(log)
        
        detailed_report.close()



