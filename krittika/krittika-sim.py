import argparse

from krittika.simulator import Simulator

if __name__ == '__main__':
    '''
        Input parameters:
        -t : Path to topology file
        -c : Path to config file
        -p : Path to partition file (Not needed if partition mode is auto)
        -o : Path to log dump directory 
        --verbose: Verbosity of the run (Default: True)
        --savetrace: If True then saves the traces (Default: True) 
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument('-t', metavar='Topology file', type=str,
                        default='../topologies/conv_nets/test.csv',
                        help='Path to the topology CSV file'
                        )

    parser.add_argument('-c', metavar='Config file', type=str,
                        default='../configs/krittika.cfg',
                        help='Path to the config file'
                        )

    parser.add_argument('-p', metavar='Partition file', type=str,
                        default='../part_files/demo_partition_file.csv',
                        help='Path to the partition file'
                        )

    parser.add_argument('-o', metavar='Top path', type=str,
                        default='../test_run_outputs',
                        help='Path to the log dump directory'
                        )

    parser.add_argument('--verbose', metavar='Verbosity', type=bool,
                        default=True,
                        help='Flag to change the verbosity of the run'
                        )

    parser.add_argument('--savetrace', metavar='Save traces', type=bool,
                        default=False,
                        help='Flag to indicate if the traces should be saved'
                        )

    args = parser.parse_args()

    topology_file = args.t
    config_file = args.c
    partition_file = args.p
    logs_top_path = args.o

    verbosity = args.verbose
    save_traces_flag = args.savetrace

    krittika = Simulator()
    krittika.set_params(
        config_filename=config_file,
        workload_filename=topology_file,
        custom_partition_filename=partition_file,
        reports_dir_path=logs_top_path,
        verbose=verbosity,
        save_traces=save_traces_flag
    )

    krittika.run()

    print('Krittika Run Done')
