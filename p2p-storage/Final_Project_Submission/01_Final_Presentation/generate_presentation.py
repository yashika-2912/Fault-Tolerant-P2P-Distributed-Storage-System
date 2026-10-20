from pathlib import Path
import re,json,math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR

O=Path(__file__).resolve().parent; D=O/"diagrams"; I=O/"images";D.mkdir(exist_ok=True);I.mkdir(exist_ok=True)
C={"navy":"0B1730","navy2":"132743","blue":"2563EB","teal":"11B5AE","cyan":"6DD5E8","ink":"18243A","muted":"52627A","pale":"F3F7FC","white":"FFFFFF","line":"CBD5E1","amber":"F2A900","red":"D94A4A","green":"248A63","lblue":"E8F0FF","lteal":"E4F7F5","lamber":"FFF4D6","lred":"FCEAEA","lgreen":"E6F5EE"}
def rgb(k): 
 h=C.get(k,k).lstrip("#");return RGBColor(int(h[0:2],16),int(h[2:4],16),int(h[4:6],16))
prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5);W,H=13.333,7.5
def txt(s,x,y,w,h,t,size=15,color="ink",bold=False,align=None,font="Aptos"):
 a=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));f=a.text_frame;f.clear();f.word_wrap=True;f.margin_left=Inches(.05);f.margin_right=Inches(.05);f.margin_top=Inches(.025);f.margin_bottom=Inches(.025)
 p=f.paragraphs[0];p.text=t;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
 if align is not None:p.alignment=align
 return a
def box(s,x,y,w,h,fill="white",stroke="line",radius=True):
 a=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));a.fill.solid();a.fill.fore_color.rgb=rgb(fill);a.line.color.rgb=rgb(stroke);a.line.width=Pt(1.2)
 return a
def dot(s,x,y,d,fill,stroke=None):
 a=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y),Inches(d),Inches(d));a.fill.solid();a.fill.fore_color.rgb=rgb(fill);a.line.color.rgb=rgb(stroke or fill);return a
def pill(s,x,y,w,label,bg="lblue",fg="blue"):
 box(s,x,y,w,.34,bg,bg);txt(s,x+.05,y+.07,w-.1,.18,label,9,fg,True,PP_ALIGN.CENTER)
def line(s,x1,y1,x2,y2,col="blue",width=2,arrow=True):
 a=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2));a.line.color.rgb=rgb(col);a.line.width=Pt(width)
 if arrow:
  try:
   from pptx.enum.dml import MSO_ARROWHEAD
   a.line.end_arrowhead=MSO_ARROWHEAD.TRIANGLE
  except:pass
 return a
def card(s,x,y,w,h,title,body,accent="blue",fill="white",sz=12):
 box(s,x,y,w,h,fill,"line");box(s,x,y,.07,h,accent,accent,False);txt(s,x+.2,y+.14,w-.36,.34,title,15,"navy",True)
 yy=y+.59
 if isinstance(body,list):
  for b in body:
   txt(s,x+.22,yy,w-.42,.54,"•  "+b,sz,"ink");yy+=.58
 else:txt(s,x+.22,yy,w-.42,h-.68,body,sz,"ink")
def node(s,x,y,w,h,title,sub="",fill="lblue",stroke="blue",ts=13):
 box(s,x,y,w,h,fill,stroke);txt(s,x+.06,y+.12,w-.12,.26,title,ts,"navy",True,PP_ALIGN.CENTER)
 if sub:txt(s,x+.09,y+.44,w-.18,h-.49,sub,10,"muted",False,PP_ALIGN.CENTER)
def slide(title,section="PROJECT DESIGN",dark=False,sub=""):
 s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=rgb("navy" if dark else "pale")
 box(s,0,0,W,.075,"teal","teal",False)
 txt(s,.56,.25,11.8,.19,section.upper(),9,"cyan" if dark else "blue",True)
 txt(s,.56,.51,12.15,.52,title,25,"white" if dark else "navy",True,font="Aptos Display")
 if sub:txt(s,.6,1.06,12,.34,sub,11,"muted" if not dark else "line")
 txt(s,.56,7.13,10,.18,"FAULT TOLERANT P2P  •  ACADEMIC PROTOTYPE",8,"muted" if not dark else "line",True)
 txt(s,12.25,7.08,.48,.22,f"{len(prs.slides):02}",9,"blue" if not dark else "cyan",True,PP_ALIGN.RIGHT)
 return s
def source(s,st):txt(s,8,6.79,4.2,.17,st,7,"muted",False,PP_ALIGN.RIGHT)
def add_image_art(path,kind):
 fig,ax=plt.subplots(figsize=(8,4.8),dpi=170);fig.patch.set_alpha(0);ax.set_facecolor((1,1,1,0));ax.set_xlim(0,10);ax.set_ylim(0,6);ax.axis("off")
 if kind=="network":
  pts=[(1.4,4.45),(8.2,4.45),(8.2,1.35)]
  center=(4.9,2.85)
  for x,y in pts:
   ax.annotate("",xy=(x,y),xytext=center,arrowprops=dict(arrowstyle="<->",color="#4FD1C5",lw=2.2),zorder=1)
  ax.add_patch(FancyBboxPatch((.45,.72),1.9,.68,boxstyle="round,pad=.1",fc="#E8F0FF",ec="#6DD5E8",lw=2,zorder=3))
  ax.text(1.4,1.06,"CLIENT / HTTP",ha="center",va="center",color="#132743",fontsize=9,weight="bold",zorder=4)
  ax.annotate("",xy=(4.9,2.85),xytext=(2.35,1.15),arrowprops=dict(arrowstyle="<->",color="#6DD5E8",lw=2.1),zorder=1)
  labels=[("N1","ACTIVE"),("N2","ACTIVE"),("N3","STANDBY")]
  for (x,y),(name,state) in zip(pts,labels):
   edge="#F2A900" if state=="STANDBY" else "#6DD5E8"
   ax.add_patch(Circle((x,y),.53,fc="#132743",ec=edge,lw=2.8,zorder=3))
   ax.text(x,y+.1,name,ha="center",color="white",fontsize=12,weight="bold",zorder=4)
   ax.text(x,y-.2,state,ha="center",color="#CAD6E5",fontsize=7,zorder=4)
  ax.add_patch(FancyBboxPatch((4.05,2.48),1.7,.75,boxstyle="round,pad=.1",fc="#2563EB",ec="#9CC1FF",lw=2,zorder=4))
  ax.text(4.9,2.86,"COORDINATOR",ha="center",va="center",color="white",fontsize=9,weight="bold",zorder=5)
  ax.text(5,.28,"coordinator-mediated chunks  |  SQLite metadata  |  TCP heartbeats",ha="center",color="#CAD6E5",fontsize=8)
 elif kind=="security":
  ax.add_patch(Polygon([(5,5.5),(8,4.5),(7.6,2),(5,.6),(2.4,2),(2,4.5)],fc="#132743",ec="#4FD1C5",lw=3))
  ax.add_patch(Circle((5,3.5),.85,fc="#2563EB",ec="white",lw=2));ax.text(5,3.5,"AES",ha="center",va="center",color="white",fontsize=18,weight="bold")
  ax.text(5,2.2,"GCM  •  SHA-256  •  Merkle",ha="center",color="#DCE8F4",fontsize=10)
 else:
  xs=[1.2,3.7,6.3,8.9];labels=["N1","DOWN","N2","N3"]
  for j,(x,l) in enumerate(zip(xs,labels)):
   if j<3: ax.add_patch(Circle((x,3.4),.5,fc="#132743",ec=["#11B5AE","#D94A4A","#11B5AE"][j],lw=3))
   else:ax.add_patch(Circle((x,3.4),.5,fc="#132743",ec="#F2A900",lw=3))
   ax.text(x,3.4,l,ha="center",va="center",color="white",fontsize=11,weight="bold")
  for a,b in [(0,1),(2,1),(2,3)]:ax.plot([xs[a]+.5,xs[b]-.5],[3.4,3.4],color="#6DD5E8",lw=2)
  ax.text(5,1.65,"repair attempt: fetch surviving copy → STORE on standby",ha="center",color="#DCE8F4",fontsize=10)
 fig.savefig(path,transparent=True,bbox_inches="tight",pad_inches=.05);fig.savefig(Path(path).with_suffix(".svg"),format="svg",transparent=True,bbox_inches="tight",pad_inches=.05);plt.close(fig)
