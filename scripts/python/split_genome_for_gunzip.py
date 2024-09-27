import sys, datetime, configparser

# reading the parameter file
config = configparser.RawConfigParser()
config.read('profile/python_params.txt')

ASSEMBLY = config.get('GENERAL', 'alignment_file')
ALLOC = config.get('GENERAL', 'alloc')
FILES_PER_BATCH = int(config.get('GENERAL', 'files_per_batch'))
INPUT_PATH = config.get('UNZIP', 'input_path')

# reading the assembly file
new_genome_list = []
with open(ASSEMBLY,'r', encoding="utf8") as f:
    next(f)
    next(f)
    for line in f:
        line = line.strip().split('\t')
        for i in line :
            if i.startswith('https://ftp') :
                new_genome_list.append(i)

# print(len(new_genome_list))

# split files to unzip into different jobs to limit the number of files to unzip in one job
# and generates scripts
def split_ftp_download_job(all_ftp_list, number_of_ftp_per_file):

    seq_count = 0
    file_count = 0
    bundle = []

    f = 'ncbi_gunzip_'  + str(file_count)
    separated_job = open('scripts/bash_jobs/unzip/' + f + '.sh', 'w')
    separated_job.write('#!/bin/bash\n')


    for ftp in all_ftp_list:
        address = ''.join(ftp.split(':')[1:]) 
        fasta = ''.join(ftp.split('/')[-1])
        ftp = fasta + '_genomic.fna.gz'
        # separated_job.write('gunzip ' + INPUT_PATH  + ftp + '\n')

        separated_job.write('gunzip ' + INPUT_PATH  + ftp + ' || ')
        separated_job.write('echo \"Failed : '  + ftp + '\"\n')
        seq_count += 1 

        if seq_count == number_of_ftp_per_file :
            separated_job.close()

            file_count += 1
            seq_count = 0

            f = 'ncbi_gunzip_'  + str(file_count)
            separated_job = open('scripts/bash_jobs/unzip/' + f + '.sh', 'w')
            separated_job.write('#!/bin/bash\n')
            
    separated_job.close()
# unzip 10000 files in one job
split_ftp_download_job(new_genome_list, FILES_PER_BATCH)
