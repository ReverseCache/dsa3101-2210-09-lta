import json
from urllib.parse import urlparse
import httplib2 as http #External library

def get_json():
    # Authentication parameters
    headers = { 'AccountKey' : 'AO4qMbK3S7CWKSlplQZqlA==', 'accept' : 'application/json'} #this is by default

    # API parameters
    uri = 'http://datamall2.mytransport.sg/' #Resource URL
    path = 'ltaodataservice/Traffic-Imagesv2'
 
    # Build query string & specify type of API call
    target = urlparse(uri + path)
    method = 'GET'
    body = ''

    # Get handle to http
    h = http.Http()
    # Obtain results
    response, content = h.request(target.geturl(), method, body, headers)
    # Parse JSON to print
    jsonObj = json.loads(content)
    return jsonObj

if __name__ == "__main__":
    get_json()