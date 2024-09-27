import sys, glob, os, datetime, configparser
# reading the parameter file
config = configparser.RawConfigParser()
config.read('profile/python_params.txt')

ASSEMBLY = config.get('GENERAL', 'alignment_file')
ALLOC = config.get('GENERAL', 'alloc')
FILES_PER_BATCH = int(config.get('GENERAL', 'files_per_batch'))
EXEC_PATH = config.get('CRISPR_DETECT', 'crisprDetect_exec_path')
INPUT_PATH = config.get('CRISPR_DETECT', 'input_path')
OUTPUT_PATH = config.get('CRISPR_DETECT', 'output_path')

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

def split_crisprDetect_job(all_ftp_list, number_of_ftp_per_file):

    seq_count = 0
    file_count = 0
    bundle = []

    f = 'ncbi_crisprDetect_' + str(file_count)    
    separated_job = open('scripts/bash_jobs/crisprDetect/' + f + '.sh', 'w')
    separated_job.write('#!/bin/bash\n')
 
    # separated_job.write('source ~/DB_UPDATE/bin/activate\n\n')

    for ftp in all_ftp_list:
        address = ''.join(ftp.split(':')[1:])
        fasta = ''.join(ftp.split('/')[-1])
        ftp = fasta + '_genomic.fna'
        # separated_job.write('perl '+ EXEC_PATH + 'CRISPRDetect.pl -f ' + INPUT_PATH + ftp + ' -o ' + OUTPUT_PATH + ftp + '.cd -T 1 -array_quality_score_cutoff 3 \n')

        # separated_job.write('perl '+ EXEC_PATH + 'CRISPRDetect.pl -f ' + INPUT_PATH + ftp + ' -o ' + OUTPUT_PATH + ftp + '.cd -T 1 -array_quality_score_cutoff 3 || ')
        # separated_job.write('perl '+ EXEC_PATH + 'CRISPRDetect.pl -f ' + INPUT_PATH + ftp + ' -o ' + OUTPUT_PATH + ftp + '.cd -tmp_dir ${SLURM_TMPDIR} -T 1 -array_quality_score_cutoff 3 || ')
        # separated_job.write('echo \"Failed : '  + ftp + '\"\n')
        
        separated_job.write('perl '+ EXEC_PATH + 'CRISPRDetect.pl -f ' + INPUT_PATH + ftp + ' -o ' + OUTPUT_PATH + ftp + '.cd -tmp_dir ${SLURM_TMPDIR} -T 1 -q 1 -array_quality_score_cutoff 3 \n')
        seq_count += 1 

        if seq_count == number_of_ftp_per_file :
            separated_job.close()

            file_count += 1
            seq_count = 0

            f = 'ncbi_crisprDetect_' + str(file_count)    
            separated_job = open('scripts/bash_jobs/crisprDetect/' + f + '.sh', 'w')
            separated_job.write('#!/bin/bash\n')
    separated_job.close()


# unzip 10000 files in one job
split_crisprDetect_job(new_genome_list, FILES_PER_BATCH )
