import sqlite3
import configparser
# reading the parameter file
config = configparser.RawConfigParser()
config.read('profile/python_params.txt')

ASSEMBLY = config.get('GENERAL', 'assembly_file')
ALLOC = config.get('GENERAL', 'alloc')
DB_FILE = config.get('FILTER_ASSEMBLIES', 'database_path')

def filter_genomes_list(db_file, genome_file):
    output_file = genome_file.split('.txt')[0] +"_filtered.txt"    

    print("Filtering out genomes already present in database...")
    _connection = sqlite3.connect(db_file)
    cursor = _connection.cursor()
    cursor.execute("select distinct ASSEMBLY_ACCESSION from ORGANISM")
    org_id = [i[0] for i in cursor.fetchall()]
    cursor.close()
    print(f"{len(org_id)} assemblies are already present in database.")

    org_id = set(org_id)
    header =[]
    new_genome_list = []
    with open(ASSEMBLY,'r', encoding="utf8") as f:
        header.append(f.readline())
        header.append(f.readline())        
        for line in f:
            line = line.strip().split('\t')
            if line[0] not in org_id:
                new_genome_list.append(line)

    with open(output_file, 'w') as f:
        for line in header:
            f.write(line)
        for line in new_genome_list:
            line = '\t'.join(line) 
            f.write(line+"\n")  

    print(f"New assemblies saved to {output_file}")

filter_genomes_list(DB_FILE, ASSEMBLY)