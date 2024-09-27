import sys, os, re, glob, time
import shutil
from Bio import Entrez
import argparse
import sqlite3
import configparser

class CrisprOpenDB:
    def __init__(self, db_file = "CrisprOpenDB.sqlite"):
        self.db_file = db_file
        self._connection = sqlite3.connect(db_file)
        self._cursor = self._connection.cursor()


    def update_organism_table(self, in_file):
        with open(in_file, 'r') as f_in:
            for line in f_in.readlines():
                line = line.strip()
                info =line.split(',')

                if len(info) == 8:    
                    species = info[0]
                    genus= info [1]
                    torder= info[2]
                    family=info[3]
                    organism_name = info[4]
                    assembly_accession = info[5]
                    genebank_id = info[6]  
                    taxid = info[7]             
                    
                    try:
                        self._cursor.execute(f"""INSERT INTO ORGANISM (SPECIES, GENUS, TORDER, FAMILY, ORGANISM_NAME, ASSEMBLY_ACCESSION, GENEBANK_ID ) values ('{species}','{genus}','{torder}','{family}','{organism_name}','{assembly_accession}','{genebank_id}')
                                        EXCEPT select SPECIES, GENUS, TORDER, FAMILY, ORGANISM_NAME, ASSEMBLY_ACCESSION, GENEBANK_ID from ORGANISM where GENEBANK_ID='{genebank_id}';""")
                    except Exception as e:
                      print(e)
                
                else:
                    with open("Error_taxonomy.txt", "a") as ferror:
                        print(f"Missing taxonomy info for: {info}")
                        ferror.write(info)
                                
                self._connection.commit()
                        
    def count_number_of_organisme(self):
        self._cursor.execute("select count(GENEBANK_ID) from ORGANISM")
        return(self._cursor.fetchall()[0])

        

                
if __name__ == "__main__":

    # reading the parameter file
    config = configparser.RawConfigParser()
    config.read('profile/python_params.txt')

    DB_FILE = config.get('GENERAL', 'database_path')
    INPUT_PATH = config.get('UPDATE_SPACER_TABLE', 'input_path')
    OUTPUT_PATH = config.get('UPDATE_SPACER_TABLE', 'output_path')


    test = CrisprOpenDB()
    number_organism = test.count_number_of_organisme()
    print("Notre DB contient {} bactéries".format(number_organism))

    file_list = glob.glob(os.path.join(INPUT_PATH , "*.tsv"))
    count = 0
    for f in file_list:
        count += 1
        print("WE ARE OPENING ",f,"the ",count," file\n")
        test.update_organism_table(f)

        # Move spacer file to archive after updating table
        f_tail = os.path.split(f)[-1]
        shutil.move(f, OUTPUT_PATH+"/"+f_tail)



    number_organism = test.count_number_of_organisme()
    print("Notre DB contient {} bactéries".format(number_organism))
    
