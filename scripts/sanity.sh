#!/bin/bash

# Get the root directory of the Git repository
tot=$(git rev-parse --show-toplevel)

# Check if git rev-parse command was successful
if [ $? -ne 0 ]; then
    echo "Error: Must be run inside a Git repository"
    exit 1
fi

krittika_dir="${tot}/krittika"

# TODO: Add tests when ready

# Test 1: Just basic sanity run
cd "${krittika_dir}";
mkdir ../outdir/sanity/
python3 ./krittika-sim.py -c ../configs/krittika.cfg -t ../topologies/test.csv -p ../partitions/temp_part.csv -o ../outdir/sanity > ../outdir/sanity/run.log
