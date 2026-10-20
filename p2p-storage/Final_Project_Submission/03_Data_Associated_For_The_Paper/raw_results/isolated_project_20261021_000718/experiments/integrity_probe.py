import hashlib, json, os, socket, subprocess, sys, time, sqlite3
from pathlib import Path
import requests
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
results=root/'experiments'/'results'; results.mkdir(parents=True,exist_ok=True)
db=results/'integrity_probe_retry.db'
if db.exists(): raise RuntimeError('Refusing to overwrite existing isolated probe DB')
ports=[5000,6001,6002,6003,6100]
for port in ports:
    with socket.socket() as s:
        s.bind(('127.0.0.1',port))
logs=[]; procs=[]
env={**os.environ,'P2P_DB_PATH':str(db)}
commands=[[sys.executable,'coordinator/app.py']]+[[sys.executable,'node/node_process.py','--node-id',f'N{i}','--port',str(6000+i)] for i in range(1,4)]
try:
    for ix,cmd in enumerate(commands):
        log=(results/f'integrity_process_{ix}.log').open('wb'); logs.append(log)
        procs.append(subprocess.Popen(cmd,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT))
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        try:
            if requests.get('http://127.0.0.1:5000/status',timeout=.4).ok: break
        except requests.RequestException: pass
        time.sleep(.1)
    else: raise RuntimeError('Coordinator did not start')
    time.sleep(1.2)
    payload=os.urandom(4096)
    upload=requests.post('http://127.0.0.1:5000/files',files={'file':('integrity_probe.bin',payload)},timeout=30); upload.raise_for_status()
    fid=upload.json()['file_id']
    c=sqlite3.connect(db)
    chunk_id,expected=c.execute('select chunk_id,chunk_hash from chunks where file_id=?',(fid,)).fetchone()
    replicas=c.execute('select node_id,role from replicas where chunk_id=? order by role,node_id',(chunk_id,)).fetchall()
    c.close()
    primary=next((node for node,role in replicas if role=='PRIMARY'),replicas[0][0])
    path=root/'node_data'/primary/(chunk_id+'.bin')
    before=path.read_bytes(); changed=bytearray(before); changed[min(16,len(changed)-1)]^=1; path.write_bytes(changed)
    observed_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    response=requests.get(f'http://127.0.0.1:5000/files/{fid}',timeout=30)
    success=response.status_code==200 and response.content==payload
    c=sqlite3.connect(db)
    mapped=c.execute('select node_id,role from replicas where chunk_id=? order by role,node_id',(chunk_id,)).fetchall()
    audit=c.execute('select event,prev_hash,entry_hash,created_at from audit_log order by entry_index').fetchall()
    c.close()
    from coordinator.audit import _entry_hash,GENESIS_HASH
    prev=GENESIS_HASH; audit_ok=True
    for event,p,h,ts in audit:
        if p!=prev or h!=_entry_hash(event,p,ts): audit_ok=False
        prev=h
    result={'file_size_bytes':len(payload),'file_id':fid,'chunk_id':chunk_id,'replicas_before':replicas,'corrupted_replica_node':primary,'expected_encrypted_chunk_sha256':expected,'corrupted_encrypted_chunk_sha256':observed_hash,'stored_replica_hash_mismatch':observed_hash!=expected,'retrieval_http_status':response.status_code,'retrieved_bytes_equal_original':success,'replica_mapping_after':mapped,'replica_count_after':len(mapped),'audit_log_verifies_after_download':audit_ok,'outcome':'PASS' if observed_hash!=expected and success else 'FAIL','procedure':'Upload random 4096-byte payload in isolated project; flip one byte in PRIMARY encrypted chunk on clone-only node storage; GET file and compare returned bytes to original.'}
    (results/'integrity_probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    if result['outcome']!='PASS': raise RuntimeError('Integrity probe did not pass expected safe fallback')
finally:
    for p in procs:
        if p.poll() is None: p.terminate()
    for p in procs:
        try: p.wait(timeout=5)
        except subprocess.TimeoutExpired: p.kill(); p.wait()
    for f in logs: f.close()