add_image_art(I/"network_hero.png","network");add_image_art(I/"security_integrity.png","security");add_image_art(I/"recovery_resilience.png","recovery")

# 25 substantial presenter notes
N=[
"""Introduce this as an educational prototype for studying reliable file storage, not as a production platform. Its design combines a Flask API, SQLite metadata, and local TCP storage-node processes. The repository configures N1 and N2 as active and N3 as standby. The subtitle states the project’s design motivation, not an experimental result. Leave every personal field unchanged until accurate student and institution details are supplied. The hero graphic is original vector-style artwork; it summarizes networked storage but should not be mistaken for a screenshot or a live deployment.""",
"""Use this roadmap to tell the evaluation panel how the argument will proceed. First establish the storage problem and goals. Then explain the current design and implementation, including how data moves and how integrity is checked. Finally, distinguish component test evidence from the unexecuted performance and end-to-end recovery experiments. The sequence matters: mechanisms are introduced before any claim about their evidence. Transition by asking what new coordination challenges appear when data is spread among machines rather than placed on a single disk.""",
"""A distributed storage system places data across computers and presents a service to clients. It can provide a path to expand capacity or use multiple resources, but distribution alone does not create reliability. A node may fail, messages may be delayed, and coordination metadata may become unavailable. Replication creates alternate copies but consumes additional space and network bandwidth. This project is a small local prototype for investigating storage, monitoring, integrity, and recovery together. Emphasize that these mechanisms need explicit design and verification; distribution by itself does not guarantee availability, confidentiality, or correctness.""",
"""The central problem is that a file with only one accessible copy can become unavailable when its host fails. Once copies are distributed, the system also needs metadata that identifies which node has which chunk, monitoring that estimates node availability, and a recovery procedure that can use a surviving copy. Integrity matters because a returned file must be checked, not merely fetched. The illustration is a conceptual one-node-loss scenario. In the implementation, downloads try replica mappings and skip nodes marked DOWN, but no live end-to-end failure run was conducted for this presentation.""",
"""These four objective groups explain what the project set out to explore. Storage objectives correspond to the implemented upload and download routes and chunking. Reliability objectives map to factor-two placement, heartbeats, and a standby repair routine. Security and integrity objectives map to AES-GCM, SHA-256, Merkle roots, and a hash-linked audit table. Evaluation objectives require more than code: tests and experiments must be run and their evidence retained. The previous audit reported eleven unit tests passing, but the benchmark harnesses and full recovery scenario remain unexecuted. Later slides will make that status explicit.""",
"""This comparison describes general trade-offs, not a claim that centralized storage cannot be redundant. Centralized services can employ replication and high availability, though their control plane may remain an operational dependency. Distributed storage without replication spreads data but may lose access to a portion when a node fails. Replication adds alternate copies with extra capacity and coordination cost. This project demonstrates selected mechanisms on one host and does not benchmark against commercial platforms. Use the table to motivate the design rather than to claim superiority over existing systems.""",
"""The proposed system uses Flask routes for the client-facing API, a coordinator workflow that accesses SQLite metadata, and TCP requests to storage nodes. The configuration defines three nodes, two active at startup and one standby, with a replication factor of two. Data is split into 1 MiB chunks and AES-GCM encrypted before storage. SHA-256 and Merkle checks support verification, while heartbeats trigger a repair attempt after an active node becomes stale. These features are present in code. Whether recovery is complete for a particular failure depends on a surviving copy and successful node communication.""",
"""Functional requirements define operations the application exposes: upload, download, status inspection, and TCP chunk storage. Quality requirements describe properties we want, such as integrity detection and availability after a selected failure. The source implements mechanisms that address some of those requirements, but implementation presence is not equivalent to proven quality. The prior unit suite provides selected component evidence. There is no measured throughput, recovery latency, or fault-success rate. Explain the badges as evidence categories: code present, unit-tested behavior, and still requiring system-level verification.""",
"""Read this architecture by following the data plane and the control plane separately. The client reaches Flask at HTTP port 5000. The coordinator applies the storage workflow, consults SQLite, and sends length-prefixed JSON TCP STORE or FETCH requests to node ports 6001 through 6003. Heartbeats use a separate TCP listener on port 6100. N1 and N2 start ACTIVE, while N3 starts STANDBY. Recovery uses the coordinator to fetch a surviving copy and store it on the standby. Despite the project title, the inspected code has no peer discovery or node-to-node coordination; nodes are controlled by the coordinator.""",
"""The module map uses actual repository files. The Flask routes are in coordinator/app.py; upload and retrieval orchestration are in coordinator/storage.py. SQLite schema and metadata helpers are in db.py. TCP framing and requests live in node_client.py, and node_process.py implements the storage server and heartbeat sender. The data and integrity helpers are chunking.py, crypto.py, merkle.py, and audit.py. heartbeat_monitor.py marks stale ACTIVE nodes DOWN and invokes recovery.py. Connect these modules verbally as a call path rather than implying each is an independently deployed service.""",
"""The upload endpoint expects multipart field file at POST /files. The handler passes its bytes to upload_bytes, which requires at least two ACTIVE nodes. It chunks at one MiB, encrypts each chunk with AES-GCM, calculates the Merkle root over encrypted chunks, and derives a deterministic pair of destinations. The coordinator sends each encrypted blob to both nodes and waits for acknowledgements. It writes file, chunk, replica, and audit metadata only after all replica writes acknowledge. A mid-upload failure can leave an orphaned node file, but the incomplete upload is not made visible in metadata.""",
"""Retrieval begins at GET /files/<file_id>. Metadata gives the ordered chunks and candidate replica locations. For each chunk, the coordinator skips nodes marked DOWN, fetches from another candidate, and compares the encrypted bytes against the stored SHA-256 digest. It then decrypts and authenticates with AES-GCM. After the chunk loop it recomputes the Merkle root over the encrypted chunks, reassembles plaintext in order, checks original size, and appends an audit event. Missing usable replicas or failed authentication or verification cause an error response instead of returning a reconstructed file.""",
"""Chunking creates pieces of at most 1 MiB; a final partial chunk is kept as-is, and an empty file yields no chunks. Each chunk uses AES-256-GCM with a random 12-byte nonce and 16-byte tag. The implementation stores nonce, ciphertext, and tag together. SHA-256 is computed over encrypted chunk bytes and compared during retrieval. The Merkle root aggregates those encrypted bytes’ digests. These mechanisms have different jobs: encryption provides confidentiality, GCM also authenticates ciphertext, and hashing supports comparison. The demo key is hard-coded in source, so this setup is not suitable for protecting real user data.""",
"""Placement is deterministic: the implementation hashes the chunk identifier, uses the first eight digest bytes as a big-endian integer, and takes the result modulo the sorted ACTIVE node count. The next circular node becomes the second destination. With the configured two ACTIVE nodes, each chunk is sent to both. The configured factor does not mean every copy is always healthy: a failed store, later disk loss, or stale metadata can reduce actual durability. Replication is also not backup. Accidental deletion or compromise can affect replicas together. Describe observed replica count only after inspecting actual metadata from a test run.""",
"""A node heartbeat loop attempts to connect to the coordinator every second, sends a framed heartbeat, and expects an acknowledgement. The coordinator records its own receive time to avoid node-clock skew. For ACTIVE nodes with a recorded heartbeat, the detector marks status DOWN when the last arrival is more than four seconds old. A node that has not sent any heartbeat is ignored until its first message. This is a timeout suspicion, not proof of permanent failure: network delay, packet loss, or coordinator trouble can look similar. These are configured thresholds, not measured detection times.""",
"""Recovery is called after the detector marks an ACTIVE node DOWN. The routine selects a node with STANDBY status, finds chunk mappings on the failed node, and searches for a surviving mapped replica that is not DOWN. It fetches the chunk and stores it on the standby. Only after a successful STORE acknowledgement does it replace the failed mapping. The routine then marks the standby ACTIVE and records the result. It can promote the standby even if some affected chunks were not repaired, so promotion is not proof of complete restoration. Treat the final arrangement as expected behavior until an end-to-end experiment verifies it.""",
"""The Merkle helper treats each encrypted chunk as a leaf hash, combines neighboring hexadecimal digests, and repeats until one root remains. If a level has an odd number of leaves, the last leaf is duplicated. The file metadata stores the resulting root, and downloads recompute it over fetched encrypted chunks. For four leaves, the first pair of parent hashes feeds a single root. The tree helps summarize integrity for the whole ordered collection, but this implementation does not provide partial proofs for retrieving only one branch. Existing unit tests verify deterministic roots and detection of a changed chunk.""",
"""Audit rows contain an event, timestamp, predecessor hash, and current hash. The genesis predecessor is a string of zeroes. Each next digest is computed over canonical JSON containing its event, previous hash, and timestamp. Verification walks the rows in insertion order and recomputes every link. A repository unit test alters an earlier event and checks that verification fails. The chain can reveal inconsistent edits when verification state is trusted, but it is not an immutable external ledger. Someone able to rewrite the database and all trusted references could recompute the chain.""",
"""The technology stack lists actual project dependencies and imports. Python is the implementation language. Flask supplies HTTP routes; SQLite stores local metadata; Python TCP sockets carry node and heartbeat messages. PyCryptodome implements AES-GCM, while hashlib provides SHA-256. Requests is used by the CLI; pytest is the test framework; Matplotlib is used by benchmark scripts. The repository contains no Docker, Kubernetes, Redis, or cloud deployment configuration. Loopback addresses and fixed ports make the deployment a local simulation, so do not describe it as a tested multi-host cluster.""",
"""The previous repository audit reported eleven passing unit tests. The inspected test suite covers chunking, crypto round trips and tampering, placement, SQLite schema, Merkle roots, audit tampering, and stale-heartbeat status changes. This is useful component-level evidence. It does not demonstrate a complete networked upload/download after a real node failure, and it does not establish performance. We did not rerun tests as part of this presentation task. The benchmark and failure-recovery harnesses exist but remain unexecuted. Do not infer coverage percentages or successful recovery scenarios from unit tests.""",
"""This is a proposed measurement plan rather than a result slide. Upload and download latency should be timed around successful client requests, with file size and repetitions recorded. Throughput can be expressed as successfully transferred bytes divided by elapsed time. Replication overhead compares additional replica bytes with original size. Detection time should measure node-stop to DOWN status; repair time should separately measure the repair phase and promotion. A sound study records trial counts, workload sizes, hardware, software, and network setup, and retains failed trials. No measurements are currently available, so formulas are provided without values.""",
"""This evidence matrix separates what source code implements from what tests or experiments establish. The previous audit reported eleven unit tests passing, while code inspection confirms upload/download, cryptography, metadata, heartbeat, Merkle, audit, and repair components exist. The test report is limited to unit cases and does not prove production reliability. No benchmark data or end-to-end failover outcomes are available. Use the amber and gray statuses for those gaps; do not turn them into green claims. The most important academic point is transparent evidence: mechanism, verification scope, and unmeasured outcomes should be stated separately.""",
"""Discuss limitations as architectural constraints or open evaluation questions. The system has one coordinator and one local SQLite database, local loopback defaults, no peer discovery or consensus, and no network authentication or TLS. The configured key is a demo constant. Recovery assumes a surviving replica and standby; failed chunks may remain unrepaired even when the standby is promoted. A restarted DOWN node is not automatically reintegrated. Future work should run isolated benchmarks and controlled failure scenarios, then examine concurrent failures, partitions, replica consistency, key provisioning, and multi-host deployment. Do not present proposed work as already complete.""",
"""Summarize the project as an integrated prototype: Flask upload and retrieval, encrypted 1 MiB chunks over TCP, SQLite metadata, deterministic two-node placement, SHA-256 and Merkle checks, hash-linked audit events, and heartbeat-triggered repair logic. The prior unit-test result gives initial evidence for selected components. The project has not yet quantified throughput, recovery time, or end-to-end fault tolerance. The balanced conclusion is that the code provides a platform for studying resilience mechanisms, while a controlled evaluation remains necessary before claiming measured availability, performance, or production security. Close by inviting questions about design assumptions and evidence.""",
"""The references are authoritative documentation for the frameworks and cryptographic standards actually discussed. The project README, configuration, source files, and test suite are primary evidence for implementation-specific details. NIST FIPS 197 specifies AES, and FIPS 180-4 specifies SHA-256 among the Secure Hash Standard algorithms. Flask, SQLite, Python socket, and PyCryptodome documentation support descriptions of those tools. The custom illustrations were generated for this deck and use no external photographs or downloaded artwork. Leave acknowledgements as placeholders until accurate names are provided, then close with thanks and invite technical questions."""
]


