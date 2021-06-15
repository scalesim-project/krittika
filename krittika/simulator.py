from krittika.config.krittika_config import KrittikaConfig
from krittika.workload_manager import WorkloadManager

class Simulator:
    def __init__(self):
        # Objects
        self.config_obj = KrittikaConfig()
        self.workload_obj = WorkloadManager()
        self.scheduler_obj = ScheduleManager()

        #
        self.autoschedule = False

        # Flags
        self.params_valid = False

    def set_params(self,
                   config_filename='',
                   workload_filename='',
                   autoschedule=False,
                   custom_schedule_filename=''
                   ):
        # Read the user input and files and prepare the objects
        self.config_obj.read_config_from_file(filename=config_filename)
        self.workload_obj.read_topologies(workload_filename=workload_filename)

        self.autoschedule = autoschedule
        if self.autoschedule:
            self.scheduler_obj.compute_schedule()
        else:
            self.scheduler_obj.read_user_schedule(filename=custom_schedule_filename)

        self.params_valid = True

    def run(self):
        # Orchestrate among the function calls to run simulations
        assert self.params_valid, 'Cannot run simulation without inputs'

        # Run compute simulations for all layers first

        # For all the generated compute simulations run the memory sims
