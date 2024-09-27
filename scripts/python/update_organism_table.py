import sys, os, re, glob, time
import shutil
from Bio import Entrez
import argparse
import sqlite3
import configparser

class CrisprOpenDB:
    def __init__(self, db_file ):
        self.db_file = db_file
        self._connection = sqlite3.connect(db_file)
        self._cursor = self._connection.cursor()


    def update_organism_table(self, in_file):
        self._cursor.execute("select distinct GENEBANK_ID from ORGANISM")
        query_results = set([i[0] for i in self._cursor.fetchall()])

        db_input_list =[]
        with open(f, 'r') as f_in:
            for line in f_in.readlines():
                line = line.strip()
                info =line.split('\t')

                if len(info) == 8:
                    taxid = info.pop(7)
                    accession = info.pop(5)

                    if info[5] not in query_results    :            
                        db_input_list.append(info)

                else:
                    try:
                        if info[-2] not in query_results    :            
                            db_input_list.append([info[0], info[1], info[2], info[3], info[4], info[-2]])

                    except Exception as e:
                        print(e)
                    
                        with open("Error_taxonomy.txt", "a") as ferror:
                            print(f"Missing taxonomy info for: {info}")
                            ferror.write(str(info))
        try:
            self._cursor.executemany("""INSERT OR IGNORE INTO ORGANISM (SPECIES, GENUS, TORDER, FAMILY, ORGANISM_NAME, GENEBANK_ID ) values (?, ?, ?, ?, ?, ? )
                                        """,
                        db_input_list)
        except Exception as e:
            print(e)
                    
        self._connection.commit()
                        
    def count_number_of_organisme(self):
        self._cursor.execute("select count(GENEBANK_ID) from ORGANISM")
        return(self._cursor.fetchall()[0])

        

                
if __name__ == "__main__":

    # reading the parameter file
    config = configparser.RawConfigParser()
    config.read('profile/python_params.txt')

    DB_FILE = config.get('GENERAL', 'database_path')
    INPUT_PATH = config.get('UPDATE_ORGANISM_TABLE', 'input_path')
    OUTPUT_PATH = config.get('UPDATE_ORGANISM_TABLE', 'output_path')


    test = CrisprOpenDB(db_file= DB_FILE)
    number_organism = test.count_number_of_organisme()
    print("Notre DB contient {} bactéries".format(number_organism))
    #test.create_tables(True) 

    file_list = glob.glob(os.path.join(input_dir, "*.tsv"))
    count = 0
    for f in file_list:
        count += 1
        print("WE ARE OPENING ",f,"the ",count," file\n")
        test.update_organism_table(f)


        # Move ORGANISM file to archive after updating table
        f_tail = os.path.split(f)[-1]
        shutil.move(f, output_dir+"/"+f_tail)


    number_organism = test.count_number_of_organisme()
    print("Notre DB contient {} bactéries".format(number_organism))
    