def add_flow(s,items,y=2.3,left=.75,boxw=1.55,gap=.22,h=1.15,fill="white",accent="blue"):
 for i,(t,sub) in enumerate(items):
  x=left+i*(boxw+gap);node(s,x,y,boxw,h,t,sub,fill,accent,12)
  if i<len(items)-1:line(s,x+boxw,y+h/2,x+boxw+gap-.03,y+h/2,"teal",1.8)
def add_title_slide():
 s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=rgb("navy");box(s,0,0,W,.075,"teal","teal",False)
 txt(s,.62,.28,11.5,.2,"FINAL YEAR PROJECT PRESENTATION",10,"cyan",True)
 txt(s,.62,.72,6.15,1.05,"FAULT TOLERANT P2P\nDISTRIBUTED STORAGE SYSTEM",27,"white",True,font="Aptos Display")
 txt(s,.67,1.95,6.0,.48,"A Distributed Approach to Reliable, Secure, and Verifiable File Storage",15,"cyan",True)
 txt(s,.68,2.53,5.85,.66,"A distributed storage prototype exploring file distribution, replication, integrity verification, and recovery from storage-node failures.",13,"line")
 s.shapes.add_picture(str(I/"network_hero.png"),Inches(6.8),Inches(1.0),width=Inches(5.9),height=Inches(3.65))
 box(s,.67,3.65,5.75,2.55,"navy2","navy2")
 txt(s,.9,3.86,5.3,.28,"PROJECT DETAILS",10,"cyan",True)
 details=["Presented by: [STUDENT NAME]     Roll Number: [ROLL NUMBER]","Department: [DEPARTMENT NAME]","Institution: [COLLEGE / UNIVERSITY NAME]","Project Guide: [GUIDE NAME]","Academic Year: [ACADEMIC YEAR]"]
 for i,v in enumerate(details):txt(s,.92,4.22+i*.36,5.1,.27,v,11,"white",i==0)
 txt(s,.58,7.12,10,.2,"FAULT TOLERANT P2P  |  ACADEMIC PROTOTYPE",8,"line",True)
 txt(s,12.25,7.08,.48,.22,"01",9,"cyan",True,PP_ALIGN.RIGHT)
 return s
def add_roadmap():
 s=slide("Presentation Overview","ROADMAP",False,"From the storage problem to implementation evidence and next experiments.")
 items=[("01","Problem","Why distribution and fault tolerance matter"),("02","Design","Requirements, architecture, algorithms"),("03","Mechanisms","Storage, security, monitoring, repair"),("04","Evidence","Tests, methodology, measured status"),("05","Close","Limitations and contribution")]
 x0=.65;w=2.34;gap=.22
 for i,(n,t,b) in enumerate(items):
  x=x0+i*(w+gap);dot(s,x+.72,1.78,.72,"blue" if i<3 else "teal")
  txt(s,x+.72,1.96,.72,.22,n,15,"white",True,PP_ALIGN.CENTER)
  if i<4:line(s,x+1.47,2.14,x+w+gap-.05,2.14,"line",2)
  txt(s,x,2.72,w,.32,t,16,"navy",True,PP_ALIGN.CENTER)
  txt(s,x+.04,3.18,w-.08,1.0,b,12,"muted",False,PP_ALIGN.CENTER)
 box(s,.8,4.85,11.75,.9,"white","line")
 txt(s,1.05,5.07,11.2,.4,"Question → design choices → implementation → evidence → what remains to be tested",16,"navy",True,PP_ALIGN.CENTER)
 return s
