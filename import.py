#!/usr/bin/env python3
import uuid, os, json, sys, time, weaviate, csv
from modules.Weaviate import Weaviate
from modules.Weaviate import getWeaviateUrlFromConfigFile
from utils.helper import *

WEAVIATE = Weaviate(sys.argv[1])
# CACHEDIR = sys.argv[2]
CLIENT = weaviate.Client(sys.argv[1])

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

biorxiv_dir = 'biorxiv_medrxiv/'
papers = load_files(biorxiv_dir)

i = 1

# create a ThingsBatchRequest for adding things
batch = weaviate.ThingsBatchRequest()

# create a ReferenceBatchRequest for adding references
batchRefs = weaviate.ReferenceBatchRequest()

for paper in papers:
    paper_obj = {}
    paper_obj['paperId'] = paper['paper_id']
    paper_obj['title'] = paper['metadata']['title']
    paper_obj['abstract'] = format_body(paper['abstract'])
    paper_obj['body'] = format_body(paper['body_text'])

    # add every 20 by taking the modus of 19 (counter starts at 0)
    if (i % 19) == 0:
        # Send the batch to Weaviate
        CLIENT.create_things_in_batch(batch)
        
        # Create an empty batch
        batch = weaviate.ThingsBatchRequest()

    # Add the thing to the batch request queue
    batch.add_thing(paper_obj, 'Paper', str(uuid.uuid3(uuid.NAMESPACE_DNS, paper_obj['paperId'])))

    i += 1

# Send the batch to Weaviate
CLIENT.create_things_in_batch(batch)
