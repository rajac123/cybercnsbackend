from typing import Optional, Dict, Any, List
from elasticsearch import Elasticsearch, RequestsHttpConnection
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body, FastAPI, status, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import json
from fastapi import APIRouter
import zipfile
import os
import salt.config
import salt.client
import requests

# ========= router ========================== #

router = APIRouter(prefix="/user", tags=['Users'])


# ========= golobal Variables ================= #

master_client = salt.client.LocalClient()
json_datas = open('cyber/config.json') 
json_data = json.load(json_datas)



def fetchData(data):
  res = []
  for i in data['hits']['hits']:
    i['_source']['_id'] = i['_id']
    res.append(i['_source'])
  return res



# ======== elasticSerach Configuration ========== #

# es = Elasticsearch(
#     ['192.168.1.205'],
#     http_auth=('admin', 'vzbEic1fmNwUZLET'),
#     scheme="https",
#     port=9200,
#     connection_class=RequestsHttpConnection,
#     use_ssl=True, 
#     verify_certs=False
#   )

# es = Elasticsearch(
#     ['106.51.72.244'],
#     http_auth=('admin', 'vzbEic1fmNwUZLET'),
#     scheme="https",
#     port=22023,
#     connection_class=RequestsHttpConnection,
#     use_ssl=True, 
#     verify_certs=False
#   )




# ======== elasticSerach GetallRecords ========== #

def get_all(indice):
  results = es.search(index=indice, body={"query": { "match_all": {}}, "size": 10 })
  return fetchData(results)


# ======== elasticSerach UpdateRecords ========= #

def update_data(indice, _id, body):
  del body['_id']
  print(body)
  update_dict = {'doc': body}
  results = es.update(index=indice, id=str(_id), body=update_dict)
  return results

# ======== elasticSerach GetOneRecord ========== #

def getone_data(indice, _id):
  get_dict = {"query": { "match": { "_id": _id}}, "size": 10000 }
  results = es.search(index=indice, body=get_dict)
  return fetchData(results)


# ======== elasticSerach GetOneRecordById ====== #

def getone_byid(indice, name):
  query = { "query": { "match_phrase_prefix": { "firstName": { "query": name } } } }
  results = es.search(index=indice, body=query)
  return fetchData(results)



# ======== API's ============================== #


@router.post('/getcustomer')
def getonecustomer(firstName: str):
  try:
    result = getone_byid('test_partner-portal',firstName)
    return JSONResponse({'status': 'success', 'data': result})
  except:
    return JSONResponse({'status': 'failed', 'data': []})



@router.get("/elasticsearch")
def get_users():
  try:
    result = get_all('test_partner-portal')
    return JSONResponse({'status': 'success', 'data': result})
  except:
    return JSONResponse({'status': 'failed', 'data': []})



@router.put("/update_data")
def update(user: Dict):
  try:
    result = update_data('test_partner-portal', user['_id'], user)
    return JSONResponse({'status': 'success', 'data': result})
  except:
    return JSONResponse({'status': 'failed', 'data': []})




@router.get("/cyber/{minion_id}/getBuildInfo")
def getbuildinfo(minion_id: str):
  headers = {"Content-Type": "application/json", "accept": "application/json"}
  url = 'https://betadev.mycybercns.com/api/cyberutils/'+minion_id+'/getBuildInfo'
  res = requests.post(url = url, headers=headers, json = {})
  print(res.json)
  try:
    return True
  except:
    return False


# ============ zip and download =========== #


def getzip(outPath, zipfilename, filename):
  zipObj = zipfile.ZipFile(zipfilename, 'w')
  retval = os.getcwd()
  os.chdir(outPath)
  for files in os.listdir(outPath):
    if files in filename:# list of files from ui
      zipObj.write(files)
  zipObj.close()
  os.chdir(retval)
  path = os.path.join(zipfilename)
  return path






def getminionlogs():
  minion_id = '1.0.0.127.in-addr.arpa'
  minion_path = '/var/log/cybercns/'
  master_path = "/var/cache/salt/master/minions/"+minion_id+"/files/tmp"
  cp_dir = os.system('salt "*" cp.push_dir /var/log/cybercns  upload_path=/tmp')
  filename = ['cybercns.log','cybercnsticket_processor.log', 'cybercnsasset_processor.log', 'cybercns_integration.log']
  if len(filename) > 1:
    if out_cmd and out_cmd[minion_id]:
      files = getzip(file_path, '/var/log/cybercns.zip')
      if os.path.exists(files):
        return FileResponse(path=files, filename='cybercns.log')
    else:
      return False
  else:
    return True
    # write single file copy

getminionlogs()

