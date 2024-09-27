import sys, datetime, configparser

# reading the parameters file
config = configparser.RawConfigParser()
# config_config = configparser.ConfigParser()
config.read('profile/python_params.txt')
# print(config_config.sections())

ASSEMBLY = config.get('GENERAL', 'alignment_file')
ALLOC = config.get('GENERAL', 'alloc')
FILES_PER_BATCH = int(config.get('GENERAL', 'files_per_batch'))
OUTPUT_PATH = config.get('DOWNLOAD', 'output_path')


# reading the assembly file
new_genome_list = []
with open(ASSEMBLY,'r') as f:
    next(f)
    next(f)
    for line in f:
        line = line.strip().split('\t')
        for i in line :
            if i.startswith('https://ftp') :
                new_genome_list.append(i)

# print()
# split files to download into different jobs to limit the number of files to download in one job
# and generate scripts
def split_ftp_download_job(all_ftp_list, number_of_ftp_per_file):

    seq_count = 0
    file_count = 0
    bundle = []

    f = 'ncbi_download_'  + str(file_count)
    separated_job = open('scripts/bash_jobs/ncbi_download/' + f + '.sh', 'w')
    separated_job.write('#!/bin/bash\n')

    for ftp in all_ftp_list:
        address = ''.join(ftp.split(':')[1:])
        fasta = ''.join(ftp.split('/')[-1])
        ftp = 'https:' + str(address) + '/' + fasta + '_genomic.fna.gz'
        separated_job.write(f"curl {ftp} -o {OUTPUT_PATH}{fasta}_genomic.fna.gz || echo \'{ftp}\'\n")
        seq_count += 1

        if seq_count == number_of_ftp_per_file :
            separated_job.close()

            file_count += 1
            seq_count = 0

            f = 'ncbi_download_'  + str(file_count)
            separated_job = open('scripts/bash_jobs/ncbi_download/' + f + '.sh', 'w')
            separated_job.write('#!/bin/bash\n')

    separated_job.close()

# download 10000 genomes in one job
split_ftp_download_job(new_genome_list, FILES_PER_BATCH ) # 10001
