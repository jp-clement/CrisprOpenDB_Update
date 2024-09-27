import os, glob

OUT_PATH = 'output/spacers/'
IN_PATH = 'scripts/bash_jobs/ncbi_download/'
FLAGS_PATH= 'logs/completion_flags/'
spacer_files = os.listdir(OUT_PATH)
dll_files = os.listdir(IN_PATH)
flags = os.listdir(FLAGS_PATH)
completed = []
missing = []
flag_num = []
files_removed = []
completed_counter = 0

# Get batch numbers of spacer file
for f in spacer_files:
    if "spacers_" in f: 
        f = f.split("spacers_")[1]
        f=f.replace('.tsv', '')
        completed.append(f)

# Get batch numbers of completion flags
for f in flags:
    batch_num = f.split("_")[-1]
    batch_num = batch_num.replace(".txt", "")

    if batch_num.isnumeric():
        flag_num.append(batch_num)
flag_num= set(flag_num)

# Remove completion flags that don't have a matching spacer file

for batch_num in flag_num:
    if batch_num not in completed:
        for f in glob.glob(FLAGS_PATH+"*_"+batch_num + ".txt"):
            files_removed.append(f)
            os.remove(f)
    
for f in dll_files:
    if "ncbi_download_" in f: 
        batch_num = f.split("ncbi_download_")[1]
        batch_num =batch_num.replace('.sh', '')

        if batch_num not in completed:
            missing.append(f)

print(f'{len(completed)} batches were completed.')
print(f'{len(files_removed)} flag files were erased.')
print(f'{len(missing)} batches are still missing.')

with open('logs/clean_flags.log', 'a') as log:
    for file in files_removed:
        log.write(file)
        log.write('\n')

# print('Batches missing:')
# for f in missing:
#     print(f)

