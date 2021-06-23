import json
import os
import re
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2.service_account import Credentials


# INPUT: a result folder from Google Cloud (ex: occc_result)
# RETURN: blob_list, a list of json files each containing grievances split per 100 pages
def getIterables(folder):

    # get credentials for storage API
    credentials = os.getenv("credentials")
    storage_client = storage.Client.from_service_account_json(credentials)

    '''
    FOR JAY: comment out lines 15 and 16 and uncomment the following
    '''
    # storage_client = storage.Client.from_service_account_json(os.getenv("API_KEY_PATH"))

    # Find all blobs with the information we want
    bucket = storage_client.get_bucket("boston-globe")
    all_blobs = [blob for blob in bucket.list_blobs()]
    pattern = re.compile(folder)
    json_list = [blob for blob in all_blobs if pattern.search(blob.name) is not None]

    # print out json file names
    print('Output files:')
    for blob in json_list:
        print(blob.name)

    print()
    print()

    return json_list



# INPUT: a json file containing 100 pages of grievances data (ex: ncci_result/output-1-to-100.json)
# RETURN: a string of 100 pages of grievances data
def joinPages(file):

    # unload json data
    json_string = file.download_as_string()
    response = json.loads(json_string)

    # concatenate data to string
    all_pages = ''
    for i in range(len(response['responses'])):
        all_pages += response['responses'][i]['fullTextAnnotation']['text']

    return all_pages



# INPUT: a list of json files each containing grievances split per 100 pages (i.e. output of getIterables())
# OUTPUT: a string of all of the grievances data
def joinJSONs(json_list):

    # iterate over the json list, combine all the pages in each json, then combine all the json strings
    all_data = ''
    for blob in json_list:
        all_data += joinPages(blob)

    return all_data



# INPUT: a string of all of the grievances data
# OUTPUT: a list of grievances where each grievance includes data from: 
#         - inmate grievance form
#         - receipt(s) by institutional grievance coordinator
#         - receipt by inmate
def getGrievList(string):
    
    # get indices of all occurences of 'inmate grievance form'
    grievs = string.split('\n')
    indices = [i for i, x in enumerate(grievs) if x == 'INMATE GRIEVANCE FORM']

    # add each grievance to a list by getting data between consecutive occurrences of 'inmate grievance form'
    grievances_list = []
    for i in range(len(indices)-1):
        grievances_list.append(grievs[indices[i]:indices[i+1]])
    
    # add last grievance because it's the last occurrence of 'inmate grievance form'
    grievances_list.append(grievs[indices[len(indices)-1]:])

    print('Number of grievances:')
    print(len(grievances_list))

    print()
    print()

    #print(grievances_list)

    return grievances_list


'''
current code is just extracting info from inmate grievance form (does not include receipts)
'''
# INPUT: a list of grievances
# RETURN: a dictionary where the key is the grievance # and the value is a list containing
#        [institution, housing, date of incident, complaint, staff involved, staff recipient]
def getFields(grievances_list):

    # test for griveance #
    grievance = grievances_list[45]
    gnum = [i for i in grievance if 'Grievance#' in i]
    gnum = gnum[0].split()[1]

    print(gnum)



if __name__ == "__main__":
    folder = 'ncci_result'
    load_dotenv(override=True)
    json_list = getIterables(folder)
    all_data = joinJSONs(json_list)
    grievances_list = getGrievList(all_data)
    getFields(grievances_list)
