# PACE-ICE setup:
```bash
# Login
ssh <userID>@login-ice.pace.gatech.edu

# Load conda
module load anaconda3
```

# Cloning the repo
```bash
git clone --recursive https://github.com/5ree/krittika_hml_proj.git
    
# If you didn't recursively clone the repo, you'd miss all deps. To fix that:
git submodule update --init --recursive
```

# Setting up the conda env
```bash
# Creating a new conda env
conda create --name <>
conda activate <>
conda install pip
pip install -r ./requirements.txt
```

### Optional conda cmds
```bash
# Dumping conda env to yaml
conda env export > my_env.yml
# Then you can just create using this .yml
conda env create -f my_env.yml
```

# Building the ANoC cython binding
```bash
# THIS IS NEEDED FOR USING THE ANOC!
# FIXME: Find a way to do this via requirements.txt
cd dependencies/AstraSimANoCModel/;
python setup.py build_ext --inplace
```

# Installing Krittika
```bash
# FIXME: Getting errors when adding this in requirements.txt so adding a manual step now
cd <your repo root>;
pip install -e .
```

# Running a test:
```bash
# Launch Krittika:
cd <your repo root>;
python3 ./krittika/krittika-sim.py -c ./configs/krittika.cfg -t ./topologies/test.csv -o ./outdir/sanity/ -p ./partitions/temp_part.csv
```
