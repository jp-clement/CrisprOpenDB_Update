import sys, os, re, glob, time
import shutil
from Bio import Entrez
import argparse
import sqlite3
import configparser

class CrisprOpenDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self._connection = sqlite3.connect(db_file)
        self._cursor = self._connection.cursor()

    def ExtractSpacers(self, inFile):
        with open(inFile, 'r') as fl:
            locus_count = 0
            accession = ""
            for line in fl:
                array = line.strip().split('\t')
                if array[2] == 'repeat_region':
                    locus_count += 1
                    spacer_count = 0
                    if array[0] != accession:                   
                        accession = array[0]

                if array[2] == 'binding_site':
                    #unique_spacer_id = 
                    spacer_count += 1
                    start_position= int(array[3])
                    end_position= int(array[4])
                    size= int(array[5])
                    orientation = array[6]
                    sArray = array[8].split(';')
                    for it in sArray:
                        if re.match('Note=', it):
                            sequence = it[5:]
                    yield([locus_count, spacer_count, start_position, end_position, size, orientation, sequence, accession])


    def insert_information(self, spacer, start, end, spacer_length, strand, genebank, pos_locus, num_locus):
        spacer_id = genebank + "_" + str(num_locus) + "_" + str(pos_locus) #We could use UUID instead.
        self._cursor.execute("insert into SPACER_TABLE values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (spacer_id, spacer, start, end, spacer_length, strand, pos_locus, num_locus, genebank))
        self._connection.commit()
        return spacer_id
    
    def fill_tables(self, in_file):
        for spacer in self.ExtractSpacers(in_file):
            if spacer[0] == -1:
                with open("DB_Creation_errors", 'a') as fo:
                    fo.write(in_file + "\t" + spacer[1]+"\n")
                break
            # (spacer, start, end, spacer_length, strand, genebank, pos_locus, num_locus)
            self.insert_information(spacer[6], spacer[2], spacer[3], spacer[4], spacer[5], spacer[7], spacer[1], spacer[0])
        return

    def count_number_of_spacers(self):
        self._cursor.execute("select count(SPACER) from SPACER_TABLE")
        return(self._cursor.fetchall()[0])

        

                
if __name__ == "__main__":

    # reading the parameter file
    config = configparser.RawConfigParser()
    config.read('profile/python_params.txt')

    DB_FILE = config.get('GENERAL', 'database_path')
    INPUT_PATH = config.get('UPDATE_SPACER_TABLE', 'input_path')
    OUTPUT_PATH = config.get('UPDATE_SPACER_TABLE', 'output_path')


    test = CrisprOpenDB(db_file = DB_FILE)
    number_spacers = test.count_number_of_spacers()
    print("Notre DB contient {} spacers".format(number_spacers))

    file_list = glob.glob(os.path.join(INPUT_PATH , "*.tsv"))
    count = 0
    for f in file_list:
        count += 1
        print("WE ARE OPENING ",f,"the ",count," file\n")
        test.fill_tables(in_file)

        # Move spacer file to archive after updating table
        f_tail = os.path.split(f)[-1]
        shutil.move(f, OUTPUT_PATH+"/"+f_tail)



    number_spacers = test.count_number_of_spacers()
    print("Notre DB contient {} spacers".format(number_spacers))
    
