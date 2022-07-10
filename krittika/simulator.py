import os
import statistics

from scalesim.topology_utils import topologies
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
        self.workload_obj = topologies()

        # State
        self.verbose = True
        self.trace_gen_flag = True
        self.autopartition = False
        self.single_layer_objects_list = []
        self.top_path='./'
        self.reports_dir_path = './'

        # REPORT Structures
        self.total_cycles_report_grid = []
        self.stall_cycles_report_grid = []
        self.overall_utils_report_grid = []
        self.mapping_eff_report_grid = []
        self.cycles_report_avg_items = []
        self.cycles_report_ready = False

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

        self.workload_obj = topologies()
        self.workload_obj.load_arrays(topofile=workload_filename)

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

        self.reports_dir_path = reports_dir_path

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
        single_arr_config.update_from_list(conf_list=conf_list)

        for layer_id in range(num_layers):
            if self.verbose:
                print('Running Layer ' + str(layer_id))
            this_layer_op_mat_obj = operand_matrix()

            this_layer_op_mat_obj.set_params(config_obj=single_arr_config,
                                             topoutil_obj=self.workload_obj,
                                             layer_id=layer_id)

            this_layer_sim = SingleLayerSim()
            this_layer_sim.set_params(config_obj=self.config_obj,
                                      op_mat_obj=this_layer_op_mat_obj,
                                      partitioner_obj=self.partition_obj,
                                      layer_id=layer_id,
                                      log_top_path=self.top_path,
                                      verbosity=self.verbose)
            this_layer_sim.run()
            self.single_layer_objects_list += [this_layer_sim]

            if self.save_traces:
                if self.verbose:
                    print('SAVING TRACES')
                this_layer_sim.save_traces()

        self.generate_all_reports()
        self.runs_done = True

    # Report generation
    def create_cycles_report_structures(self):
        assert self.runs_done

        for lid in range(self.workload_obj.get_num_layers()):
            this_layer_sim_obj = self.single_layer_objects_list[lid]

            total_cycles_list = this_layer_sim_obj.get_total_cycles_list()
            stall_cycles_list = this_layer_sim_obj.get_stall_cycles_list()
            overall_util_list = this_layer_sim_obj.get_overall_util_list()
            mapping_eff_list = this_layer_sim_obj.get_mapping_eff_list()
            compute_util_list = this_layer_sim_obj.get_compute_util_list()

            self.cycles_report_avg_items += [statistics.mean(total_cycles_list)]
            self.cycles_report_avg_items += [statistics.mean(stall_cycles_list)]
            self.cycles_report_avg_items += [statistics.mean(overall_util_list)]
            self.cycles_report_avg_items += [statistics.mean(mapping_eff_list)]
            self.cycles_report_avg_items += [statistics.mean(compute_util_list)]

        self.cycles_report_ready = True


    def create_bandwidth_report_structures(self):
        print('WIP')

    def create_detailed_report_structures(self):
        print('WIP')

    def save_all_cycle_reports(self):
        print('WIP')

    def save_all_bw_reports(self):
        print('WIP')

    def save_all_detailed_reports(self):
        print('WIP')

    def save_traces(self):
        print('WIP')


