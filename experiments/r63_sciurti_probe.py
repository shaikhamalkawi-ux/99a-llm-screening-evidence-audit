#!/usr/bin/env python3
"""Public-source admission probe. Print only metadata; never publish source rows."""
import urllib.request,json,time
from pathlib import Path
def get(url):
    for trial in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'99a public scientific-data source admission (R63)'})
            with urllib.request.urlopen(req,timeout=45) as f:return json.load(f)
        except Exception as e:
            if trial==2: raise
            time.sleep(2)
def walk(url):
    while url:
        obj=get(url)
        for it in obj.get('data',[]):
            a=it['attributes']
            if a.get('kind')=='folder':
                walk(it['relationships']['files']['links']['related']['href'])
            elif a.get('kind')=='file':
                found.append({'id':it['id'],'name':a.get('name'),'path':a.get('materialized_path',a.get('path')),'size':a.get('size'),'modified':a.get('date_modified'),'hashes':a.get('extra',{}).get('hashes',{}),'download':it['links'].get('download')})
        url=obj.get('links',{}).get('next')
found=[]
out={'source':'Sciurti et al. 2026, DOI 10.1017/rsm.2025.10044; OSF kjnwt','status':'not yet admitted'}
try:
    node=get('https://api.osf.io/v2/nodes/kjnwt/')
    out['project_title']=node['data']['attributes']['title']
    walk('https://api.osf.io/v2/nodes/kjnwt/files/osfstorage/?page[size]=100')
    out['status']='metadata retrieved; schema and record-level concordance still to be tested'
except Exception as e:out['error']=repr(e)
out['files']=found
Path('r63_sciurti_public_source_inventory.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
