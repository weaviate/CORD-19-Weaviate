_UNDER DEVELOPMENT_

# CORD-19 Weaviate

The COVID-19 Open Research Dataset Challenge (CORD-19) is published by Kaggle: https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge.


## How to get started

### Download the papers
Download all `biorxiv_medxriv` json files from https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge into a folder with the same name.

### Execute the import

1. [Install weaviate-cli](https://www.semi.technology/documentation/weaviate-cli/current/installation.html).
2. `$ pip3 install -r requirements.txt`
3. `$ weaviate-cli cluster-create`
4. `$ weaviate-cli schema-import --location=schema.json`
5. `$ python3 import.py <weaviate-url>`


## Status
Currently, the paper id, title, abstract and full body text of 885 papers of `biorxiv_medxriv` can be imported by the script above. Next steps are:
- [ ] Add metadata (references) of the papers to Weaviate. First, separate objects for authors, institutes, journals etc need to be created.
- [ ] Add papers from the other collections (commercial, non-commercial, custom licence, see https://pages.semanticscholar.org/coronavirus-research)
- [ ] EXPLORE! Use GraphQL and do classifications etc!

## Notes
- [ ] Let's collaborate to make something great
- [ ] I did not pay full attention to vectorization settings in the schema. When we want to do search and classification, maybe this needs better setting (better check now than later)

## References
- Used some code from this kernel: https://www.kaggle.com/xhlulu/cord-19-eda-parse-json-and-generate-clean-csv