def add_intro():
 s=slide("Introduction to Distributed Storage Systems","01  •  CONTEXT",False,"Distribute bytes across nodes; coordinate access, placement, and verification.")
 card(s,.65,1.7,5.8,3.85,"Single-machine storage",["One host stores and serves the file.","A host or disk outage can interrupt access to that copy.","Simple to reason about; capacity is tied to the machine."],"muted","white",13)
 card(s,6.85,1.7,5.8,3.85,"Distributed storage",["Data is stored on multiple networked computers.","Clients use a service rather than managing each disk.","Replication may create an alternate copy, with extra storage and coordination cost."],"teal","white",13)
 # Editable storage-device illustrations show where copies reside.
 box(s,2.2,4.48,2.5,.62,"navy2","navy2")
 for k in range(3):
  box(s,2.38,4.57+k*.14,2.12,.095,"blue" if k==0 else "navy2","teal",False)
  dot(s,4.22,4.59+k*.14,.055,"teal")
 for j,x in enumerate([7.35,8.95,10.55]):
  box(s,x,4.48,1.3,.68,"navy2","teal",True)
  for k in range(2):
   box(s,x+.15,4.58+k*.23,1.0,.11,"blue" if j<2 else "amber","teal" if j<2 else "amber",False)
  txt(s,x,5.2,1.3,.18,["Node A","Node B","Node C"][j],8,"muted",True,PP_ALIGN.CENTER)
 line(s,6.35,3.65,6.85,3.65,"blue",2)
 txt(s,.85,5.9,11.7,.48,"Distribution creates options; explicit replication, monitoring, and integrity checks are needed to make those options useful.",15,"navy",True,PP_ALIGN.CENTER)
 return s
def add_problem():
 s=slide("Problem Statement","01  •  MOTIVATION",False,"Illustrative failure scenario — availability of the remaining copy is not a measured outcome.")
 node(s,.8,2.25,2.0,1.1,"Client","requests file","lblue","blue")
 node(s,4.0,1.75,2.25,1.25,"Node A","copy becomes unavailable","lred","red")
 node(s,4.0,3.85,2.25,1.25,"Node B","alternate copy","lgreen","green")
 node(s,8.3,2.75,2.4,1.25,"Coordinator","metadata + selection","lblue","blue")
 line(s,2.8,2.78,4,2.35,"red",2)
 line(s,2.8,2.9,4,4.35,"green",2)
 line(s,6.25,2.35,8.3,3.05,"red",1.5)
 line(s,6.25,4.35,8.3,3.65,"green",1.8)
 txt(s,7.0,1.8,3.6,.45,"Challenges: locate replicas • detect failures • verify bytes • repair mappings",12,"muted",True,PP_ALIGN.CENTER)
 card(s,.85,5.5,11.55,.92,"Project motivation","Combine selected storage, monitoring, integrity, and repair mechanisms in a small prototype, then state clearly what has and has not been verified.","teal","white",12)
 return s
