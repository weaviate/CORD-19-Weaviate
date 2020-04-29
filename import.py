#!/usr/bin/env python3
import uuid, os, json, sys, time, weaviate, csv
from datetime import datetime
from modules.Weaviate import Weaviate
from utils.helper import *
import csv

DATADIR = sys.argv[2]
WEAVIATE = Weaviate(sys.argv[1])
# CACHEDIR = sys.argv[2]
CLIENT = weaviate.Client(sys.argv[1])


journals = [];
##
# Function to clean up data
##
def processInput(k, v):
    if k == 'Author':
        v = v.replace(' Wsj.Com', '')
        v = v.replace('.', ' ')
        return v
    elif k == 'Summary':
        v = v.replace('\n', ' ')
        return v

    return v

##
# Import the publications without refs except for cities
## 
print('add publisher')

publishers = ['biorxiv', 'CZI', 'Elsevier', 'medrxiv', 'PMC', 'PMC_new', 'WHO']
for publisher in publishers:
    WEAVIATE.runREST('/v1/things', {
        'class': 'Publisher',
        'id': str(uuid.uuid3(uuid.NAMESPACE_DNS, publisher.lower())),
        'schema': {
            'name': publisher
        }
    }, 0, 'POST')

##
# Import the papers
## 
print('add papers')

dataDirs = {
    'biorxiv_medrxiv': DATADIR + '/biorxiv_medrxiv/biorxiv_medrxiv/',
    'custom_license': DATADIR + '/custom_license/custom_license/',
    'comm_use_subset': DATADIR + '/comm_use_subset/comm_use_subset/',
    'noncomm_use_subset': DATADIR + '/noncomm_use_subset/noncomm_use_subset/'
}

i = 1

# create a ThingsBatchRequest for adding things
batch = weaviate.ThingsBatchRequest()

# create a ReferenceBatchRequest for adding references
batchRefs = weaviate.ReferenceBatchRequest()

with open(DATADIR+'/metadata.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        #CreateJurnal

        print(str(i))

        paper = {}
        paper_obj = {
            "abstract": "",
            "body": ""
        }
        if row['full_text_file']:
            file = 'pmc_json/' + row['pmcid'] + '.xml.json' if row['source_x'] == 'PMC' else 'pdf_json/' + row[
                'sha'] + '.json'
            file_path = dataDirs[row['full_text_file']] + file
            try:
                with open(file_path) as json_file:
                    paper = json.load(json_file)
                    paper_obj['abstract'] = format_body(paper.get('abstract')) if paper.get('abstract') else ""
                    paper_obj['body'] = format_body(paper.get('body_text')) if paper.get('body_text') else ""
            except:
                print('file is missing')

        journalId = str(uuid.uuid3(uuid.NAMESPACE_DNS, row['journal'].lower()))

        if journalId not in journals:
            CLIENT.create_thing({"name": row['journal']}, "Journal", journalId)
            journals.append(journalId)

        paper_obj['paperId'] = row['sha']
        paper_obj['title'] = row['title']
        paper_obj['doi'] = row['doi']
        paper_obj['pmcId'] = row['pmcid']
        paper_obj['pubmedId'] = row['pubmed_id']
        paper_obj['publishTime'] = datetime.strptime(row['publish_time'], '%Y-%m-%d').isoformat() + "Z"
        paper_obj['journal'] = [{"beacon":"weaviate://localhost/things/"+journalId}]
        paper_obj['source'] = [{"beacon":"weaviate://localhost/things/"+str(uuid.uuid3(uuid.NAMESPACE_DNS, row['source_x'].lower()))}]
        paper_obj['license'] = row['license']
        paper_obj['hasFullText'] = row['has_pdf_parse'] == 'True'

        # add every 20 by taking the modus of 19 (counter starts at 0)
        if (i % 19) == 0:
            # Send the batch to Weaviate
            asd = CLIENT.create_things_in_batch(batch)

            # Create an empty batch
            batch = weaviate.ThingsBatchRequest()

        # Add the thing to the batch request queue
        batch.add_thing(paper_obj, 'Paper', str(uuid.uuid3(uuid.NAMESPACE_DNS, paper_obj['paperId'])))

        i += 1

    # Send the batch to Weaviate
    CLIENT.create_things_in_batch(batch)
