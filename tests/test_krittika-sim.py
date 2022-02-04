from krittika.compute.compute_node import ComputeNode
from krittika.krittika_config import KrittikaConfig as kconfig

def test_os_mmx(cfg_obj=kconfig()):

    mut = ComputeNode()
    mut.set_params(
        config=cfg_obj,
        compute_unit='MMX',
        dataflow='os'    
    )    

