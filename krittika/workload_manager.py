from scalesim.topology_utils import topologies


class WorkloadManager:
    def __init__(self):

        self.num_networks = 1
        self.list_of_topologies = []
        self.topo_valid = False

    def read_topologies(self, workload_filename=''):

        f = open(workload_filename)
        line_num = 0
        format = 'conv'

        for row in f:
            if line_num == 0:
                format = str(row.strip("").split(', ')[1].strip(""))
                assert format in ['gemm', 'conv']
            else:
                topofilename = str(row.strip("").split(', ')[0].strip(""))
                topo_obj = topologies()

                if format == 'gemm':
                    topo_obj.load_arrays(topofilename, mnk_inputs=True)
                else:
                    topo_obj.load_arrays(topofilename)

                self.list_of_topologies += [topo_obj]
                line_num += 1

        self.num_networks = line_num - 1

        # There should be atleast 3 lines or 1 topofile
        if line_num > 1:
            self.topo_valid = True