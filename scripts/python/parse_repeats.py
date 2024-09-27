import  os, re, glob, sys

              
if __name__ == "__main__":
    print('EXTRACTING SPACERS FROM FILES')
    slurm_tmpdir = os.getenv('SLURM_TMPDIR')+"/"
    output_path = 'output/spacers'

    if len(sys.argv) >1:
        batch_number = sys.argv[1]
    else:
        sys.exit("Error: Did not specify batch number. Exiting.")

    file_list = glob.glob(os.path.join(slurm_tmpdir, "*.gff"))
    print(len(file_list))
    count = 0

    with open(f'{output_path}/spacers_{batch_number}.tsv' , 'w') as f_out:       
        for f in file_list:
            if os.path.isfile(f):
                with open(f, 'r') as f_in:
                    for line in f_in:
                        f_out.write(line)           
            else:
                print('File missing:'+ f)

    print("Merging of spacer files completed.")
    



