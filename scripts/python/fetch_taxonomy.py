import sys, os, re, glob, time
import shutil
from Bio import Entrez
import argparse

Entrez.email = "jean-pierre.clement@iid.ulaval.ca"
Entrez.api_key = "63cc72c74f8c086af84f5b5ca5ad88c57e09"


class db_entry:
    def __init__(self, accession):
        self.gb_id = ""
        self.accession = accession
        self.acc_version = accession.split(".")[0]
        self.taxid =""
        self.species =  ""
        self.genus =  ""
        self.order =  ""
        self.family =  ""
        self.organism_name =  ""
        self.error = False

    def missing_info(self):
        for info in [self.species, self.genus, self.order, self.family, self.organism_name, self.accession]:
            if info =="":
                return True            
        return False

    def get_values(self):
        return [self.species, self.genus, self.order, self.family, self.organism_name, self.accession]
    
    def get_taxid(self):
        return self.taxid
    
def ncbi_efetch(accession, retry=0, max_retry=7):
    try:
        fetch_handle = Entrez.efetch( db="nucleotide",  retmode="gb", id = accession) 
        info = fetch_handle.readlines()
        fetch_handle.close()
    except:
        if retry == max_retry:
            print("NCBI_efect max retries reached!")
            with open("Error_taxonomy.txt", "a") as ferror:
                for acc in accession:
                    ferror.write(f'accession # : {acc}')
                    ferror.write('\n')
            return None
        else:
            ncbi_efetch(accession, retry=retry + 1)
    
    return info

def efetch_parser(gb_info):
    ''' The efetch(rettype = gb) is fastest option to download efetch data
    but requires a text parser, not the most robust, but at least it is efficient'''
    entries = []
    #  Break down by entries
    for line in gb_info:
        if line.startswith('Seq-entry'):
            entries.append([])
        entries[-1].append(line)

    taxnames =[]
    taxids = []
    accs =[]
    # Parse info for each entries
    for entry in entries:    
        name = ''
        id = ''
        acc = '' 
        for n, line in enumerate(reversed(entry)):
            idx = len(entry) - n
            if 'taxname' in line:
                name = line.split('\"')[1]

            elif "db \"taxon\"" in line:
                id = entry[idx].split('tag id ')[1].strip()

            if 'accession ' in line :
                acc = line.split('\"')[1].strip()

        taxnames.append(name)
        accs.append(acc)
        taxids.append(id)

    return accs, taxnames, taxids

def fetch_taxonomy_info(taxids, retry=0, max_retry=7):
    try:
        handle = Entrez.efetch(db="Taxonomy", id=set(taxids), retmode="xml")
        taxonomies = Entrez.read(handle)
        handle.close()
    except Exception as e:
        if retry == max_retry:
            print(f"fetch_taxonomy_info max retries reached!")
            with open("Error_taxonomy.txt", "a") as ferror:
                for taxid in taxids:
                    ferror.write(f'taxid # : {taxid}')
                    ferror.write('\n')
            return None
        else:
            fetch_taxonomy_info(taxids, retry=retry + 1)

    return taxonomies


def parse_taxonomy_info(taxonomies, querry):
    # make quick access for taxonomy info
    tax_dict ={}
    for rec in taxonomies:
        tax_dict[rec['TaxId']] = rec

    for acc in querry.keys():
        # print(acc)
        tax_id = querry[acc].get_taxid()

        if tax_id in tax_dict:

            rec = tax_dict[tax_id]
            # querry[acc].organism_name = rec['ScientificName']

            for items in rec["LineageEx"]:
                if items["Rank"] == "species":
                    querry[acc].species = items["ScientificName"]
                elif items["Rank"] == "genus":
                    querry[acc].genus = items["ScientificName"]
                elif items["Rank"] == "order":
                    querry[acc].order = items["ScientificName"]
                elif items["Rank"] == "family":
                    querry[acc].family = items["ScientificName"]

            # Manage the case when taxonomy type is other than strain -- assumes it is species then
                if rec['Rank'] == 'species':
                    querry[acc].species = rec['ScientificName']

    return

def fetch_NCBI_info(genebank_ids):
    querry = {}
    for id in genebank_ids:
        acc = id.split('.')[0]
        querry[acc] = db_entry(acc)


    # Get info from nucleotide DB
    info = ncbi_efetch(accession = querry.keys()) 
    if info == None:
        return None    
    accs, taxnames, taxids = efetch_parser(gb_info = info)

    for acc, taxname, taxid in list(zip(accs, taxnames, taxids)): 
        if acc in querry.keys():
            querry[acc].taxid = taxid
            querry[acc].organism_name = taxname

    # Get info from ncbi taxonomy DB
    taxonomies = fetch_taxonomy_info(taxids = taxids)
    parse_taxonomy_info(taxonomies, querry)

    return querry         

#####################################

def ncbi_batch_fetching(accession_list, output_file, batch_size = 199):
    if len(accession_list)> 0:               
        for i in range(0, len(accession_list), batch_size):
            print(time.strftime("%Y-%m-%d %H:%M", time.localtime()))
            print(f"Fetching taxonomy info for batch {i} to {i+batch_size}")

            genebank_ids = accession_list[i:i+batch_size] 

            try:
                querry = fetch_NCBI_info(genebank_ids = genebank_ids)
                if not querry:
                    raise Exception("Error : fetch_NCBI_info() did not return any information")
                
            except Exception as e:
                print(e)
                print(f" Couldn't fetch the ncbi information for {genebank_ids}")
                continue
                
            # Update ORGANISM DB
            db_input_list = []
            for id in genebank_ids:
                id_accession_num = id.split('.')[0]

                if id_accession_num in querry:

                    db_input_list.append(querry[id_accession_num].get_values()  + [id] + [querry[id_accession_num].get_taxid()])
                else:
                    with open("Error_taxonomy.txt", "a") as ferror:
                        print("Missing taxonomy info for: {}".format(id))
                        ferror.write([id])

                
            with open(output_file, 'a') as f:
                for line in db_input_list:
                    f.write('\t'.join(line))
                    f.write('\n')            

def ExtractAccessionNumbers(inFile):
    accession_list = []
    with open(inFile, 'r') as fl:
        for line in fl:
            array = line.strip().split('\t')          
            if array[2] == 'binding_site':

                accession_list.append(array[0])
    return list(set(accession_list))


                
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to fetch taxonomy data from a CrisprDetect output file",  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", help="Path to input crisprDetect tsv file where genebank ids are stored as the first column")
    parser.add_argument("-o", "--output",help="Path to output file containing taxonomy info for all genebank ids")

     # -i "output\spacers\spacers_11.tsv" -o"output/taxonomy/taxonomy_11.tsv"

    args = vars(parser.parse_args())
    IN_FILE = args['input']
    OUTPUT_FILE = args['output']
     
    accession_list = ExtractAccessionNumbers(IN_FILE)
    ncbi_batch_fetching(accession_list = accession_list, output_file= OUTPUT_FILE)

    

