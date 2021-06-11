from configparser import ConfigParser


class KrittikaConfig:
    def __init__(self):

        self.run_name = 'default_run_name'

        #
        self.num_compute_cores = 1
        self.matmul_present = True
        self.vector_present = True

        self.matmul_arr_row = 1
        self.matmul_arr_col = 1
        self.matmul_default_dataflow = 'ws'

        self.vector_dim = 1
        self.vector_default_dataflow = 'ws'

        self.default_ifmap_offset = 0
        self.default_filter_offset = 10 ** 7
        self.default_ofmap_offset = 2 * 10 ** 7

        # Supported partition modes:
        # USER, IFMAP, FILTER, AUTO (Best effort first filter, then inputs)
        self.partition_mode = 'AUTO'

        self.per_unit_ifmap_sram_size_kb = 1
        self.per_unit_filter_sram_size_kb = 1
        self.per_unit_ofmap_sram_size_kb = 1

        # Suported bandwidth modes: 'USER', 'CALC'
        self.bandwidth_use_mode = 'CALC'

        self.per_unit_user_ifmap_interface_bw = 1
        self.per_unit_user_filter_interface_bw = 1
        self.per_unit_user_ofmap_interface_bw = 1

        # Flags
        self.config_valid = False

    #
    def __force_valid(self):
        self.config_valid = True

    #
    def read_config_from_file(self, filename):

        cfg = ConfigParser()
        cfg.read(filename)

        section = 'GENERAL'
        self.run_name = int(cfg.get(section, 'Run Name'))

        section = 'COMPUTE'
        self.num_compute_cores = int(cfg.get(section, 'Num Compute Cores'))

        matmul_present_str = cfg.get(section, 'MatMul Core Present')
        if matmul_present_str in ['true', 'True', 'TRUE']:
            self.matmul_present = True
            self.matmul_arr_row = int(cfg.get(section, 'MatMul ArrRow'))
            self.matmul_arr_col = int(cfg.get(section, 'MatMul ArrCol'))

            matmul_default_dataflow = cfg.get(section, 'MatMul Default Dataflow')
            assert matmul_default_dataflow in ['os', 'ws', 'is'], 'Invalid dataflow: ' + str(matmul_default_dataflow)
            self.matmul_default_dataflow = matmul_default_dataflow

        else:
            self.matmul_present = False

        vector_present_str = cfg.get(section, 'Vector Core Present')
        if vector_present_str in ['true', 'True', 'TRUE']:
            self.vector_present = True
            self.vector_dim = int(cfg.get(section, 'Vector Dim'))

            vector_default_dataflow = cfg.get(section, 'Vector Default Dataflow')

            assert vector_default_dataflow in ['os', 'ws', 'is'], 'Invalid dataflow: ' + str(vector_default_dataflow)
            self.vector_default_dataflow = vector_default_dataflow

        else:
            self.vector_present = False

        part_strategy = cfg.get(section, 'Partition Strategy')
        assert part_strategy in ['USER', 'IFMAP', 'FILTER', 'AUTO'], \
            'Invalid partition mode ' + part_strategy + '. Supported vals: [USER, AUTO, IFMAP, FILTER]'
        self.partition_mode = part_strategy

        section = 'MEMORY'
        ifmap_offset = int(cfg.get(section, 'IFMAP Offset'))
        filter_offset = int(cfg.get(section, 'FITLER Offset'))
        ofmap_offset = int(cfg.get(section, 'OFMAP Offset'))

        assert ifmap_offset >= 0, 'Offsets cannot be negative'
        assert filter_offset >= 0, 'Offsets cannot be negative'
        assert ofmap_offset >= 0, 'Offsets cannot be negative'

        self.default_ifmap_offset = ifmap_offset
        self.default_filter_offset = filter_offset
        self.default_ofmap_offset = ofmap_offset

        ifmap_sram_sz = int(cfg.get(section, 'Per Core IFMAP SRAM Size KB'))
        filter_sram_sz = int(cfg.get(section, 'Per Core FILTER SRAM Size KB'))
        ofmap_sram_sz = int(cfg.get(section, 'Per Core OFMAP SRAM Size KB'))

        assert ifmap_sram_sz > 0, 'Invalid SRAM size'
        assert filter_sram_sz > 0, 'Invalid SRAM size'
        assert ofmap_sram_sz > 0, 'Invalid SRAM size'

        section = 'INTERFACE'
        bw_mode = cfg.get(section, 'Bandwidth Mode')
        assert bw_mode in ['USER', 'CALC'], 'Invalid mode of operation: ' + bw_mode + '. Valid modes are [USER, CALC]'
        self.bandwidth_use_mode = bw_mode

        ifmap_bw = int(cfg.get(section, 'Per Core User IFMAP buf interface BW (Words/Cycle)'))
        filter_bw = int(cfg.get(section, 'Per Core User FILTER buf interface BW (Words/Cycle)'))
        ofmap_bw = int(cfg.get(section, 'Per Core User 0FMAP buf interface BW (Words/Cycle)'))

        assert ifmap_bw > 0, 'Invalid BW value'
        assert filter_bw > 0, 'Invalid BW value'
        assert ofmap_bw > 0, 'Invalid BW value'

        self.per_unit_user_ifmap_interface_bw = ifmap_bw
        self.per_unit_user_filter_interface_bw = filter_bw
        self.per_unit_user_ofmap_interface_bw = ofmap_bw

        self.config_valid = True

    # ------ SET METHODS ------
    #
    def set_config_vals(self,
                        run_name='',
                        matmul_valid=True, vector_valid=True,
                        matmul_arr_row=1, matmul_arr_col=1,
                        matmul_dataflow='',
                        vector_macs=1, vector_dataflow='',
                        ifmap_offset=0, filter_offset=10**7, ofmap_offset=2*10**7,
                        partition_mode='',
                        ifmap_sram_kb=1, filter_sram_kb=1, ofmap_sram_kb=1,
                        bw_use_mode='',
                        per_core_ifmap_bw=1, per_core_filter_bw=1, per_core_ofmap_bw=1
                        ):

        assert run_name is not '', 'Please provide a valid run name'
        assert matmul_arr_row > 0 and matmul_arr_col > 0, 'Dimensions should be non zero and positive'
        assert matmul_dataflow in ['os', 'ws', 'is'], 'Invalid dataflow: ' + matmul_dataflow
        assert vector_macs > 0, 'Vector dimensions should be non zero and positive'
        assert vector_dataflow in ['os', 'ws', 'is'], 'Invalid dataflow: ' + vector_dataflow
        assert ifmap_offset >= 0, 'Offsets should be non negative integers'
        assert filter_offset >= 0, 'Offsets should be non negative integers'
        assert ofmap_offset >= 0, 'Offsets should be non negative integers'
        assert partition_mode in ['USER', 'AUTO', 'IFMAP', 'FILTER'], 'Invalid partition mode provided'
        assert ifmap_sram_kb > 0, 'SRAM sizes should be a positive integer'
        assert filter_sram_kb > 0, 'SRAM sizes should be a positive integer'
        assert ofmap_sram_kb > 0, 'SRAM sizes should be a positive integer'
        assert bw_use_mode in ['USER', 'CALC'], 'Invalid interface bandwidth mode provided'
        assert per_core_ifmap_bw > 0, 'Bandwidth should be positive integer'
        assert per_core_filter_bw > 0, 'Bandwidth should be positive integer'
        assert per_core_ofmap_bw > 0, 'Bandwidth should be positive integer'

        self.config_valid = True

        self.set_run_name(input_run_name=run_name)
        self.set_compute_unit_valids(matmul_valid=matmul_valid, vector_valid=vector_valid)
        self.set_matmul_dims(arr_row=matmul_arr_row, arr_col=matmul_arr_col)
        self.set_matmul_dataflow(input_dataflow=matmul_dataflow)
        self.set_vector_dim(vector_mac=vector_macs)
        self.set_vector_dataflow(input_dataflow=vector_dataflow)
        self.set_operand_offsets(ifmap_offset=ifmap_offset, filter_offset=filter_offset, ofmap_offset=ofmap_offset)
        self.set_partition_mode(part_mode=partition_mode)
        self.set_per_unit_sram_sizes_kb(ifmap_sram_kb=ifmap_sram_kb, filter_sram_kb=filter_sram_kb,
                                        ofmap_sram_kb=ofmap_sram_kb)
        self.set_bandwidth_use_mode(bw_use_mode=bw_use_mode)
        self.set_interface_bandwidths(per_core_ifmap_bw=per_core_ifmap_bw, per_core_filter_bw=per_core_filter_bw,
                                      per_core_ofmap_bw=per_core_ofmap_bw)

    #
    def set_run_name(self, input_run_name=''):
        assert self.config_valid
        assert input_run_name is not ''

        self.run_name = input_run_name

    #
    def set_compute_unit_valids(self, matmul_valid=True, vector_valid=True):
        assert self.config_valid

        self.matmul_present = matmul_valid
        self.vector_present = vector_valid

    #
    def set_matmul_dims(self, arr_row=1, arr_col=1):
        assert self.config_valid and self.matmul_present
        assert arr_row > 0 and arr_col > 0, 'Dimensions should be non zero and positive'

        self.matmul_arr_row = arr_row
        self.matmul_arr_col = arr_col

    #
    def set_matmul_dataflow(self, input_dataflow=''):
        assert self.config_valid and self.matmul_present
        assert input_dataflow in ['os', 'ws', 'is'], 'Invalid dataflow: ' + input_dataflow

        self.matmul_default_dataflow = input_dataflow

    #
    def set_vector_dim(self, vector_mac=1):
        assert self.config_valid and self.vector_present
        assert vector_mac > 0, 'Dimensions should be non zero and positive'

        self.vector_dim = vector_mac

    #
    def set_vector_dataflow(self, input_dataflow=''):
        assert self.config_valid and self.vector_present
        assert input_dataflow in ['os', 'ws', 'is'], 'Invalid dataflow: ' + input_dataflow

        self.vector_default_dataflow = input_dataflow

    #
    def set_operand_offsets(self, ifmap_offset=0, filter_offset=10 ** 7, ofmap_offset=2 * 10 ** 7):
        assert self.config_valid
        assert not ifmap_offset < 0, 'Offsets should be non negative integers'
        assert not filter_offset < 0, 'Offsets should be non negative integers'
        assert not ofmap_offset < 0, 'Offsets should be non negative integers'

        self.default_ifmap_offset = int(ifmap_offset)
        self.default_filter_offset = int(filter_offset)
        self.default_filter_offset = int(ofmap_offset)

    #
    def set_partition_mode(self, part_mode = ''):
        assert self.config_valid
        assert part_mode in ['USER', 'AUTO', 'IFMAP', 'FILTER'], 'Invalid partition mode provided'

        self.partition_mode = part_mode

    #
    def set_per_unit_sram_sizes_kb(self, ifmap_sram_kb=0, filter_sram_kb=0, ofmap_sram_kb=0):
        assert self.config_valid
        assert ifmap_sram_kb > 0, 'SRAM sizes should be a positive integer'
        assert filter_sram_kb > 0, 'SRAM sizes should be a positive integer'
        assert ofmap_sram_kb > 0, 'SRAM sizes should be a positive integer'

        self.per_unit_ifmap_sram_size_kb = ifmap_sram_kb
        self.per_unit_filter_sram_size_kb = filter_sram_kb
        self.per_unit_ofmap_sram_size_kb = ofmap_sram_kb

    #
    def set_bandwidth_use_mode(self, bw_use_mode=''):
        assert self.config_valid
        assert bw_use_mode in ['USER', 'CALC'], 'Invalid interface bandwidth mode provided'

        self.bandwidth_use_mode = bw_use_mode

    #
    def set_interface_bandwidths(self, per_core_ifmap_bw=0, per_core_filter_bw=0, per_core_ofmap_bw=0):
        assert self.config_valid
        assert per_core_ifmap_bw > 0, 'Bandwidth should be positive integer'
        assert per_core_filter_bw > 0, 'Bandwidth should be positive integer'
        assert per_core_ofmap_bw > 0, 'Bandwidth should be positive integer'

        self.per_unit_user_ifmap_interface_bw = per_core_ifmap_bw
        self.per_unit_user_filter_interface_bw = per_core_filter_bw
        self.per_unit_user_ofmap_interface_bw = per_core_ofmap_bw

    # ------ GET METHODS ------
    #
    def get_run_name(self):
        assert self.config_valid
        return self.run_name

    #
    def get_compute_unit_valids(self):
        assert self.config_valid
        return self.matmul_present, self.vector_present

    #
    def get_matmul_dims(self):
        assert self.config_valid and self.matmul_present
        return self.matmul_arr_row, self.matmul_arr_col

    #
    def get_matmul_dataflow(self):
        assert self.config_valid and self.matmul_present
        return self.matmul_default_dataflow

    #
    def get_vector_dim(self):
        assert self.config_valid and self.vector_present
        return self.vector_dim

    #
    def get_vector_dataflow(self):
        assert self.config_valid and self.vector_present
        return self.vector_default_dataflow

    #
    def get_operand_offsets(self):
        assert self.config_valid
        return self.default_ifmap_offset, self.default_filter_offset, self.default_ofmap_offset

    #
    def get_partition_mode(self):
        assert self.config_valid
        return self.partition_mode

    #
    def get_per_unit_sram_sizes_kb(self):
        assert self.config_valid
        return self.per_unit_ifmap_sram_size_kb, \
                self.per_unit_filter_sram_size_kb, \
                self.per_unit_ofmap_sram_size_kb

    #
    def get_bandwidth_use_mode(self):
        assert self.config_valid
        return self.bandwidth_use_mode

    #
    def get_interface_bandwidths(self):
        assert self.config_valid
        return self.per_unit_user_ifmap_interface_bw, \
               self.per_unit_user_filter_interface_bw, \
               self.per_unit_user_ofmap_interface_bw

    #
    def write_config_file(self, filename='krittika_config.cfg'):
        assert self.config_valid

        cp = ConfigParser()

        section = 'GENERAL'
        cp.add_section(section)
        cp.set(section, 'Run Name', str(self.run_name))

        section = 'COMPUTE'
        cp.add_section(section)
        cp.set(section, 'Num Compute Cores', str(self.num_compute_cores))
        cp.set(section, 'MatMul Core Present', str(self.matmul_present))
        cp.set(section, 'Vector Core Present', str(self.vector_present))

        if self.matmul_present:
            cp.set(section, 'MatMul ArrRow', str(self.matmul_arr_row))
            cp.set(section, 'MatMul ArrCol', str(self.matmul_arr_col))
            cp.set(section, 'MatMul Default Dataflow', str(self.matmul_default_dataflow))

        if self.vector_present:
            cp.set(section, 'Vector Dim', str(self.vector_dim))
            cp.set(section, 'Vector Default Dataflow', str(self.vector_default_dataflow))

        cp.set(section, 'Partition Strategy', str(self.partition_mode))

        section = 'MEMORY'
        cp.add_section(section)
        cp.set(section, 'IFMAP Offset', str(self.default_ifmap_offset))
        cp.set(section, 'FILTER Offset', str(self.default_filter_offset))
        cp.set(section, 'OFMAP Offset', str(self.default_ofmap_offset))

        cp.set(section, 'Per Core IFMAP SRAM Size KB', str(self.per_unit_ifmap_sram_size_kb))
        cp.set(section, 'Per Core FILTER SRAM Size KB', str(self.per_unit_filter_sram_size_kb))
        cp.set(section, 'Per Core OFMAP SRAM Size KB', str(self.per_unit_ofmap_sram_size_kb))

        section = 'INTERFACE'
        cp.add_section(section)
        cp.set(section, 'Bandwidth Mode', str(self.bandwidth_use_mode))
        cp.set(section, 'Per Core User IFMAP buf interface BW (Words/Cycle)',
                            str(self.per_unit_user_ifmap_interface_bw))
        cp.set(section, 'Per Core User FITLER buf interface BW (Words/Cycle)',
                            str(self.per_unit_user_filter_interface_bw))
        cp.set(section, 'Per Core User OFMAP buf interface BW (Words/Cycle)',
                            str(self.per_unit_user_ofmap_interface_bw))

        with open(filename, 'w') as configfile:
            cp.write(configfile)

    #
    @staticmethod
    def write_default_config(filename='krittika_default_config.cfg'):
        default = KrittikaConfig()
        default.__force_valid()
        default.write_config_file(filename)
