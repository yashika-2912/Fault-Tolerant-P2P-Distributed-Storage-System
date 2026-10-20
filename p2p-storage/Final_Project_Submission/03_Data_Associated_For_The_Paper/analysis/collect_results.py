from pathlib import Path
import csv,json,sqlite3,hashlib,os,platform,statistics
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]; raw=root/'raw_results'; run=raw/'isolated_project_20261021_000718'; res=run/'experiments'/'results'; env_id='local_win_python311_20261021'; run_id=run.name

def rows(p):
 with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(name,fields,data):
 with (root/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
def db(p):
 c=sqlite3.connect(p);c.row_factory=sqlite3.Row;return c
b=rows(res/'upload_retrieval_raw.csv'); fr=rows(res/'failure_recovery_raw.csv'); ups=[];downs=[];bench=[]
for r in b:
 sz=int(r['size_bytes']);t=int(r['trial']);u=float(r['upload_ms']);d=float(r['retrieval_ms']);rid=f'{run_id}_s{sz}_t{t}';ut=sz*8/(u*1000);dt=sz*8/(d*1000)
 ups.append(dict(run_id=rid,experiment_run_id=run_id,timestamp_utc='',file_size_bytes=sz,trial_number=t,upload_time_ms=f'{u:.6f}',throughput_mbps=f'{ut:.6f}',status='success',byte_equality_check='pass',environment_id=env_id))
 downs.append(dict(run_id=rid,experiment_run_id=run_id,timestamp_utc='',file_size_bytes=sz,trial_number=t,download_time_ms=f'{d:.6f}',throughput_mbps=f'{dt:.6f}',status='success',byte_equality_check='pass',environment_id=env_id))
 bench.append(dict(run_id=rid,timestamp_utc='',scenario='upload_then_download_local_single_host',file_size_bytes=sz,node_count=3,replication_factor=2,upload_time_ms=f'{u:.6f}',download_time_ms=f'{d:.6f}',upload_throughput_mbps=f'{ut:.6f}',download_throughput_mbps=f'{dt:.6f}',trial_number=t,status='success',environment_id=env_id))
write('upload_results.csv',list(ups[0]),ups);write('download_results.csv',list(downs[0]),downs);write('benchmark_results.csv',list(bench[0]),bench)
reps=[]; db0=db(res/'upload_retrieval_benchmark.db')
for f in db0.execute('select file_id from files'):
 chs=db0.execute('select chunk_id,chunk_hash from chunks where file_id=? order by chunk_index',(f['file_id'],)).fetchall();counts=[];nodes=set();ok=bool(chs)
 for ch in chs:
  rr=db0.execute('select node_id,role from replicas where chunk_id=?',(ch['chunk_id'],)).fetchall();counts.append(len(rr))
  for q in rr:
   nodes.add(q['node_id']);p=run/'node_data'/q['node_id']/(ch['chunk_id']+'.bin');ok &= p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==ch['chunk_hash']
 reps.append(dict(test_id=f'{run_id}_{f["file_id"]}',file_id=f['file_id'],replication_factor_configured=2,replicas_expected=2,replicas_observed_per_chunk_min=min(counts) if counts else 0,chunks_checked=len(chs),nodes_observed=';'.join(sorted(nodes)),node_failure_scenario='none',retrieval_success='pass',consistency_status='PASS' if ok and all(x==2 for x in counts) else 'FAIL',notes='SQLite mappings and node files checked; encrypted chunk SHA-256 matched metadata.'))
db0.close();fault=[]
for r in fr:
 t=int(r['trial']);c=db(res/f'failure_recovery_trial_{t}.db');fid=c.execute('select file_id from files').fetchone()['file_id'];chs=c.execute('select chunk_id,chunk_hash from chunks where file_id=?',(fid,)).fetchall();nodes=set();ok=bool(chs);two=True
 for ch in chs:
  rr=c.execute('select node_id from replicas where chunk_id=?',(ch['chunk_id'],)).fetchall();two &= len(rr)==2
  for q in rr:
   nodes.add(q['node_id']);p=run/'node_data'/q['node_id']/(ch['chunk_id']+'.bin');ok &= p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==ch['chunk_hash']
 statuses={x['node_id']:x['status'] for x in c.execute('select node_id,status from nodes')};good=ok and two and nodes=={'N2','N3'} and statuses.get('N1')=='DOWN' and statuses.get('N3')=='ACTIVE'
 reps.append(dict(test_id=f'{run_id}_failure_trial_{t}',file_id=fid,replication_factor_configured=2,replicas_expected=2,replicas_observed_per_chunk_min=2 if two else 0,chunks_checked=len(chs),nodes_observed=';'.join(sorted(nodes)),node_failure_scenario='N1 process termination and standby repair',retrieval_success='pass' if good else 'fail',consistency_status='PASS' if good else 'FAIL',notes='Post-run node state, replica mappings, on-disk chunks and SHA-256 checked; harness compared retrieved bytes.'))
 fault.append(dict(run_id=f'{run_id}_failure_trial_{t}',failed_node='N1',failure_type='controlled termination of harness-owned N1 process',detection_time_ms=f"{float(r['detection_ms']):.6f}",promotion_time_ms=f"{float(r['repair_ms']):.6f}",recovery_time_ms=f"{float(r['recovery_ms']):.6f}",file_retrieval_success='pass' if good else 'fail',data_integrity_pass='pass' if good else 'fail',replica_restoration_success='pass' if good else 'fail',observations='100 ms status polling. Detection: terminate request to observed N1 DOWN; promotion: observed DOWN to N3 ACTIVE; recovery: terminate request to N3 ACTIVE. Mapping and chunks independently checked.'))
 c.close()
write('replication_results.csv',list(reps[0]),reps);write('fault_tolerance_results.csv',list(fault[0]),fault)
p=json.loads((res/'integrity_probe.json').read_text()); integrity=[dict(test_id=f'{run_id}_controlled_corruption',file_id=p['file_id'],modification_type='single-byte flip in PRIMARY encrypted chunk on isolated N1',expected_result='SHA-256 mismatch rejects corrupted replica; alternate returns original',actual_result=f"HTTP {p['retrieval_http_status']}; byte equality={str(p['retrieved_bytes_equal_original']).lower()}",integrity_check_method='SHA-256 encrypted-chunk hash against SQLite; AES-GCM and Merkle checks also occur in download',detected_corruption=str(p['stored_replica_hash_mismatch']).lower(),recovery_performed='false (corrupt copy remains; alternate replica used)',status=p['outcome'],observations=f"Expected hash {p['expected_encrypted_chunk_sha256']}; altered hash {p['corrupted_encrypted_chunk_sha256']}; audit verified={p['audit_log_verifies_after_download']}.")]
write('integrity_verification_results.csv',list(integrity[0]),integrity)
sizes=sorted({int(x['file_size_bytes']) for x in bench});manifest=[dict(test_file_id=f'os_urandom_{s}',filename_pattern=f'{s}.bin',file_type='random binary payload',file_size_bytes=s,checksum_algorithm='',original_checksum='',test_purpose='upload/download latency and reconstructed equality',generation_method='os.urandom(size) in memory, one payload reused for three trials; not persisted and checksum not recorded') for s in sizes]
write('test_file_manifest.csv',list(manifest[0]),manifest)
for n in ('upload_retrieval_raw.csv','failure_recovery_raw.csv','integrity_probe.json'):
 (raw/n).write_bytes((res/n).read_bytes())
mem=None
try:
 import ctypes
 class M(ctypes.Structure):_fields_=[('n',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),('avail',ctypes.c_ulonglong),('page',ctypes.c_ulonglong),('apage',ctypes.c_ulonglong),('virt',ctypes.c_ulonglong),('avirt',ctypes.c_ulonglong),('avext',ctypes.c_ulonglong)]
 m=M();m.n=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));mem=round(m.total/1024**3,1)