def add_objectives():
 s=slide("Objectives of the Project","02  •  GOALS",False,"Project objectives are goals; later slides separate implemented behavior from evidence.")
 data=[("01","Distributed storage",["Upload and retrieve files","Split bytes into chunks","Track files and chunks in metadata"],"blue","lblue"),("02","Reliability",["Maintain configured replicas","Monitor liveness with heartbeats","Attempt standby-based repair"],"teal","lteal"),("03","Security + integrity",["AES-256-GCM encryption","SHA-256 chunk checks","Merkle root and linked audit"],"green","lgreen"),("04","Evaluation",["Use unit tests for components","Measure performance","Test live failure and recovery"],"amber","lamber")]
 for i,(n,t,b,a,f) in enumerate(data):
  x=.7+(i%2)*6.2;y=1.62+(i//2)*2.45
  box(s,x,y,5.75,2.1,f,"line");dot(s,x+.23,y+.2,.48,a);txt(s,x+.23,y+.32,.48,.18,n,10,"white",True,PP_ALIGN.CENTER);txt(s,x+.88,y+.22,4.5,.32,t,16,"navy",True)
  for j,v in enumerate(b):txt(s,x+.32,y+.78+j*.36,5,.28,"• "+v,12,"ink")
 return s
def add_existing():
 s=slide("Existing Approaches and Their Trade-offs","02  •  CONTEXT",False,"Centralized systems can also use redundancy; compare design trade-offs, not product quality.")
 headers=["Approach","Potential advantage","Potential limitation"]
 rows=[
 ["Single machine","Simple deployment","Host failure may interrupt access to its copy"],
 ["Centralized service","Straightforward coordination","Control service may be a bottleneck or dependency"],
 ["Distributed, no replicas","Data spread across nodes","Node loss can make its portion unavailable"],
 ["Distributed + replicas","Alternate copies may aid availability","More storage, traffic, and coordination"]]
 x=.68;y=1.68;widths=[3.1,4.15,5.0];heights=[.58]+[.83]*4
 xx=x
 for k,h in enumerate(headers):
  box(s,xx,y,widths[k],heights[0],"navy","navy",False);txt(s,xx+.12,y+.15,widths[k]-.24,.24,h,12,"white",True)
  xx+=widths[k]+.04
 for i,row in enumerate(rows):
  xx=x;yy=y+.64+i*.87
  for j,val in enumerate(row):
   box(s,xx,yy,widths[j],.78,"white" if i%2==0 else "lblue","line",False)
   txt(s,xx+.12,yy+.12,widths[j]-.24,.52,val,12,"ink",j==0)
   xx+=widths[j]+.04
 txt(s,.9,5.78,11.5,.5,"This project explores the final row as a prototype; it makes no benchmark or superiority claim.",14,"navy",True,PP_ALIGN.CENTER)
 return s
def add_proposed():
 s=slide("Proposed System","02  •  APPROACH",False,"A coordinator-led local prototype combines storage, metadata, integrity checks, and repair logic.")
 node(s,.7,2.2,1.75,1.02,"Client","HTTP","lblue","blue")
 node(s,3.25,2.2,2.0,1.02,"Flask API","upload / download","lblue","blue")
 node(s,6.1,2.2,2.0,1.02,"SQLite","metadata","lteal","teal")
 node(s,9.55,1.5,2.0,1.05,"N1 + N2","ACTIVE • R=2","lteal","teal")
 node(s,9.55,3.5,2.0,1.05,"N3","STANDBY","lamber","amber")
 line(s,2.45,2.7,3.25,2.7)
 line(s,5.25,2.7,6.1,2.7,"teal")
 line(s,5.25,2.42,9.55,2.0,"blue")
 line(s,5.25,2.9,9.55,3.95,"amber")
 txt(s,2.55,4.95,8.2,.75,"Design intent: retain alternate encrypted chunks and use node-health information to guide retrieval and attempted repair.",15,"navy",True,PP_ALIGN.CENTER)
 txt(s,2.6,5.85,8.2,.3,"Code fact: upload requires at least two ACTIVE nodes; N3 begins as STANDBY.",11,"muted",False,PP_ALIGN.CENTER)
 return s
def add_requirements():
 s=slide("Functional and Non-Functional Requirements","03  •  REQUIREMENTS",False,"Requirements indicate desired behavior; code and test scope determine the evidence level.")
 card(s,.75,1.7,5.75,4.5,"Functional requirements",["POST /files accepts multipart field file.","GET /files/<id> returns reconstructed bytes.","GET /status reports node metadata.","TCP nodes support STORE and FETCH.","Heartbeats update coordinator-side liveness.","Repair copies affected chunks when a source and standby are available."],"blue","white",12)
 card(s,6.85,1.7,5.75,4.5,"Quality attributes to evaluate",["Integrity: compare expected and computed hashes.","Availability: test retrieval after selected failures.","Security: use encryption; review key and transport handling.","Performance: measure request latency and throughput.","Maintainability: separate API, storage, metadata, and helpers.","Evidence status: no benchmark or end-to-end recovery run yet."],"teal","white",12)
 return s
def add_architecture():
 s=slide("High-Level System Architecture","03  •  ARCHITECTURE",False,"Data plane and control plane are separated; arrows show the inspected coordinator-mediated flow.")
 # zones
 box(s,.6,1.55,12.1,3.05,"white","line");txt(s,.82,1.68,2,.22,"DATA PLANE",10,"blue",True)
 box(s,.6,4.8,12.1,1.65,"white","line");txt(s,.82,4.94,2,.2,"CONTROL PLANE",10,"teal",True)
 node(s,.9,2.55,1.5,.86,"Client","HTTP","lblue","blue",12)
 node(s,3.05,2.3,2.0,1.2,"Flask coordinator","app.py / storage.py","lblue","blue",12)
 node(s,6.0,2.45,1.75,.95,"SQLite","5 metadata tables","lteal","teal")
 node(s,9.0,1.95,1.45,.95,"N1","ACTIVE","lteal","teal")
 node(s,10.85,1.95,1.45,.95,"N2","ACTIVE","lteal","teal")
 node(s,9.9,3.15,1.6,.9,"N3","STANDBY","lamber","amber")
 line(s,2.4,2.92,3.05,2.92,"blue")
 line(s,5.05,2.8,6,2.8,"teal")
 line(s,5.05,2.62,9,2.35,"blue")
 line(s,5.05,3.02,10.85,2.55,"blue")
 line(s,5.05,3.3,9.9,3.55,"amber")
 node(s,1.05,5.35,2.25,.7,"Heartbeat listener","TCP :6100","lteal","teal",11)
 node(s,4.35,5.35,2.5,.7,"Failure detector","1 s scan • 4 s timeout","lamber","amber",11)
 node(s,8.1,5.35,3.8,.7,"Replica repair","survivor → standby after ACK","lgreen","green",11)
 line(s,3.3,5.7,4.35,5.7,"teal")
 line(s,6.85,5.7,8.1,5.7,"amber")
 line(s,9.95,4.05,3.3,5.7,"green",1.4)
 txt(s,5.0,4.52,2.75,.18,"heartbeats from N1–N3",8,"green",True,PP_ALIGN.CENTER)
 txt(s,8.55,4.5,3.6,.18,"TCP node ports 6001–6003",8,"muted",False,PP_ALIGN.RIGHT)
 txt(s,7.3,1.7,1.35,.18,"DATA: blue",8,"blue",True)
 txt(s,7.3,1.92,1.35,.18,"METADATA: teal",8,"teal",True)
 txt(s,7.3,2.14,1.35,.18,"REPAIR: amber",8,"amber",True)
 txt(s,7.3,2.36,1.35,.18,"HEARTBEAT: green",8,"green",True)
 txt(s,.9,6.51,11.5,.18,"Implementation note: nodes are coordinator-managed; peer discovery and node-to-node coordination are not implemented.",8,"muted",False,PP_ALIGN.CENTER)
 source(s,"Code: app.py • storage.py • heartbeat_monitor.py • node_process.py • refs [1–3, 7]")
 return s
def add_modules():
 s=slide("Major Modules and Source Responsibilities","03  •  IMPLEMENTATION",False,"Module names and functions below are present in the repository.")
 rows=[
 ("API / client","coordinator/app.py • upload(), download(), status()"),
 ("Workflow","coordinator/storage.py • upload_bytes(), download_bytes()"),
 ("Metadata","coordinator/db.py • init_db(), file/chunk/replica helpers"),
 ("TCP client","coordinator/node_client.py • store_chunk(), fetch_chunk()"),
 ("Storage node","node/node_process.py • STORE/FETCH server + heartbeat_loop()"),
 ("Chunk / crypto","chunking.py • split_file(); crypto.py • aes_encrypt(), aes_decrypt()"),
 ("Integrity / audit","merkle.py • build_merkle_root(); audit.py • append/verify"),
 ("Health / repair","heartbeat_monitor.py • check_all_nodes_once(); recovery.py • recover_failed_node()")]
 for i,(a,b) in enumerate(rows):
  x=.72+(i%2)*6.16;y=1.55+(i//2)*1.23
  box(s,x,y,5.75,1.02,"white","line");pill(s,x+.18,y+.14,1.55,a,"lblue","blue")
  txt(s,x+1.86,y+.16,3.68,.68,b,10,"ink")
 return s
def add_upload():
 s=slide("File Upload and Storage Workflow","04  •  DATA PATH",False,"Metadata is persisted only after all replica STORE acknowledgements succeed.")
 steps=[("1  Request","POST /files\nmultipart: file"),("2  Validate","field present\n2 ACTIVE nodes"),("3  Chunk","split_file\n1 MiB pieces"),("4  Protect","AES-GCM\nMerkle root"),("5  Place","replica_set\n2 nodes"),("6  Store","TCP STORE\nACK each copy"),("7  Record","SQLite rows\nUPLOAD audit")]
 for i,(a,b) in enumerate(steps):
  x=.48+i*1.83;node(s,x,2.05,1.55,1.35,a,b,"white","teal" if i in (3,5,6) else "blue",11)
  if i<6:line(s,x+1.55,2.73,x+1.8,2.73,"teal",1.5)
  if i==3:pass
 card(s,.8,4.05,5.6,1.35,"Success condition","Each chunk is acknowledged by both selected nodes before file/chunk/replica metadata is inserted.","green","lgreen",12)
 card(s,6.85,4.05,5.6,1.35,"Failure nuance","A failed later store can leave orphaned node files; the incomplete file is not made visible in metadata.","amber","lamber",12)
 source(s,"Source: coordinator/app.py • storage.py • placement.py • node_client.py")
 return s
def add_download():
 s=slide("File Retrieval and Reconstruction","04  •  DATA PATH",False,"Verification order follows coordinator/storage.py.")
 steps=[("1  Request","GET /files/<id>"),("2  Lookup","file + ordered chunks"),("3  Fetch","try replicas not DOWN"),("4  Check","SHA-256 encrypted bytes"),("5  Decrypt","AES-GCM authentication"),("6  Aggregate","Merkle root over cipher"),("7  Rebuild","join + size check")]
 for i,(a,b) in enumerate(steps):
  x=.48+i*1.83;node(s,x,2.05,1.55,1.35,a,b,"white","green" if i>=3 else "blue",11)
  if i<6:line(s,x+1.55,2.73,x+1.8,2.73,"teal",1.5)
 card(s,.8,4.08,5.6,1.35,"Fallback behavior","Missing, unreachable, or hash-mismatched replicas are skipped while another mapped copy is available.","teal","lteal",12)
 card(s,6.85,4.08,5.6,1.35,"Failure behavior","No valid replica, GCM authentication failure, Merkle mismatch, or size mismatch prevents success.","red","lred",12)
 source(s,"Source: coordinator/storage.py • crypto.py • merkle.py")
 return s
def add_crypto():
 s=slide("Chunking, Encryption, and Integrity Processing","05  •  DATA PROTECTION",False,"Encryption, authentication, and hash comparison have different roles.")
 steps=[("File","original bytes"),("Chunk","1 MiB max"),("Encrypt","AES-256-GCM"),("Digest","SHA-256"),("Merkle","root over encrypted chunks"),("Store","replicas + metadata")]
 for i,(a,b) in enumerate(steps):
  x=.48+i*1.82;node(s,x,2.0,1.55,1.22,a,b,"white","teal" if i in (2,3,4) else "blue",11)
  if i<5:line(s,x+1.55,2.61,x+1.78,2.61,"teal",1.4)
 s.shapes.add_picture(str(I/"security_integrity.png"),Inches(.9),Inches(3.55),width=Inches(3.5),height=Inches(2.2))
 card(s,4.7,3.7,3.55,1.65,"AES-GCM","Random 12-byte nonce and 16-byte tag; stored layout is nonce || ciphertext || tag.","blue","white",11)
 card(s,8.65,3.7,3.65,1.65,"Checks","SHA-256 compares encrypted chunk bytes. Merkle root summarizes the encrypted chunk sequence.","green","white",11)
 txt(s,1,6.1,11.4,.36,"Demo limitation: AES key is a static source-code constant; do not use it for sensitive data.",12,"red",True,PP_ALIGN.CENTER)
 txt(s,1,6.5,11.4,.18,"Standards/API: AES [4] • SHA-256 [5] • PyCryptodome [6]",8,"muted",False,PP_ALIGN.CENTER)
 source(s,"Source: config.py • crypto.py • chunking.py • storage.py")
 return s
def add_replication():
 s=slide("Replication and Deterministic Data Placement","05  •  STORAGE DESIGN",False,"Configured factor R=2; actual health still depends on successful stores and node availability.")
 node(s,.85,2.15,2.2,1.15,"Chunk ID","SHA-256 prefix","lblue","blue")
 node(s,4.0,2.15,2.7,1.15,"Placement index","first 8 bytes mod |ACTIVE|","white","teal")
 line(s,3.05,2.72,4,2.72)
 node(s,8.15,1.55,2.2,1.05,"N1","ACTIVE","lteal","teal")
 node(s,8.15,3.15,2.2,1.05,"N2","ACTIVE","lteal","teal")
 line(s,6.7,2.55,8.15,2.03,"blue")
 line(s,6.7,2.88,8.15,3.65,"blue")
 node(s,10.65,2.35,1.75,1.05,"N3","STANDBY","lamber","amber")
 line(s,10.35,2.05,10.65,2.65,"amber",1.5)
 line(s,10.35,3.65,10.65,3.05,"amber",1.5)
 box(s,1.0,4.55,11.3,1.25,"white","line")
 txt(s,1.25,4.8,10.8,.28,"primary = sorted_ACTIVE[index]     •     secondary = sorted_ACTIVE[(index + 1) mod n]",14,"navy",True,PP_ALIGN.CENTER)
 txt(s,1.2,5.28,10.9,.28,"With the initial ACTIVE set {N1, N2}, every chunk is placed on both nodes. Upload refuses fewer than two ACTIVE nodes.",11,"muted",False,PP_ALIGN.CENTER)
 return s
def add_heartbeat():
 s=slide("Heartbeat-Based Failure Detection","06  •  NODE HEALTH",False,"Configured interval 1 s • timeout 4 s • detector scans once per interval.")
 # timeline
 line(s,1.0,3.25,12.2,3.25,"line",2,False)
 for x,lab in [(1.5,"t₀"),(3.5,"t₀+1s"),(5.5,"+2s"),(7.5,"+3s"),(9.5,"+4s"),(11.1,"scan")]:
  dot(s,x,3.08,.34,"teal" if x<9.4 else "amber")
  txt(s,x-.25,3.55,.85,.25,lab,10,"muted",True,PP_ALIGN.CENTER)
 for x in [1.5,3.5,5.5,7.5]:
  txt(s,x-.38,2.35,1.05,.22,"HEARTBEAT",9,"green",True,PP_ALIGN.CENTER)
 txt(s,9.0,2.35,1.2,.24,"MISSED",9,"red",True,PP_ALIGN.CENTER)
 box(s,9.4,1.65,2.6,.48,"lred","lred");txt(s,9.52,1.78,2.35,.2,"age > 4 s → mark DOWN",11,"red",True,PP_ALIGN.CENTER)
 card(s,.85,4.45,5.5,1.25,"Detection is suspicion","Timeout cannot distinguish a crashed node from delay, packet loss, or a coordinator/network outage.","amber","lamber",12)
 card(s,6.85,4.45,5.5,1.25,"Actual state rule","Only ACTIVE nodes with a previously received heartbeat are checked; unseen nodes are ignored.","blue","white",12)
 source(s,"Source: config.py • heartbeat_monitor.py • node_process.py")
 return s
def add_recovery():
 s=slide("Standby Recovery and Replica Repair","06  •  NODE HEALTH",False,"Code implements copy attempts and promotion; full end-to-end recovery remains unverified.")
 s.shapes.add_picture(str(I/"recovery_resilience.png"),Inches(.55),Inches(1.65),width=Inches(4.25),height=Inches(2.55))
 seq=[("1","Mark failed ACTIVE DOWN"),("2","Select a STANDBY"),("3","Find surviving mapped replica"),("4","FETCH then STORE each chunk"),("5","Remap only after STORE ACK"),("6","Promote standby ACTIVE")]
 for i,(n,t) in enumerate(seq):
  y=1.68+i*.66;dot(s,5.15,y,.36,"teal" if i<4 else "amber");txt(s,5.15,y+.1,.36,.15,n,9,"white",True,PP_ALIGN.CENTER);txt(s,5.68,y+.03,6.6,.28,t,13,"ink",i==5)
 card(s,.75,5.92,11.85,.58,"Important","Promotion can occur even if some chunks were not repaired; do not equate N3 ACTIVE with complete restoration.","red","lred",11)
 source(s,"Source: heartbeat_monitor.py • recovery.py • db.py")
 return s
def add_merkle():
 s=slide("Merkle-Tree Integrity Verification","07  •  INTEGRITY",False,"Project tree leaves are hashes of encrypted chunks; odd leaves are duplicated at a level.")
 # coordinates
 leafx=[1.45,4.25,7.05,9.85]
 nodes=[(x,4.95,f"H(C{i+1})","lblue","blue") for i,x in enumerate(leafx)]
 parents=[(2.85,3.55,"H(L₁ || L₂)"),(8.45,3.55,"H(L₃ || L₄)")]
 root=(5.65,2.2,"MERKLE ROOT")
 for x,y,t,fi,ac in nodes:node(s,x,y,1.75,.7,t,"encrypted chunk hash",fi,ac,11)
 node(s,2.3,3.65,2.85,.75,parents[0][2],"pair hash","lteal","teal",10)
 node(s,7.9,3.65,2.85,.75,parents[1][2],"pair hash","lteal","teal",10)
 node(s,4.7,2.3,2.8,.78,root[2],"stored in files.merkle_root","lgreen","green",12)
 for x in [2.32,5.12]:line(s,x,4.95,3.15 if x<4 else 4.1,4.4,"blue",1.6)
 for x in [7.92,10.72]:line(s,x,4.95,8.1 if x<9 else 8.95,4.4,"blue",1.6)
 line(s,3.73,3.65,5.6,3.05,"teal",2);line(s,9.33,3.65,6.6,3.05,"teal",2)
 txt(s,.9,6.1,11.4,.32,"Construction: hash each encrypted chunk → hash adjacent digest pairs → repeat to one root; duplicate an odd final leaf.",11,"muted",False,PP_ALIGN.CENTER)
 source(s,"Source: coordinator/merkle.py • storage.py • tests/test_merkle_audit.py")
 return s
def add_audit():
 s=slide("Hash-Linked Audit Log","07  •  INTEGRITY",False,"Each record hash binds its event, timestamp, and predecessor digest.")
 entries=[("ENTRY 1","UPLOAD","prev = 000…000","hash = h₁"),("ENTRY 2","DOWNLOAD","prev = h₁","hash = h₂"),("ENTRY 3","PROMOTE","prev = h₂","hash = h₃"),("ENTRY 4","RECOVERY","prev = h₃","hash = h₄")]
 for i,(a,b,c,d) in enumerate(entries):
  x=.55+i*3.2;node(s,x,2.35,2.65,1.75,a,b+"\n"+c+"\n"+d,"white","teal",12)
  if i<3:line(s,x+2.65,3.22,x+3.1,3.22,"teal",2)
 txt(s,.9,4.65,5.5,.34,"Verification: recompute each entry hash and compare the predecessor link.",13,"navy",True)
 # tamper inset
 box(s,7.1,4.45,5.2,1.4,"lred","red")
 txt(s,7.35,4.63,4.7,.28,"ALTERED EVENT → HASH MISMATCH",12,"red",True,PP_ALIGN.CENTER)
 txt(s,7.35,5.05,4.7,.55,"Detects inconsistent edits if the verifier retains trusted chain state; not an immutable external ledger.",10,"ink",False,PP_ALIGN.CENTER)
 source(s,"Source: coordinator/audit.py • db.py • tests/test_merkle_audit.py")
 return s
def add_stack():
 s=slide("Implementation and Technology Stack","08  •  IMPLEMENTATION",False,"Only technologies present in requirements or imported project code are shown.")
 layers=[("CLIENT","Python CLI • Requests","blue"),("HTTP API","Flask • upload / download / status","teal"),("COORDINATION","Python modules • placement • recovery","blue"),("METADATA","SQLite • files / chunks / nodes / replicas / audit","teal"),("NODE I/O","TCP sockets • framed JSON STORE / FETCH","blue"),("CRYPTO","PyCryptodome AES-GCM • hashlib SHA-256","green")]
 for i,(a,b,col) in enumerate(layers):
  y=1.52+i*.72;box(s,1.4,y,10.55,.56,"white","line");box(s,1.4,y,2.2,.56,col,col,False);txt(s,1.5,y+.17,2,.2,a,11,"white",True,PP_ALIGN.CENTER);txt(s,3.9,y+.15,7.7,.24,b,12,"ink",True)
 txt(s,2.0,6.05,9.4,.28,"Testing: pytest  •  Benchmark plotting dependency: Matplotlib  •  Deployment: local loopback prototype",11,"muted",False,PP_ALIGN.CENTER)
 txt(s,2.0,6.42,9.4,.18,"Framework and storage references: Flask [1] • SQLite [2] • Python sockets [3]",8,"muted",False,PP_ALIGN.CENTER)
 return s
def add_testing():
 s=slide("Testing Strategy and Verified Test Result","09  •  EVIDENCE",False,"Previous repository audit: 11 unit tests passed; that result was not rerun for this deck.")
 card(s,.72,1.62,5.8,3.95,"Unit-test evidence",["Chunk split/reassemble and empty input","AES-GCM round trips, wrong key, tampering","Placement and SQLite schema","Merkle root and audit tamper detection","Stale ACTIVE heartbeat marking"],"green","white",12)
 card(s,6.82,1.62,5.8,3.95,"Not established by that result",["Live upload/download across child processes","Retrieval after an actual node termination","Complete standby replica restoration","Failure-detection or recovery latency","Performance under repeated or concurrent load"],"amber","lamber",12)
 pill(s,.95,5.88,2.1,"11 TESTS REPORTED","lgreen","green")
 txt(s,3.25,5.9,8.6,.28,"Unit tests check components; end-to-end experiments exercise the running system.",13,"navy",True)
 source(s,"Evidence: repository tests • previous audit report")
 txt(s,8.0,6.55,4.2,.18,"pytest docs [8]",8,"muted",False,PP_ALIGN.RIGHT)
 return s
def add_method():
 s=slide("Experimental Evaluation Methodology","09  •  EVALUATION PLAN",False,"Proposed metrics only — no benchmark or end-to-end recovery experiment has been executed.")
 measures=[("Latency","elapsed request time","mean = Σt / n"),("Throughput","successful bytes / elapsed time","bytes ÷ seconds"),("Replica overhead","additional replica bytes","extra / original"),("Detection","node stop → DOWN state","record wall-clock ms"),("Repair","DOWN → repair/promotion","separate copy and total")]
 for i,(a,b,c) in enumerate(measures):
  x=.55+i*2.55;card(s,x,1.78,2.33,2.15,a,[b,c],"blue" if i<3 else "teal","white",11)
 box(s,.85,4.45,11.6,1.25,"navy2","navy2")
 txt(s,1.12,4.67,11,.28,"Controlled run checklist",13,"cyan",True,PP_ALIGN.CENTER)
 txt(s,1.15,5.07,10.9,.4,"Record file sizes • trial count • OS/hardware • topology • fixed-port availability • all failures",11,"white",False,PP_ALIGN.CENTER)
 txt(s,1,6.0,11.2,.32,"No values are reported: existing benchmark scripts write under experiments/results and were left unexecuted.",11,"red",True,PP_ALIGN.CENTER)
 return s
def add_evidence():
 s=slide("Results and Current Implementation Evidence","09  •  EVALUATION",False,"Separate source presence, prior unit evidence, and missing system-level measurements.")
 rows=[("Upload / retrieval routes","In source","No live E2E run"),("AES-GCM / SHA-256","In source + unit tests","Selected component checks"),("Merkle helper","In source + unit tests","No scale/performance data"),("Audit hash chain","In source + unit test","Tamper check is component-level"),("Heartbeat detector","In source + unit test","No real failure timing"),("Standby repair routine","In source","End-to-end recovery unrun"),("Benchmarks","Scripts present","Not executed")]
 widths=[3.3,3.1,5.4];x0=.8;y0=1.55
 for j,h in enumerate(["Capability","Evidence status","What is still unknown"]):
  x=x0+sum(widths[:j]);box(s,x,y0,widths[j],.48,"navy","navy",False);txt(s,x+.1,y0+.12,widths[j]-.2,.2,h,11,"white",True)
 for i,row in enumerate(rows):
  y=y0+.54+i*.61
  for j,v in enumerate(row):
   x=x0+sum(widths[:j]);box(s,x,y,widths[j],.55,"white" if i%2==0 else "lblue","line",False);txt(s,x+.1,y+.13,widths[j]-.2,.3,v,10,"ink",j==0)
 txt(s,.9,6.45,11.5,.22,"No benchmark values, recovery duration, success rate, or storage-overhead result is available.",11,"red",True,PP_ALIGN.CENTER)
 return s
def add_future():
 s=slide("Limitations and Future Enhancements","10  •  NEXT STEPS",False,"Separate established architectural limits from evaluation work still to be done.")
 card(s,.72,1.65,5.8,4.7,"Current constraints / open evidence",["Single coordinator and local SQLite metadata","Loopback defaults; no peer discovery or consensus","No HTTP/TCP authentication or TLS","Static demo key; no external key management","No automatic reintegration of restarted DOWN nodes","Benchmarks and end-to-end recovery unmeasured"],"amber","white",11)
 card(s,6.82,1.65,5.8,4.7,"Future work",["Isolated upload/download benchmark series","Controlled one-node failure and repair trials","Network delay, partition, and concurrent-failure tests","Replica consistency and repair validation","Secure key provisioning and authenticated transport","Multi-host and workload scaling evaluation"],"teal","white",11)
 return s
def add_conclusion():
 s=slide("Conclusion and Project Contribution","10  •  SUMMARY",True,"A prototype foundation for investigating resilient storage—not a production availability claim.")
 cols=[("STORAGE","HTTP file operations\n1 MiB encrypted chunks\nTCP node I/O","blue"),("INTEGRITY","SHA-256 comparisons\nMerkle root check\nHash-linked audit events","teal"),("RECOVERY","Heartbeat-based DOWN state\nStandby copy attempts\nEvidence still needed","amber")]
 for i,(a,b,col) in enumerate(cols):
  x=.8+i*4.15;box(s,x,2.0,3.65,2.25,"navy2",col);txt(s,x+.2,2.25,3.25,.33,a,16,"cyan" if col!="amber" else "amber",True,PP_ALIGN.CENTER);txt(s,x+.25,2.9,3.15,1.0,b,13,"white",False,PP_ALIGN.CENTER)
 txt(s,1.05,4.8,11.2,.7,"Initial unit-test evidence exists. Controlled experiments are needed to quantify performance and establish end-to-end recovery effectiveness.",16,"white",True,PP_ALIGN.CENTER)
 txt(s,1.05,5.95,11.2,.36,"Distributed storage + integrity verification + failure monitoring = a foundation for investigating resilient systems.",12,"cyan",True,PP_ALIGN.CENTER)
 return s
def add_references():
 s=slide("References and Acknowledgements","CLOSING",True)
 refs=[
 ("[1] Flask Documentation","https://flask.palletsprojects.com/en/stable/"),
 ("[2] SQLite Documentation","https://sqlite.org/docs.html"),
 ("[3] Python socket module","https://docs.python.org/3/library/socket.html"),
 ("[4] NIST FIPS 197, AES","https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf"),
 ("[5] NIST FIPS 180-4, Secure Hash Standard","https://csrc.nist.gov/pubs/fips/180-4/upd1/final"),
 ("[6] PyCryptodome AES API","https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html"),
 ("[7] Repository README, configuration, source, tests","Local project files inspected for implementation claims"),
 ("[8] pytest documentation","https://docs.pytest.org/en/stable/")]
 for i,(a,b) in enumerate(refs):
  col=0 if i<4 else 1;row=i if i<4 else i-4;x=.75+col*6.0;y=1.45+row*.78
  txt(s,x,y,5.55,.25,a,11,"cyan",True);txt(s,x,y+.3,5.55,.25,b,8,"white")
 box(s,1.0,5.05,11.3,.75,"navy2","navy2")
 txt(s,1.2,5.18,10.9,.2,"Acknowledgements: [GUIDE / LAB / INSTITUTIONAL ACKNOWLEDGEMENTS]",9,"line",True,PP_ALIGN.CENTER)
 txt(s,1.2,6.05,10.9,.38,"THANK YOU  •  QUESTIONS AND DISCUSSION",18,"white",True,PP_ALIGN.CENTER)
 return s

# Build exact 25 substantive slides
add_title_slide();add_roadmap();add_intro();add_problem();add_objectives();add_existing();add_proposed();add_requirements();add_architecture();add_modules();add_upload();add_download();add_crypto();add_replication();add_heartbeat();add_recovery();add_merkle();add_audit();add_stack();add_testing();add_method();add_evidence();add_future();add_conclusion();add_references()
if len(prs.slides)!=25:raise RuntimeError(f"expected 25 slides, got {len(prs.slides)}")


# Supporting diagram exports. The corresponding diagrams in the presentation are native editable shapes.
def diagram_export(name,title,labels,edges):
 fig,ax=plt.subplots(figsize=(11,4.2),dpi=150);fig.patch.set_facecolor("#F3F7FC");ax.set_facecolor("#F3F7FC");ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis("off")
 n=len(labels);xs=[.08+i*.84/max(n-1,1) for i in range(n)]
 for i,(head,sub) in enumerate(labels):
  x=xs[i];y=.48
  ax.add_patch(FancyBboxPatch((x-.075,y-.12),.15,.24,boxstyle="round,pad=.015",fc="#E8F0FF",ec="#2563EB",lw=1.6))
  ax.text(x,y+.035,head,ha="center",va="center",fontsize=9,weight="bold",color="#0B1730")
  ax.text(x,y-.055,sub,ha="center",va="center",fontsize=6.4,color="#52627A",wrap=True)
 for a,b,label in edges:
  x1,x2=xs[a]+.078,xs[b]-.078
  ax.annotate("",xy=(x2,.48),xytext=(x1,.48),arrowprops=dict(arrowstyle="->",lw=1.5,color="#11B5AE"))
  ax.text((x1+x2)/2,.55,label,ha="center",fontsize=6,color="#18243A")
 ax.text(.02,.91,title,fontsize=15,weight="bold",color="#0B1730")
 fig.savefig(D/(name+".png"),bbox_inches="tight",dpi=170);fig.savefig(D/(name+".svg"),bbox_inches="tight");plt.close(fig)
diagram_export("upload_workflow","Upload workflow",[(x,y) for x,y in [("HTTP","POST /files"),("Chunk","1 MiB"),("Protect","AES-GCM"),("Place","R = 2"),("Store","TCP ACK"),("Metadata","SQLite")]],[(i,i+1,"") for i in range(5)])
diagram_export("retrieval_workflow","Retrieval workflow",[(x,y) for x,y in [("HTTP","GET /id"),("Lookup","ordered chunks"),("Fetch","replica"),("Check","SHA-256"),("Decrypt","GCM"),("Root","Merkle"),("Rebuild","size check")]],[(i,i+1,"") for i in range(6)])
diagram_export("heartbeat_detection","Heartbeat detection",[(x,y) for x,y in [("Node","HEARTBEAT"),("Coordinator","record time"),("Timeout","> 4 s"),("State","ACTIVE → DOWN"),("Repair","routine call")]],[(i,i+1,"") for i in range(4)])
diagram_export("replica_repair","Standby replica repair",[(x,y) for x,y in [("N1","failed"),("N2","surviving copy"),("N3","standby"),("Metadata","remap on ACK"),("Status","promote")]],[(0,1,"source"),(1,2,"copy"),(2,3,"ack"),(3,4,"")])
# Merkle and audit diagrams are also included as dedicated native shapes in slides 17 and 18.
(D/"README.md").write_text("""# Diagram assets

The editable versions are native PowerPoint shapes on slides 9 (architecture), 11 (upload), 12 (retrieval), 14 (placement), 15 (heartbeat), 16 (repair), 17 (Merkle), and 18 (audit chain). The PNG/SVG files here are portable reference exports for upload, retrieval, heartbeat, and repair flows. The original hero/security/recovery illustrations used inside the deck are under ../images/ and were generated locally for this presentation. No external images were used.
""",encoding="utf-8")
# write speaker notes and source citations
titles=[
"Title Slide","Presentation Overview","Introduction to Distributed Storage Systems","Problem Statement","Objectives of the Project","Existing Approaches and Their Trade-offs","Proposed System","Functional and Non-Functional Requirements","High-Level System Architecture","Major Modules and Source Responsibilities","File Upload and Storage Workflow","File Retrieval and Reconstruction","Chunking, Encryption, and Integrity Processing","Replication and Deterministic Data Placement","Heartbeat-Based Failure Detection","Standby Recovery and Replica Repair","Merkle-Tree Integrity Verification","Hash-Linked Audit Log","Implementation and Technology Stack","Testing Strategy and Verified Test Result","Experimental Evaluation Methodology","Results and Current Implementation Evidence","Limitations and Future Enhancements","Conclusion and Project Contribution","References and Acknowledgements"]
notes=N
if len(titles)!=25 or len(notes)!=25:raise RuntimeError("slide or notes count mismatch")
def wc(s):return len(re.findall(r"\b[\w’'-]+\b",s))
note_md=["# Speaker Notes","","> Presenter notes are stored in this Markdown file. They are not embedded in the PPTX because python-pptx does not provide reliable native notes-slide authoring.",""]
for i,(t,n) in enumerate(zip(titles,notes),1):
 if wc(n)<80:raise RuntimeError(f"speaker notes too short: slide {i} has {wc(n)} words")
 note_md += [f"## Slide {i:02d} — {t}","",n,"",f"**Presenter handoff:** {titles[i] if i<25 else 'Invite questions and discussion.'}",""]
note_md += ["## Viva prompts","","- What is the difference between replication and backup?","- Why is failure detection a suspicion rather than proof?","- What do AES-GCM, SHA-256, and the Merkle root each contribute?","- What does the previous unit-test result establish, and what does it not establish?","- Which controlled experiment should be run first, and what evidence should be retained?",""]
(O/"presentation_notes.md").write_text("\n".join(note_md),encoding="utf-8")
(O/"presentation_references.md").write_text("""# Presentation References

## Project evidence

Project README, requirements.txt, configuration, source modules, tests, and design document in the project repository. Implementation-specific statements were checked against these files. A previous repository audit reported 11 passing unit tests; this presentation generation did not rerun the suite. The benchmark scripts exist under experiments/bench_upload_retrieval.py and experiments/bench_failure_recovery.py; neither they nor end-to-end recovery were executed.

## Official technology and standards references

[1] Flask documentation, https://flask.palletsprojects.com/en/stable/
[2] SQLite documentation, https://sqlite.org/docs.html
[3] Python socket module, https://docs.python.org/3/library/socket.html
[4] NIST FIPS 197-upd1, Advanced Encryption Standard, https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf
[5] NIST FIPS 180-4, Secure Hash Standard, https://csrc.nist.gov/pubs/fips/180-4/upd1/final
[6] PyCryptodome AES API, https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html
[7] Project repository README, configuration, source code, tests, and design document (local files).
[8] pytest documentation, https://docs.pytest.org/en/stable/

## Visual assets

All artwork in images/ was created for this presentation using Matplotlib vector primitives and exported as PNG/SVG. No external photographs, icons, or stock assets were used; there are no external asset licensing obligations.
""",encoding="utf-8")
# Deck output
pptx=O/"Fault-Tolerant-P2P-Distributed-Storage-System.pptx"
prs.core_properties.title="Fault Tolerant P2P Distributed Storage System"
prs.core_properties.subject="Final-year project presentation"
prs.core_properties.author="[STUDENT NAME]"
prs.core_properties.keywords="distributed storage, replication, integrity, fault detection"
prs.save(pptx)

