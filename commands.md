# PACE-ICE setup:

    # Login
    ssh <userID>@login-ice.pace.gatech.edu

    # Load conda
    module load anaconda3

# Setting up the conda env

    # Creating a new conda env
    conda create --name <>
    conda activate <>
    conda install pip
    pip install -r ./requirements.txt   

### Optional conda cmds

    # Dumping conda env to yaml
    conda env export > my_env.yml
    # Then you can just create using this .yml
    conda env create -f my_env.yml

# Setting up the repo

    git clone --recursive https://github.com/5ree/krittika_hml_proj.git
    # If you didn't recursively clone the repo, you'd miss all deps. To fix that:
    git submodule update --init --recursive

    # Build our ANoC's py bindings
    # THIS IS NEEDED FOR USING THE ANOC!
    # FIXME: Find a way to do this via requirements.txt
    python setup.py build_ext --inplace

# Running a test:
    # Launch Krittika:
    cd $root;
    python3 ./krittika/krittika-sim.py -c ./configs/krittika.cfg -t ./topologies/test.csv -o ./outdir/sanity/ -p ./partitions/temp_part.csv

