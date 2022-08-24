'''
The purpose of this file is to format mappings that can be used for the CaseOLAP scoring.
The mappings are the outputs: 
- pmid2pcount_path: {'PMID':{'Entity':'Hits',...},...}
- category2pmids_path: {'Category1': ['PMID_1',...,'PMID_n' ], ...}

Starting with the textcube provided PMIDs in each category, this produces mappings of 
PMIDs in each category only if those PMIDs were found to contain entities of interest.
'''
import json
from caseolap._11_metadata_update import *


'''
Parameters
'''
# Input file paths
entitycount_path = 'data/entitycount.txt'              # PMID Entity|Count ...
pmid2category_path = 'data/textcube_pmid2category.json'# PMIDs of interest to category
category_names_file = './config/textcube_config.json'  # Category names


# Output file paths
outfile_pmid2entity2count = 'data/metadata_pmid2entity2count.json' # {PMID:{Entity:Count,...},...}
cat2pmids_path = 'data/metadata_category2pmids.json'   # {CatName:[PMID,...], ...}
logfile_path = './log/metadata_update_log.txt'         # Similar to pmid2pcount


'''
Main Code
'''
if __name__ == '__main__':
    # Open log file
    logfile = open(logfile_path, 'w') 

    # Get category names
    category_names = json.load(open(category_names_file,'r'))

    # Initialize class
    MU = MetadataUpdate(category_names) 
    
    # Rewrite PMID->Entity->Entity Count as a nested dictionary
    MU.update_pmid2entity2count(entitycount_path, outfile_pmid2entity2count, logfile)    

    # Category->PMID (PMIDs in which queried entities were discovered)
    MU.map_category2pmid_pmids_with_entities(pmid2category_path, cat2pmids_path, logfile) 
    
    # Close log file
    logfile.close()
    
    