import math


class WorkloadManager:
    def __init__(self):

        self.num_layers = 0
        self.topo_file_name = ''
        self.topo_list = []
        self.spatio_temp_dim_arrays = []
        self.layers_calculated_hyperparams = []
        self.topo_valid = False
        self.topo_hyper_param_valid = False
        self.topo_spatiotemp_params_valid = False

    def test(self):
        self.read_topologies('./topologies/test.csv')
        print(self.topo_list)
        self.topo_calc_hyperparams()
        print(self.get_layer_ifmap_dims(3))
        self.get_layer_window_size(3)
        self.set_spatio_temporal_params()
        print(self.get_layer_spatio_temp_dim_arrays(3))
        print(self.get_spatiotemporal_dims(3,'ws'))
        
    #
    def read_topologies(self, workload_filename=''):
        self.topo_file_name = workload_filename
        f = open(workload_filename)
        format = 'conv'

        for index, row in enumerate(f):
                format = str(row.strip("").split(', ')[0].strip(""))
                assert format in ['gemm', 'conv', 'activation']

                if format == "conv":
                    self.load_arrays_conv(row, index)
                elif format == "gemm":
                    self.load_arrays_gemm(row, index)
                elif format == "activation":
                    self.load_arrays_activation(row, index)

                self.num_layers += 1

        # There should be atleast one layer in topology file
        if self.num_layers > 0:
            self.topo_valid = True
    
    #
    def load_arrays_conv(self, row, layer_id):
        row = row.strip()
        elems = row.split(',')[:]
        entry = ['conv', layer_id]
        for i in range(1, len(elems)):
            val = int(str(elems[i].strip()))
            entry.append(val)
            
            if i == 7 and len(elems) < 9:
                entry.append(val)  # Add the same stride in the col direction automatically

        assert entry[4] <= entry[2], 'Filter height cannot be larger than IFMAP height'
        assert entry[5] <= entry[3], 'Filter width cannot be larger than IFMAP width'

        self.topo_list.append(entry)
    
    #    
    def load_arrays_gemm(self, row, layer_id):
        row = row.strip()
        elems = row.split(',')[:]
        m = int(elems[1].strip())
        n = int(elems[2].strip())
        k = int(elems[3].strip())
        entry = ['gemm', layer_id, m, k, 1, k, 1, n, 1, 1]

        self.topo_list.append(entry)
    
    #
    def load_arrays_activation(self, row, layer_id):
        row = row.strip()
        elems = row.split(',')[:]
        entry = ['activation', layer_id]
        for i in range(1, len(elems)):
            func = str(elems[i].strip())
            assert func in ['relu', 'batch_norm', 'tanh', 'softmax'], \
                'Unsupported activation, choose from relu, batch_norm, tanh, softmax'
            entry.append(func)

        self.topo_list.append(entry)

    #
    def get_num_layers(self):
        if not self.topo_valid:
            print("ERROR: topologies not loaded")

        return self.num_layers

    # calculate hyper-parameters (ofmap dimensions, number of MACs, and window size of filter)
    def topo_calc_hyperparams(self, topofilename=""):
        if not self.topo_valid:
            self.read_topologies(topofilename)
        self.layers_calculated_hyperparams = []
        for array in self.topo_list:
            if array[0] in ['conv', 'gemm']:
                layer_id = array[1]
                ifmap_h = array[2]
                ifmap_w = array[3]
                filt_h = array[4]
                filt_w = array[5]
                num_ch   = array[6]
                num_filt = array[7]
                stride_h = array[8]
                stride_w = array[9]
                ofmap_h = int(math.ceil((ifmap_h - filt_h + stride_h) / stride_h))
                ofmap_w = int(math.ceil((ifmap_w - filt_w + stride_w) / stride_w))
                num_mac = ofmap_h * ofmap_w * filt_h * filt_w * num_ch * num_filt
                window_size = filt_h * filt_w * num_ch
                entry = [layer_id, ofmap_h, ofmap_w, num_mac, window_size]
                print(entry)
                self.layers_calculated_hyperparams.append(entry)
        self.topo_hyper_param_valid = True


    #
    def get_layer_ifmap_dims(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_ifmap_dims: Invalid layer id")
        
        layer_params = self.topo_list[layer_id]
        assert layer_params[0] in ['conv', 'gemm'], 'It should be a conv/gemm layer'
        
        return layer_params[2:4]    # Idx = 2, 3

    #
    def get_layer_filter_dims(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_ifmap_dims: Invalid layer id")

        layer_params = self.topo_list[layer_id]
        return layer_params[4:6]    # Idx = 4, 5

    #
    def get_layer_num_channels(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_num_filter: Invalid layer id")

        layer_params = self.topo_list[layer_id]
        assert layer_params[0] in ['conv', 'gemm'], 'It should be a conv/gemm layer'
        
        return layer_params[6]

    #
    def get_layer_num_filters(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_num_filter: Invalid layer id")
        
        layer_params = self.topo_list[layer_id]
        assert layer_params[0] in ['conv', 'gemm'], 'It should be a conv/gemm layer'

        return layer_params[7]


    #
    def get_layer_strides(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_strides: Invalid layer id")

        layer_params = self.topo_list[layer_id]
        assert layer_params[0] in ['conv', 'gemm'], 'It should be a conv/gemm layer'

        return layer_params[8:10]

    #
    def get_layer_window_size(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_num_filter: Invalid layer id")
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams()

        layer_params = self.topo_list[layer_id]
        assert layer_params[0] in ['conv', 'gemm'], 'It should be a conv/gemm layer'

        layer_hyperparams = self.get_layer_hyperparams(layer_id)

        return layer_hyperparams[4]
    
    #
    def get_layer_num_ofmap_px(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_num_filter: Invalid layer id")
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams()

        layer_params = self.topo_list[layer_id]
        assert layer_params[0] in ['conv', 'gemm'], 'It should be a conv/gemm layer'

        layer_hyperparams = self.get_layer_hyperparams(layer_id)

        num_filters = self.get_layer_num_filters(layer_id)
        num_ofmap_px = layer_hyperparams[1] * layer_hyperparams[2] * num_filters 
        return num_ofmap_px

    #
    def get_layer_ofmap_dims(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_ofmap_dims: Invalid layer id")
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams()

        layer_params = self.topo_list[layer_id]
        assert layer_params[0] in ['conv', 'gemm'], 'It should be a conv/gemm layer'

        layer_hyperparams = self.get_layer_hyperparams(layer_id)

        ofmap_dims = layer_hyperparams[1:3]
        return ofmap_dims

    #
    def get_layer_params(self, layer_id=0):
        if not (self.topo_valid or self.num_layers - 1 < layer_id):
            print("ERROR: topologies.get_layer_params: Invalid layer id")
            return
        layer_params = self.topo_list[layer_id]
        return layer_params

    #
    def calc_spatio_temporal_params(self, df='os', layer_id=0):
        s_row = -1
        s_col = -1
        t_time = -1
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams(self.topo_file_name)

        num_filt  = self.get_layer_num_filters(layer_id= layer_id)
        num_ofmap = self.get_layer_num_ofmap_px(layer_id=layer_id)
        num_ofmap = int(num_ofmap / num_filt)
        window_sz = self.get_layer_window_size(layer_id=layer_id)
        if df == 'os':
            s_row = num_ofmap
            s_col = num_filt
            t_time = window_sz
        elif df == 'ws':
            s_row = window_sz
            s_col = num_filt
            t_time = num_ofmap
        elif df == 'is':
            s_row = window_sz
            s_col = num_ofmap
            t_time = num_filt
        
        return s_row, s_col, t_time

    #
    def set_spatio_temporal_params(self):
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams(self.topo_file_name)
        for i  in range(self.num_layers):
            if self.topo_list[i][0] in ['conv', 'gemm']:
                this_layer_params_arr = [i]
                for df in ['os', 'ws', 'is']:
                    sr, sc, tt = self.calc_spatio_temporal_params(df=df, layer_id=i)
                    this_layer_params_arr.append([sr, sc, tt])
                self.spatio_temp_dim_arrays.append(this_layer_params_arr)
        self.topo_spatiotemp_params_valid = True

    #
    def get_transformed_mnk_dimensions(self, layer_id=0):
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams(self.topo_file_name)

        M = 0
        N = 0
        K = 0
        if self.topo_list[layer_id][0] in ['conv', 'gemm']:
            M = self.get_layer_num_ofmap_px(layer_id)
            N = self.get_layer_num_filters(layer_id)
            K = self.get_layer_window_size(layer_id)

        return (M, N, K)
    
    #
    def get_layer_mac_ops(self, layer_id=0):
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams(topofilename=self.topo_file_name)
        layer_hyperparams = self.get_layer_hyperparams(layer_id)
        mac_ops = layer_hyperparams[3]
        return mac_ops

    #
    def get_all_mac_ops(self):
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams(topofilename=self.topo_file_name)
        total_mac = 0
        for layer in range(self.num_layers):
            total_mac += self.get_layer_mac_ops(layer)
        return total_mac

    # spatio-temporal dimensions specific to dataflow
    def get_spatiotemporal_dims(self, layer_id=0, df='ws'):
        if not self.topo_spatiotemp_params_valid:
            self.set_spatio_temporal_params()
        df_list = ['os', 'ws', 'is']
        df_idx = df_list.index(df)

        layer_spatio_temp_arrays = self.get_layer_spatio_temp_dim_arrays(layer_id)

        s_row = layer_spatio_temp_arrays[df_idx+1][0] #+1 is used to account for layer id at index 0
        s_col = layer_spatio_temp_arrays[df_idx+1][1]
        t_time = layer_spatio_temp_arrays[df_idx+1][2]
        return s_row, s_col, t_time

    #
    def get_layer_hyperparams(self, layer_id=0):
        if not self.topo_hyper_param_valid:
            self.topo_calc_hyperparams(topofilename=self.topo_file_name)

        for hyperparams in self.layers_calculated_hyperparams:
            if hyperparams[0] == layer_id:
                layer_hyperparams = hyperparams

        return layer_hyperparams

    #
    def get_layer_spatio_temp_dim_arrays(self, layer_id=0):
        if not self.topo_spatiotemp_params_valid:
            self.set_spatio_temporal_params()

        for spatio_temp_arrays in self.spatio_temp_dim_arrays:
            if spatio_temp_arrays[0] == layer_id:
                spatio_temp_arrays = spatio_temp_arrays

        return spatio_temp_arrays