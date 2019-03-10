
###########################################################################
#A tagging script using tag editor boto3 ResourceTag
# for the any aws account taggging
# covert this to a handler function and this can be a scheduled lambda
###########################################################################
import boto3
import argparse
import csv
import json
import time

field_names = ['ResourceArn', 'TagKey', 'TagValue']
def writeToCsv(writer, args, tag_list):
    for resource in tag_list:
        print("Extracting tags for resource: " +
              resource['ResourceARN'] + "...")
        for tag in resource['Tags']:
            row = dict(
                ResourceArn=resource['ResourceARN'], TagKey=tag['Key'], TagValue=tag['Value'])
            writer.writerow(row)

def input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True,
                        help="Output CSV file (eg, /tmp/tagged-resources.csv)")
    parser.add_argument("--tags",  type=str, required=False,
                        help="{'tag-name': 'tag-value'}")
    parser.add_argument("--bucket",  type=str, required=True,
                        help="Provide the bucket name to save CSV file")
    parser.add_argument("--key",  type=str, required=True,
                        help="Provide the bucket key to save CSV file")
    parser.add_argument("--query",
                        help="Query DDL filename")
    parser.add_argument("--newtags",
                        help="{'tag-name': 'tag-value'")
    return parser.parse_args()

###### Query from s3 #######

def s3parsing(bucket, key, query, newtags):
    s3 = boto3.client('s3')
    print ('_____________......____________')
    with open(query) as queryfile:
        read_query = queryfile.read()
        print (read_query.strip())
    response = s3.select_object_content(
        Bucket=bucket,
        Key=key,
        ExpressionType='SQL',
        Expression=read_query.strip(),
        InputSerialization = {'CSV': {"FileHeaderInfo": "Use"}},
        OutputSerialization = {'CSV': {}},
    )
    for event in response['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            result = records.strip("\n").replace('\n', ',')
    client = boto3.client('resourcegroupstaggingapi')
    response = client.tag_resources(ResourceARNList=result.split(','), Tags=newtags)
    print (response)

def main():
    args = input_args()
    tag_list = []
    #generating tag filters here that was passed by the user
    tags = json.loads(args.tags)
    for key, value in tags.items():
        tag_list.append({'Key': key,'Values': [value]})
    print (tag_list)
    restag = boto3.client('resourcegroupstaggingapi')
    #write all the tagged resources to the csv file
    with open(args.output, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL,
                                delimiter=',', dialect='excel', fieldnames=field_names)
        writer.writeheader()
        response = restag.get_resources(ResourcesPerPage=50, TagFilters=tag_list)
        writeToCsv(writer, args, response['ResourceTagMappingList'])
        while 'PaginationToken' in response and response['PaginationToken']:
            token = response['PaginationToken']
            response = restag.get_resources(
                ResourcesPerPage=50, PaginationToken=token)
            writeToCsv(writer, args, response['ResourceTagMappingList'])
    #push the file to s3
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(args.output, args.bucket, args.key)
    time.sleep(10)
    #call the querying functionality to filter and tag
    s3parsing(args.bucket,args.key,args.query,args.newtags)

if __name__ == '__main__':
    main()
