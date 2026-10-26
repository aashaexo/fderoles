import json,re,urllib.request,concurrent.futures as cf
UA={'User-Agent':'Mozilla/5.0'}
def get(u):
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25))
    except Exception: return None
PAT=re.compile(r'forward[\s-]*deploy|\bFDE\b',re.I)
def chk(line):
    k,s=line.split()
    out=[]
    if k=='ashby':
        d=get(f'https://api.ashbyhq.com/posting-api/job-board/{s}')
        if d:
            for j in d.get('jobs',[]):
                if PAT.search(j['title']): out.append((j['title'],j.get('location',''),j['jobUrl'],j.get('organizationName') or s))
    elif k=='gh':
        for host in ['boards-api.greenhouse.io']:
            d=get(f'https://{host}/v1/boards/{s}/jobs')
            if d:
                for j in d.get('jobs',[]):
                    if PAT.search(j['title']): out.append((j['title'],j.get('location',{}).get('name',''),j['absolute_url'],j.get('company_name') or s))
    elif k=='lever':
        for host in ['api.lever.co','api.eu.lever.co']:
            d=get(f'https://{host}/v0/postings/{s}?mode=json')
            if isinstance(d,list):
                for j in d:
                    if PAT.search(j['text']): out.append((j['text'],j.get('categories',{}).get('location',''),j['hostedUrl'],s))
                if d: break
    return k,s,out
lines=[l for l in open('scripts/slugs.txt').read().split('\n') if l and not l.startswith('yc') ]
res={}
with cf.ThreadPoolExecutor(30) as ex:
    for k,s,out in ex.map(chk,lines):
        if out: res[f'{k}:{s}']=out
json.dump(res,open('live.json','w'),indent=1)
print(len(res))
for key,v in sorted(res.items()): print(key, len(v), '|', v[0][0], '|', v[0][1])
