# awshammer 

- [awsblog](#awsblog)
- [Usage](#usage)

## awsblog

This a program which was written by following this blog,

[awsbloglink](https://aws.amazon.com/blogs/architecture/how-to-efficiently-extract-and-query-tagged-resources-using-the-aws-resource-tagging-api-and-s3-select-sql/)

## Usage

Run this python program by passing the right arguments. This will do an API call to the resource tag api and will list all the resources
based on your tag filter and will save the CSV file in S3. You can query against the CSV file, further filter resources and tag them.

```
python awstagger.py --output {outputfile} 
                       --tags {tags} 
                       --bucket {bucketname} 
                       --key {keyname} 
                       --query {query} 
                       --newtags {tag to add}

where

{outputfile} - filelocation to save the csvfile ex. /tmp/tagged-resources.csv
{tags} - resources will be filtered based on this tags "{'tag-name': 'tag-value'}" 
{bucketname} - bucketname to store the CSV file 
{keyname} - bucket keyname to store the object csv file
{query} - query file 
{newtags} - "{'tag-name': 'tag-value'}" these tags will be added 
```

