
# TODO: Anand: This should be renamed to partitioner
# I intend to use this class to read write generate and update the partitioning schedule
class PartitionManager:
    def __init__(self):
        self.partition_table = []

        # Flags
        self.partition_table_valid = False

    def get_layer_partitions(self, layer_id=0):
        assert self.partition_table_valid, 'Partition table is not valid'

        partition_data = self.partition_table[layer_id]
        input_part = partition_data[1]
        filter_part = partition_data[2]

        return input_part, filter_part

    #
    def get_opt_compute_params(self, layer_id=0):
        assert self.partition_table_valid, 'Partition table is not valid'

        partition_data = self.partition_table[layer_id]
        opt_compute_unit = partition_data[3]
        opt_dataflow = partition_data[4]

        return opt_compute_unit, opt_dataflow
