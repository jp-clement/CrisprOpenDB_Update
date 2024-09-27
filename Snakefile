#!/usr/bin/python

# Run this command to lunch the pipeline
# source DB_UPDATE/bin/activate ; snakemake --unlock ; snakemake -pk --profile profile --rerun-incomplete

# Clean flags here

path_to_cripsrDetect = "/home/jpcle8/projects/rrg-eroussea/jpcle8/MAJ_CrisprOpenDB/CRISPRDetect"

import os
files = os.listdir("scripts/bash_jobs/ncbi_download")
batches = []
for file in files:
    if ".sh" in file:
        s = file.split(".sh")[0]
        s = s.split("_")[-1]
        batches.append(s)

rule all:
  input: 
    expand("logs/completion_flags/completed_taxonomy_{batch}.txt",  batch = batches)
    
  log:

      "logs/all.log"
  shell: 
    """

      python scripts/python/update_spacer_table.py
      python scripts/python/update_organism_table.py

      echo Done! 
     """

rule download:
    input:
        "scripts/bash_jobs/ncbi_download/ncbi_download_{batch}.sh"
    output:
       "logs/completion_flags/completed_download_batch_{batch}.txt"
    group:
      'batch_group'
    log:
      'logs/download/download_{batch}.log'
    shell:
        """
        parallel --jobs 32 < {input} &> {log} || true

        touch {output}
        """

rule unzip:
  input:
    'logs/completion_flags/completed_download_batch_{batch}.txt'
  output:
    'logs/completion_flags/completed_unzip_batch_{batch}.txt'
  group:
    'batch_group'
  log:
      'logs/unzip/unzip_{batch}.log'
  threads: 32
  shell:
    """
        parallel --jobs 32 < scripts/bash_jobs/unzip/ncbi_gunzip_{wildcards.batch}.sh &> {log} || true

        touch {output}
    """

rule criprDetect:
  input:
    "logs/completion_flags/completed_unzip_batch_{batch}.txt"
  output:
    "logs/completion_flags/completed_crisprDetect_batch_{batch}.txt"

  group:
    "batch_group"
  log:
      "logs/crisprD/crisprD_{batch}.log"
  threads: 32     
  shell:
    """
    module load viennarna/2.5.1
    module load cd-hit/4.8.1
    module load StdEnv/2020
    module load gcc/9.3.0
    module load blast+/2.13.0
    module load emboss/6.6.0

    parallel --jobs 32 < scripts/bash_jobs/crisprDetect/ncbi_crisprDetect_{wildcards.batch}.sh > {log} || true

    touch {output}
    """
 



rule saveSpacers:
  input:
    "logs/completion_flags/completed_crisprDetect_batch_{batch}.txt"
  output:
    "logs/completion_flags/completed_saveSpacers_{batch}.tsv"

  group:
    "batch_group"
  log:
      "logs/saveSpacers/spacers_{batch}.log"
  threads: 1    
  shell:
    """
    module load StdEnv/2020 

    python scripts/python/parse_repeats.py {wildcards.batch} >> {log} 1>&2 || true

    touch {output}
    """



rule fetch_taxonomy:
  input:

    "logs/completion_flags/completed_saveSpacers_{batch}.tsv"
  output:
    "logs/completion_flags/completed_taxonomy_{batch}.txt"
  log:
      "logs/saveSpacers/spacers_{batch}.log"
  threads: 1    
  shell:
    """
    module load StdEnv/2020 
    source DB_UPDATE/bin/activate

    python scripts/python/fetch_taxonomy.py --input output/spacers/spacers_{wildcards.batch}.tsv --output output/taxonomy/taxonomy_{wildcards.batch}.tsv >> {log} 1>&2

    touch {output}
    """
