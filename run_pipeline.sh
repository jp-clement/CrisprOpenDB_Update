#!/bin/bash
#SBATCH --time=30:00:00
#SBATCH --account=def-eroussea
#SBATCH -o logs/run_pipeline.out
#SBATCH --error=logs/run_pipeline.err

# Building venv
echo "Building venv" 

rm- r DB_UPDATE
module load StdEnv/2020  intel/2020.1.217 
module load python/3.10
virtualenv --no-download DB_UPDATE
source DB_UPDATE/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
deactivate

# cp -a -r logs "archive/logs-$(date +"%m-%d-%y-%r")"
# find logs/ -type f -exec rm -rf {} \;

# Build folder structure 
echo "Building folder structure" 

mkdir /genomes_list/
mkdir archive
mkdir scripts/bash

# find output/ -type f -exec rm -rf {} \;
mkdir output/
mkdir output/archive/
mkdir output/spacers/
mkdir output/taxonomy/

mkdir logs
mkdir logs/completion_flags/
mkdir scripts/bash_jobs/
mkdir logs/download/
mkdir logs/unzip/
mkdir logs/crisprD/
mkdir logs/updateDB/
mkdir logs/completion_flags/
mkdir logs/saveSpacers/
mkdir logs/fetch_taxonomy/

# # Get genome assembly list
# echo "Getting genome assembly list" 
# wget ftp://ftp.ncbi.nih.gov/genomes/genbank/bacteria/assembly_summary.txt -O genomes_list/$(date +"%m-%d-%y")_assembly_summary.txt

# NEW_ASSEMBLY=genomes_list/$(date +"%m-%d-%y")_assembly_summary.txt
# sed -i "3 c\\assembly_file: ${NEW_ASSEMBLY}" profile/python_params.txt

# Generate bash scripts
# echo "Generate bash scripts" 
# find scripts/bash_jobs/ -type f -exec rm -rf {} \;

# python scripts/python/split_genome_for_crisprdetect.py
# python scripts/python/split_genome_for_ftp_download.py
# python scripts/python/split_genome_for_gunzip.py

# Running the pipeline
echo "Launching Snakemake" 
module load StdEnv/2020  intel/2020.1.217 
source DB_UPDATE/bin/activate

snakemake --unlock
snakemake -pk --profile profile --rerun-incomplete &> logs/snakemake_$(date +"%m-%d-%y").log
