#!/bin/bash
#########################################
#####   How to install CrisprDetect #####
#########################################


####################################
#####   Download Dependencies  #####
####################################
cpan Parallel::ForkManager

wget http://www.clustal.org/download/current/clustalw-2.1-linux-x86_64-libcppstatic.tar.gz
tar xvzf clustalw-2.1-linux-x86_64-libcppstatic.tar.gz
mv clustalw-2.1-linux-x86_64-libcppstatic/clustalw2 /home/${USER}/bin/clustalw 



####################################
#####  Download Crispr Detect  #####
####################################
# git clone https://github.com/ambarishbiswas/CRISPRDetect_2.2.git

#### Need to add this bit of text between line 28 "our $tmp_dir="$cd_path/tmp";" and line 29 "my $no_of_threads=4;" of CRISPRDtect.pl 

######### Added the little section below to handle the command line -tmp_dir option properly. (plpla) #########
# for(my $i=0;$i<=$#ARGV;$i++){
#         if($ARGV[$i]=~/-tmp_dir/){
#                 $tmp_dir=$ARGV[$i+1];
#                 if(not -e $tmp_dir){
#                         print "\nError: The specified directory: $tmp_dir not found. User should create the directory, and give read and write permission to perl and its dependent tools. Best to use the default '/tmp' directory.\n\n";exit;
#                 }        
#         }
# }


####################################
#####        Run example       #####
####################################

module load emboss/6.6.0
module load viennarna/2.5.1
module load cd-hit/4.8.1
module load StdEnv/2020
module load gcc/9.3.0
module load blast+/2.13.0

perl CRISPRDetect.pl -f test_multifasta.fa -o test_CRISPRDetect -check_direction 0 -array_quality_score_cutoff  3 -T 1