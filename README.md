# Improved-CaseOLAP-PD
 CaseOLAP with improved entity name filtering, more readable code, and easier to re-run. 
 
The name filtering is a way to semi-automatically filter the queried synonyms to improve search results. When you search for an entity in the text documents (i.e. publications), you use the entities' names (i.e. synonyms). If the publication's text matches a name of an entity, that counts as a hit for that entity. However, some provided names are too ambiguous; many acronyms refer to things other than proteins such as diseases, surgical procedures, programs, and more (e.g., ALS could be a protein or a disease, PC2 can be a protein or Principal Component 2 from a Principal Component Analysis). To improve this situation, this version of CaseOLAP will find all short synonyms (i.e. <=3 letters, <=2 characters) and synonyms that are English words (i.e. synonyms that are found in an English dictionary and thus are likely to have alernate meanings). The user can then go through these synonyms and decide if they should be included in the query (the user may rely on human knowledge or search for the terms in PubMed and see what they typically refer to). CaseOLAP will then only  use the synonyms that the user did not disapproved. This improves search results and makes CaseOLAP scores better by reducing very false false positives although increasing some false negatives. 

The code is more readable now due to increased comments or making code more concise or Pythonic in some areas. The results are more interpretable because the top ranked entities are displayed along with their synonyms and hits (results/ranked entities), plus the top ranked synonyms of the entities and their hits are displayed (results/ranked synonyms) for each category and the total.
 
The code is easier to run because of some other changes to the order of how the code is run, the 'behind-the-scenes' of the entity count process, and other changes to the how the algorithm in run while preserving the same end result of a CaseOLAP score. There are new files which include the aforementioned features. 

 Note: Like the other recent uses of CaseOLAP in the biomedical domain, this  uses Popularity (P) and Distinctiveness (D), not integrity. Because the entities are determined by a knowledge base, not by a phrase-mining program such as SegPhrase or AutoPhrase, the integrity score would always be 1. Thus, here the CaseOLAP score is calculate with P+D (result/caseolap.csv), P (result/popularity_score.csv), and D (distinctiveness_score.csv). 

 
 # CaseOLAP :

CaseOLAP is a cloud computing platform for phrase-mining. specifically, for user-defined entity-category association. It has five major steps; 'downloading', 'parsing', 'indexing', 'entity count' and 'CaseOLAP score calculation'. There are mltiple steps in a single major step, which are based on user's interest in entity list and categories as well as data set being used. This pipeline describes these major steps for PubMed abstracts as text data, the mitochondrial proteins as entity list, and MeSH descriptors attached to abstracts as categories.


***0. Setting up Python Environment*** : 

Install Anconda python and git in the Unix system. Create the 'caseolap' python environment.

```
conda env create -f environment.yaml
```
### Follow instructions in the runner. The runner is the main file that runs the other scripts. However,
you will need to modify some of the input files for those scripts. 

