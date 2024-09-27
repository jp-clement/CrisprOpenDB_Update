# Snakemake to update the CrisprOpenDB

## To launch the pipeline from scratch, run the following command:
bash run_pipeline.sh

This will:
- set up the venv
- download the most recent set of assembly from NCBI
- generate a new set of bash scripts from the new assembly list
- remove all log files
- remove all flags
- launch Snakemake

## To lunch snakemake if many of the above steps have already been performed, run the following command:
source DB_UPDATE/bin/activate ; snakemake --unlock ; snakemake -pk --profile profile --rerun-incomplete

## config files
The SLURM parameters for the Snakemake can be updated from the file:
profile/config.yaml

Most of the other parameter (e.g. location of the CrisprOpenDB.sqlite file or the assembly_list) can be modified in the file:
profile/python_params.txt