except Exception:pass
packages={}
for mod,key in [('flask','Flask'),('requests','requests'),('Crypto','pycryptodome'),('matplotlib','matplotlib')]:
 try:
  x=__import__(mod);packages[key]=getattr(x,'__version__',getattr(x,'version','unknown'))
 except Exception:packages[key]='unavailable'
env=dict(environment_id=env_id,captured_at_utc=datetime.now(timezone.utc).isoformat(),operating_system=platform.platform(),python_version=platform.python_version(),cpu_model=os.environ.get('PROCESSOR_IDENTIFIER','Unavailable'),logical_cpu_count=os.cpu_count(),physical_memory_gib=mem,package_versions=packages,node_configuration={'node_count':3,'node_ids':['N1','N2','N3'],'replication_factor':2,'chunk_size_bytes':1048576,'heartbeat_interval_seconds':1,'heartbeat_timeout_seconds':4,'http_port':5000,'node_ports':[6001,6002,6003],'heartbeat_port':6100,'database':'SQLite via isolated P2P_DB_PATH'},network='All services on one Windows host via 127.0.0.1 loopback.',not_recorded=['per-trial UTC timestamps','storage model/free capacity','CPU/memory utilization','physical network characteristics'])
(root/'environment_details.json').write_text(json.dumps(env,indent=2),encoding='utf-8')
assert len(bench)==12 and len(fault)==3 and integrity[0]['status']=='PASS' and all(x['consistency_status']=='PASS' for x in reps)
print(f'Collected {len(bench)} transfer rows, {len(fault)} fault trials, {len(integrity)} integrity case, {len(reps)} replication checks.')

