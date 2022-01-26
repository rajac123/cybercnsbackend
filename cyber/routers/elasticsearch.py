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
# ========= salt config ================ #



router = APIRouter(
    prefix="/user",
    tags=['Users']
)


def fetchData(data):
  res = []
  for i in data['hits']['hits']:
    i['_source']['_id'] = i['_id']
    res.append(i['_source'])
  return res



# ======== elasticSerach Configuration ========== #

es = Elasticsearch(
    ['192.168.1.205'],
    http_auth=('admin', 'vzbEic1fmNwUZLET'),
    scheme="https",
    port=9200,
    connection_class=RequestsHttpConnection,
    use_ssl=True, 
    verify_certs=False
  )

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
  result = getone_byid('test_partner-portal',firstName)
  return JSONResponse({'status': 'success', 'data': result})


@router.get("/elasticsearch")
def get_users():
  result = get_all('test_partner-portal')
  return JSONResponse({'status': 'success', 'data': result})


@router.put("/update_data")
def update(user: Dict):
  result = update_data('test_partner-portal', user['_id'], user)
  return JSONResponse({'status': 'success', 'data': result})


# ============ zip and download =========== #



# outPath = '/var/log/raja'
# zipfilename = '/var/log/sample.zip'

def getzip(outPath, zipfilename):
  zipObj = zipfile.ZipFile(zipfilename, 'w')
  filename = ['cybercns.log','cybercnsticket_processor.log', 'cybercnsasset_processor.log', 'cybercns_integration.log']
  retval = os.getcwd()
  os.chdir(outPath)
  for files in os.listdir(outPath):
    if files in filename:# list of files from ui
      zipObj.write(files)
  zipObj.close()
  os.chdir(retval)
  path = os.path.join(zipfilename)
  return path

master_client = salt.client.LocalClient()

@router.get("/ifconfig")
def ifconfig():
  minion_id = '1.0.0.127.in-addr.arpa'
  source_file = '/var/log/cybercns/'
  file_path = "/var/cache/salt/master/minions/"+minion_id+"/files/tmp"
  out_cmd = master_client.cmd(minion_id,'cp.push_dir' ,[source_file])
  if out_cmd and out_cmd[minion_id]:
    # files = os.path.join(file_path)
    files = getzip(file_path, 'var/log/cybercns.zip')
    if os.path.exists(files):
      return FileResponse(path=files, filename='cybercns.log')
  else:
    return False


import os
>>> os.system('salt "*" cp.push_dir /var/log/cybercns  upload_path=/tmp')




