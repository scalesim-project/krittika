import configparser as cp


class KrittikaConfig:
    """
        This class deals with architecture configuration of the simulator
    """
    def __init__(self) -> None:
        """
            Initialize the class with default parameters
            - At this moment we support homogenous partitions
        """
        self.section_names = ['GENERAL', 'COMPUTE', 'MEMORY', 'INTERFACE']
        self.valid_partition_strategies = ['IFMAP', 'FILTER', 'CONST_DF', 'AUTO']
        self.valid_bandwidth_modes = ['USER', 'CALC']
        self.valid_dataflows = ['ws', 'is', 'os']

        # Section: GENERAL
        self.run_name = 'krittika_demo'

        # Section: COMPUTE
        self.num_compute_cores = 2
        self.matmul_core = True
        self.vector_core = True

        # Matmul unit is a systolic array
        self.matmul_rows = 32
        self.matmul_cols = 32
        self.matmul_default_df = 'ws'

        # Vector unit is a 1D systolic array
        # TODO: In the next version we can check if this is a good choice or not
        self.vector_dim = 32
        self.vector_default_df = 'ws'

        self.partition_strategy = 'AUTO'

        # Section: MEMORY
        # These offsets are legacy from SCALE-Sim code: They are user updatable
        self.ifmap_offset = 0
        self.filter_offset = int(1 * 10 ** 7)
        self.ofmap_offset = int(2 * 10 ** 7)

        # Per core SRAM sizes
        self.per_core_ifmap_sram_size_kb = 128
        self.per_core_filter_sram_size_kb = 128
        self.per_core_ofmap_sram_size_kb = 128

        # Section: INTERFACE
        self.bandwidth_mode = 'CALC'
        self.per_core_ifmap_bw_words_per_cycle = 1
        self.per_core_filter_bw_words_per_cycle = 1
        self.per_core_ofmap_bw_words_per_cycle = 1

        # Status variables
        self.config_valid = False

    #
    def read_config(self, configfilename=''):
        """
        This method reads the config file and populates the member functions 
        """

        cfg = cp.ConfigParser()
        cfg.read(configfilename)

        # GENERAL
        sec = self.section_names[0]
        self.run_name = cfg.get(sec, 'run name')

        # COMPUTE
        sec = self.section_names[1]

        num_comp_cores = int(cfg.get(sec, 'num compute cores'))
        assert num_comp_cores > 0, 'Compute cores should be > 0'
        self.num_compute_cores = num_comp_cores

        matmul_stat = cfg.get(sec, 'matmul core present')
        assert matmul_stat in ['true, True, TRUE, false, False, FALSE'], 'Status should be true or false'
        if matmul_stat in ['true, True, TRUE']:
            self.matmul_core = True
        else:
            self.matmul_core = False

        if self.matmul_core:
            rows = int(cfg.get(sec, 'matmul arrrow'))
            assert rows > 0, 'Invalid rows'
            self.matmul_rows = rows

            cols = int(cfg.get(sec, 'matmul arrcol'))
            assert cols > 0, 'Invalid cols'
            self.matmul_cols = cols

            df = cfg.get(sec, 'matmul default dataflow')
            assert df in self.valid_dataflows, 'Invalid dataflow'
            self.matmul_default_df = df

        vector_stat = cfg.get(sec, 'vector core present')
        assert vector_stat in ['true, True, TRUE, false, False, FALSE'], 'Status should be true or false'
        if vector_stat in ['true, True, TRUE']:
            self.vector_core = True
        else:
            self.vector_core = False

        if self.vector_core:
            vec_dim = int(cfg.get(sec, 'vector dim'))
            assert vec_dim > 0, 'Invalid vector dimensions'
            self.vector_dim = vec_dim

            df = cfg.get(sec, 'vector default dataflow')
            assert df in self.valid_dataflows, 'Invalid dataflow'
            self.vector_default_df = df

        part_strat = cfg.get(sec, 'partition strategy')
        assert part_strat in self.valid_partition_strategies, 'Invalid strategy: Valid values are: ' \
                                                              + ', '.join(self.valid_partition_strategies)

        self.partition_strategy = part_strat

        # MEMORY
        sec = self.section_names[1]

        ifmap_offset = int(cfg.get(sec, 'ifmap offset'))
        assert ifmap_offset >= 0, "IFMAP offset cannot be negative"
        self.ifmap_offset = ifmap_offset

        filter_offset = int(cfg.get(sec, 'filter offset'))
        assert filter_offset >= 0, "filter offset cannot be negative"
        self.filter_offset = filter_offset

        ofmap_offset = int(cfg.get(sec, 'ofmap offset'))
        assert ofmap_offset >= 0, "OFMAP offset cannot be negative"
        self.ofmap_offset = ofmap_offset

        per_core_ifmap_sram_sz = int(cfg.get(sec, 'per core ifmap sram size kb'))
        assert per_core_ifmap_sram_sz > 0, "IFMAP SRAM size cannot be zero"
        self.per_core_ifmap_sram_size_kb = per_core_ifmap_sram_sz

        per_core_filter_sram_sz = int(cfg.get(sec, 'per core filter sram size kb'))
        assert per_core_filter_sram_sz > 0, "Filter SRAM size cannot be zero"
        self.per_core_filter_sram_size_kb = per_core_filter_sram_sz

        per_core_ofmap_sram_sz = int(cfg.get(sec, 'per core ofmap sram size kb'))
        assert per_core_ofmap_sram_sz > 0, "OFMAP SRAM size cannot be zero"
        self.per_core_ofmap_sram_size_kb = per_core_ofmap_sram_sz

        # Interface
        sec = self.section_names[2]

        bw_mode = cfg.get(sec, 'bandwidth mode')
        assert bw_mode in self.valid_bandwidth_modes, 'Valid BW modes are: ' + ', '.join(self.valid_bandwidth_modes)
        self.bandwidth_mode = bw_mode

        per_core_ifmap_bw = int(cfg.get(sec, 'per per core user ifmap buf interface bw (words/cycle)'))
        assert per_core_ifmap_bw > 0, 'Bandwidth cannot be -ve or zero'
        self.per_core_ifmap_bw_words_per_cycle = per_core_ifmap_bw

        per_core_filter_bw = int(cfg.get(sec, 'per per core user filter buf interface bw (words/cycle)'))
        assert per_core_filter_bw > 0, 'Bandwidth cannot be -ve or zero'
        self.per_core_filter_bw_words_per_cycle = per_core_filter_bw

        per_core_ofmap_bw = int(cfg.get(sec, 'per per core user ofmap buf interface bw (words/cycle)'))
        assert per_core_ofmap_bw > 0, 'Bandwidth cannot be -ve or zero'
        self.per_core_ofmap_bw_words_per_cycle = per_core_ofmap_bw

        self.config_valid = True

    #
    def load_config(self):
        """
        This method is intended to update the class members from an internal data structure
        """
        pass

    def get_partition_mode(self):
        """
            Returns the partition mode set by the user
        """
        assert self.config_valid, 'Please set the configurations first'
        return self.partition_strategy

    def get_num_cores(self):
        """
            Returns the number of cores set by the user
        """
        assert self.config_valid, 'Please set the configurations first'
        return self.num_compute_cores

    def get_default_matmul_dataflow(self):
        """
            Returns the default dataflow of the matmul unit set by the user
        """
        assert self.config_valid, 'Please set the configurations first'
        return self.matmul_default_df

    def get_default_vector_dataflow(self):
        """
            Returns the default dataflow of the vector unit set by the user
        """
        assert self.config_valid, 'Please set the configurations first'
        return self.vector_default_df

    def get_compute_unit_valids(self):
        """
            Returns the valid bit for mat_mul and vector units set by the user
        """
        assert self.config_valid, 'Please set the configurations first'
        return self.matmul_core, self.vector_core

    def get_matmul_dims(self):
        """
            Returns the dimensions of the mmx unit set by the user
        """
        assert self.config_valid, 'Please set the configurations first'
        return self.matmul_rows, self.matmul_cols

    def get_vector_dims(self):
        """
            Returns the dimensions of the vector unit set by the user
        """
        assert self.config_valid, 'Please set the configurations first'
        return self.vector_dim



