# CORD-19 Weaviate

The COVID-19 Open Research Dataset Challenge (CORD-19) is published by Kaggle: https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge. The goal is to explore the dataset and get new insights using [Weaviate](https://github.com/semi-technologies/weaviate).


## How to get started

### Download the papers

Download all json files from https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge into a folder.

### Run with Docker

1. `docker run --env "WEAVIATE_URL=<weaviate-url>" semitechnologies/weaviate-demo-covid19`

_Please note that the Kaggle data is cached inside the Docker container._

### Execute the import

Start an English [local Weaviate](https://www.semi.technology/documentation/weaviate/current/get-started/install.html#docker-compose) or a Weaviate on the cluster service ([Install weaviate-cli](https://www.semi.technology/documentation/weaviate-cli/current/installation.html) then `$ weaviate-cli cluster-create`).

0. `$ pip3 install -r requirements.txt`
0. `$ weaviate-cli schema-import --location=schema.json`
0. `$ python3 import.py <weaviate-url> <data-folder>`

## Example Queries

Count all papers

```graphql
{
  Aggregate{
    Things{
      Paper{
        meta {
          count
        }
      }
    }
  }
}
```

Get a paper with a graph reference

```graphql
{
  Get {
    Things {
      Paper {
        title
        Journal {
          ... on Journal {
            name
          }
        }
      }
    }
  }
}
```

Search for the concept of _chiroptera_

```graphql
{
  Get {
    Things {
      Paper(
        explore:{
          concepts: ["chiroptera"] # <== basically a bat
        },
      	limit: 5
      ) {
        title
        abstract
      }
    }
  }
}
```

Search for the concept of _chiroptera_ in a relation to _cattle_

```graphql
{
  Get {
    Things {
      Paper(
        explore:{
          concepts: ["chiroptera"] # <== basically a bat
          moveTo: {
            concepts: ["cattle"] # <== relation to cows, bulls, oxen, or calves
            force: 0.85
          }
        },
      	limit: 5
      ) {
        title
        abstract
      }
    }
  }
}
```

## Status

Currently, the paper id, title, abstract and full body text of 885 papers of `biorxiv_medxriv` can be imported by the script above. Next steps are:
- [x] Add metadata (references) of the papers to Weaviate. First, separate objects for authors, institutes, journals etc need to be created.
- [ ] Add papers from the other collections (commercial, non-commercial, custom licence, see https://pages.semanticscholar.org/coronavirus-research)

## Notes

- [ ] Let's collaborate to make something great
- [x] I did not pay full attention to vectorization settings in the schema. When we want to do search and classification, maybe this needs better setting (better check now than later)

## References

- Used some code from this kernel: https://www.kaggle.com/xhlulu/cord-19-eda-parse-json-and-generate-clean-csv