## Server-Wide Steps
Steps 1-5 should be performed once and is used globally, across the whole server. 
The later steps should be customized for each project (if you're doing multiple projects)

---------------------------

***1. Download Documents*** : 

Set up the FTP data address at 'config/ftp_config.json' and select 'baseline' and/or 'updatefiles' in 'config/download_config.json'. This will download the data file from source to the cloud storage, check the integrity of download data, and extract them.

Run this to download the PubMed publications in bulk.
```
python 01_run_download.py
```
-------------------------------

***2. Parsing Documents*** : 
Set up the parameters for parsing at 'config/parsing_config.json'. Based on the items selected. Parsed data for each document becomes available as JSON dictionary.

Parse the downloaded documents so that the desired fields (e.g., title, abstract) in each publication are stored into a JSON.
```
python 02_run_parsing.py
```
---------------------------

***3. MeSH to PMID Mapping***

PubMed articles have MeSH term metadata, i.e. a section detailing the MeSH terms of the publication's topics. 
This maps all MeSH terms to publications that are reported to study those terms and vice verse (i.e. MeSH to PMID, PMID to MeSH)

```
python 03_run_mesh2pmid_mapping.py

```
---------------------------

***4, 5. Document Indexing***
Create a Elasticsearch indexing database for parsed documents. To initiate the index select the 
parameters in 'config/indrx_init.json' and to populate the index, select parameters at 
'config/index_populate.json'. Make sure ElasticSearch is running:
!nohup elasticsearch-6.5.4/bin/elasticsearch > search.txt
Note: This version of CaseOLAP indexes the text in a case-sensitive manner. This is important because
when the text is lowercased, queries for a protein abbreviated "ON" will count all mentions of "on"
as that protein, ruining results of your top-scoring entities. 


```
python 04_run_index_init.py
python 05_run_populate_init.py
```


## Project-Specific Steps
These steps should be customized for the project. This is where you will need to change some of the
input files for your study (e.g., choose publication categories of interest, choose entities of 
interest to query).

---------------------------

***6. Text-Cube Creation***

 The user should provide the categories of publications they want to study. These categories are
 MeSH tree numbers (e.g., "C14.280.647 C14.907.585" for myocardial ischemia). All descendant MeSH
 tree numbers will be used as well (the pipeline will do this for you) so that the categories' 
 sub-categories will be included in the same category. The publications belonging to this category
 will be stored in their own part of the textcube, i.e. will be categorized together.
 
 Input your categories' root tree numbers at 'input/categories.txt'. 
 
```
python 06_run_textcube.py
```

---------------------------

***7. Case-vary the synonyms***
Before this step, you must provide a file in 'input/entities.txt'. The file should contain all the
entities you want to search for in the publications. Each row should have an entity's main name/ID
and then an optional list of the entity's synonyms because the same entity may be referred to in 
publications by different names/synonyms. The rows should be |-deliminted 
(e.g., 'Entity_ID|synonym1|synonym two| syn thr3e')

Because the publications' text have been indexed as case-sensitive ElasticSearch documents, the
entities you query for should be queried for so that they will be discovered. For example, a 
document may say "Protein ABC" and one of your provided synonyms for an entity may be "protein ABC".
The query for your synonym will not be found in the text. To address this, this script makes a
case-varied version of the synonym so that both "protein ABC" and "Protein ABC" will be queried and 
count for the same entity if discovered in the publication/document text. 
 
```
python '07_run_vary_synonyms_cases.py'
```


---------------------------

***8. Count the synonyms among the publications***
This queries for all synonyms (i.e., all the entities' names) across your publications of interest.

Note: Later when you are deciding which synonyms seem too ambiguous to include in the search and you
filter your synonym list, this ElasticSearch querying does not need to be re-run (which would take a
long time to do). Instead, you just quickly recalculate the entities' scores based on your newly
filtered synonym list. 

Note: Because entities may share synonyms, this iterates through each synonym and searches for it 
across all documents once, not iterating through each entity and searching for the synonyms possibly 
multiple times. 

```
python '08_run_count_synonyms.py'
```


---------------------------

***9. Determine which synonyms should be searched for***

Some synonyms will be very ambiguous, and when they are found in the publications' text, they may
tend to refer to something other than your entity of interest. For example, if you are searching for
the protein called "ALS", but you are also studying the disease "ALS", the query would count every
"ALS" as times that the protein ALS was mentioned in a publication. However, the vast majority of 
those mentions would likely not refer to your entity (protein) but to something else (the disease). 
Some synonyms may tend to be more ambiguous than others, particularly very short synonyms which could
be acronyms for non-entity terms (e.g., the disease ALS) and synonyms which are common words that do
do always refer to the specific instance of your entity (e.g., "Hint" not referring to the protein which 
you think it is). Based on that logic, this identifies those types of synonyms you submitted and 
then shows them to you. You will then inspect the list stored in 'data/remove_these_synonyms.txt'.
Any word in here will have its hits excluded from an entity's score calculation. You may add other
words or phrases that you also want excluded (e.g., multi-word synonyms like "Growth Factor"). This 
process can be easily repeated. These synonyms are case-sensitive, so if one case-variation of a 
synonym is in here but another is still in the case-sensitive entity file, only the first one will
be excluded from the next steps in the pipeline. 

```
python '09_run_screen_synonyms.py'
```
---------------------------

# Next steps:
- Add/remove synonyms as described in the next block
- Run steps 10-13. 
- Inspect the scores. 
- Add/remove synonyms again from 'data/remove_these_synonyms.txt'
- Repeat the process until you're satisfied.

---------------------------

***10. Create entity-to-count mappings***
Using only the synonyms you allowed to be used (not the synonyms in remove_these_synonyms.txt), this
creates entity-to-count, i.e. entity-to-hits mappings for all entities. Because the ElasticSearch
queries in the publications were already performed in step 8, this step should be very quick. 

```
python '10_run_make_entity_counts.py'
```


---------------------------

***11. Update the metadata***

```
python '11_run_metadata_update.py'
```


---------------------------

***12. Calculate CaseOLAP scores for all entities***
Using the approved synonym list and other output from prior steps, this calculates each entities'
CaseOLAP score. The CaseOLAP score depends on how frequent an entity is found in a category (popularity), 
how unique an entity is to a category (distinctiveness), and how much a queried entity name matches
a phrase in a publication (integrity). Here, only popularity and distinctiveness are useful because
integrity is set to 1; all hits are exact matches between the queried entity and the publication text.

```
python '12_run_caseolap_score.py'
```

---------------------------

***13. View entities scores and inspect the reasons for their scores***
You may notice that some entities score highly due to false positive synonyms. In that case, 
go back to the file mentioned just before step 9. Add the bad synonyms to the list, and run steps 
10-13 again until you are satisfied with the quality of the results.
Check the files in in *results/ranked_entities* and *results/ranked_synonyms* (unless you changed 
where they're stored) for more detailed inspection of the top-scoring entities and most found synonyms.
Instead of going through all synonyms in previous steps, it's best to use your efforts with the synonyms that
were actually found and then to prioritize the top-scoring proteins. 

```
python '13_run_inspect_entity_scores.py'
```
