"""
Live Web Dashboard
Sagnik Chakrabarti | GSU CSc 4740/6740
Run: python dashboard.py  then open http://localhost:5000
"""

import json, threading, queue
from flask import Flask, Response, jsonify
from experiment import run, CONCEPTS, TOKEN_BUDGETS

app = Flask(__name__)
Q = queue.Queue()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Multi-Agent Communication Lab</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet"/>
<style>
:root{--bg:#060810;--panel:#0c1020;--border:#1a2540;--accent:#00f5c4;--accent2:#7c3aed;--accent3:#f59e0b;--red:#ef4444;--text:#e2e8f0;--muted:#64748b;--mono:'Space Mono',monospace;--sans:'Syne',sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,245,196,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,245,196,.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0}
.wrap{max-width:1400px;margin:0 auto;padding:24px;position:relative;z-index:1}
header{display:flex;align-items:center;justify-content:space-between;padding:20px 0 28px;border-bottom:1px solid var(--border);margin-bottom:28px}
.logo{display:flex;align-items:center;gap:14px}
.logo-icon{width:44px;height:44px;background:var(--accent);border-radius:8px;display:grid;place-items:center;font-size:22px;flex-shrink:0}
h1{font-size:1.6rem;font-weight:800;letter-spacing:-.02em}
h1 span{color:var(--accent)}
.sub{font-family:var(--mono);font-size:.7rem;color:var(--muted);margin-top:2px}
.badge{display:flex;align-items:center;gap:8px;background:var(--panel);border:1px solid var(--border);border-radius:999px;padding:6px 16px;font-family:var(--mono);font-size:.75rem}
.dot{width:8px;height:8px;border-radius:50%;background:var(--muted);transition:background .3s}
.dot.on{background:var(--accent);animation:pulse 1.2s infinite}
.dot.done{background:var(--accent3)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.sc{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:20px}
.sl{font-family:var(--mono);font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
.sv{font-size:2rem;font-weight:800;color:var(--accent);line-height:1}
.ss{font-family:var(--mono);font-size:.7rem;color:var(--muted);margin-top:6px}
.main{display:grid;grid-template-columns:1fr 380px;gap:20px;margin-bottom:24px}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:24px}
.pt{font-size:.8rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:20px;display:flex;align-items:center;gap:8px}
.pt::before{content:'';width:3px;height:14px;background:var(--accent);border-radius:2px;display:block}
.bc{display:flex;flex-direction:column;gap:16px}
.br{display:flex;align-items:center;gap:12px}
.bl{font-family:var(--mono);font-size:.72rem;width:80px;color:var(--muted);flex-shrink:0}
.bt{flex:1;height:28px;background:rgba(255,255,255,.03);border-radius:4px;overflow:hidden;display:flex;flex-direction:column;gap:3px;padding:2px 0}
.brow{height:10px;border-radius:3px;transition:width .8s cubic-bezier(.34,1.56,.64,1);display:flex;align-items:center;padding-left:6px;font-family:var(--mono);font-size:.58rem;font-weight:700;color:#fff;min-width:32px}
.brow.ei{background:linear-gradient(90deg,var(--accent2),var(--accent))}
.brow.ac{background:linear-gradient(90deg,#065f46,var(--accent))}
.bm{font-family:var(--mono);font-size:.68rem;color:var(--muted);width:70px;text-align:right;flex-shrink:0}
.legend{display:flex;gap:20px;margin-top:16px}
.li{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:.7rem;color:var(--muted)}
.ld{width:10px;height:10px;border-radius:2px}
.feed-panel{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:24px;display:flex;flex-direction:column;max-height:500px}
.fs{overflow-y:auto;flex:1;display:flex;flex-direction:column;gap:10px}
.fs::-webkit-scrollbar{width:4px}
.fs::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
.fi{background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:8px;padding:12px;animation:fi .4s ease;border-left:3px solid var(--muted)}
.fi.ok{border-left-color:var(--accent)}
.fi.ng{border-left-color:var(--red)}
@keyframes fi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.fh{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.fc{font-weight:700;font-size:.85rem;color:var(--accent)}
.fb{font-family:var(--mono);font-size:.65rem;color:var(--muted);background:rgba(255,255,255,.05);padding:2px 8px;border-radius:3px}
.fm{font-family:var(--mono);font-size:.7rem;color:var(--text);margin-bottom:6px;line-height:1.5;word-break:break-word}
.ff{display:flex;justify-content:space-between}
.fg{font-family:var(--mono);font-size:.65rem}
.fg.ok{color:var(--accent)}
.fg.ng{color:var(--red)}
.fe{font-family:var(--mono);font-size:.65rem;color:var(--accent2)}
.tbl-wrap{background:var(--panel);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.tbl-hdr{padding:18px 24px;border-bottom:1px solid var(--border)}
table{width:100%;border-collapse:collapse}
th{font-family:var(--mono);font-size:.65rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);padding:10px 16px;text-align:left;background:rgba(255,255,255,.02);border-bottom:1px solid var(--border)}
td{font-family:var(--mono);font-size:.72rem;padding:10px 16px;border-bottom:1px solid rgba(255,255,255,.04);vertical-align:top;max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(255,255,255,.02)}
.tag{display:inline-block;padding:2px 8px;border-radius:3px;font-size:.65rem;font-weight:700}
.tok{background:rgba(0,245,196,.1);color:var(--accent)}
.tng{background:rgba(239,68,68,.1);color:var(--red)}
.ctrl{display:flex;justify-content:center;margin-bottom:28px;gap:16px}
.btn{background:var(--accent);color:#060810;border:none;border-radius:8px;padding:12px 32px;font-family:var(--sans);font-size:.9rem;font-weight:800;cursor:pointer;letter-spacing:.02em;transition:transform .15s,opacity .15s}
.btn:hover{transform:translateY(-1px);opacity:.9}
.btn:disabled{opacity:.35;cursor:not-allowed;transform:none}
.btn.out{background:transparent;color:var(--text);border:1px solid var(--border)}
.empty{text-align:center;padding:40px;color:var(--muted);font-family:var(--mono);font-size:.8rem}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="logo">
    <div class="logo-icon">🧬</div>
    <div>
      <h1>Multi-Agent <span>Comm Lab</span></h1>
      <div class="sub">Emergent Communication Experiment // Sagnik Chakrabarti // GSU CSc 4740</div>
    </div>
  </div>
  <div class="badge"><div class="dot" id="dot"></div><span id="stxt">Ready</span></div>
</header>

<div class="ctrl">
  <button class="btn" id="startBtn" onclick="startExp()">▶ Run Experiment</button>
  <button class="btn out" onclick="reset()">↺ Reset</button>
</div>

<div class="stats">
  <div class="sc"><div class="sl">Rounds Done</div><div class="sv" id="sR">0</div><div class="ss">of 16 total</div></div>
  <div class="sc"><div class="sl">Accuracy</div><div class="sv" id="sA">—</div><div class="ss">receiver correct</div></div>
  <div class="sc"><div class="sl">Avg Emergence Index</div><div class="sv" id="sE">—</div><div class="ss">0=English · 1=novel</div></div>
  <div class="sc"><div class="sl">Current Budget</div><div class="sv" id="sB">—</div><div class="ss">words per message</div></div>
</div>

<div class="main">
  <div class="panel">
    <div class="pt">Emergence Index & Accuracy by Budget</div>
    <div class="bc" id="chart"><div class="empty">Start to see results</div></div>
    <div class="legend">
      <div class="li"><div class="ld" style="background:linear-gradient(90deg,#7c3aed,#00f5c4)"></div>Emergence Index</div>
      <div class="li"><div class="ld" style="background:linear-gradient(90deg,#065f46,#00f5c4)"></div>Accuracy</div>
    </div>
  </div>
  <div class="feed-panel">
    <div class="pt">Live Round Feed</div>
    <div class="fs" id="feed"><div class="empty">Rounds appear here…</div></div>
  </div>
</div>

<div class="tbl-wrap">
  <div class="tbl-hdr"><div class="pt">Full Round Log</div></div>
  <div style="overflow-x:auto;max-height:340px;overflow-y:auto">
    <table>
      <thead><tr><th>#</th><th>Concept</th><th>Budget</th><th>Agent-S Message</th><th>Agent-R Guess</th><th>Result</th><th>EI</th><th>Tokens</th></tr></thead>
      <tbody id="tbl"></tbody>
    </table>
  </div>
</div>
</div>

<script>
let rounds=[],bstats={},es=null;
function startExp(){
  document.getElementById('startBtn').disabled=true;
  document.getElementById('dot').className='dot on';
  document.getElementById('stxt').textContent='Running…';
  document.getElementById('feed').innerHTML='';
  document.getElementById('tbl').innerHTML='';
  rounds=[];bstats={};updateStats();
  es=new EventSource('/run');
  es.onmessage=e=>{
    const d=JSON.parse(e.data);
    if(d.done){es.close();document.getElementById('dot').className='dot done';document.getElementById('stxt').textContent='Done ✓';document.getElementById('startBtn').disabled=false;return;}
    addRound(d);
  };
  es.onerror=()=>{es.close();document.getElementById('dot').className='dot';document.getElementById('stxt').textContent='Error';document.getElementById('startBtn').disabled=false;};
}
function addRound(r){
  rounds.push(r);
  const b=r.token_budget;
  if(!bstats[b])bstats[b]={c:0,t:0,ei:[],tok:[]};
  bstats[b].t++;bstats[b].c+=r.correct?1:0;
  bstats[b].ei.push(r.emergence_index);bstats[b].tok.push(r.message_tokens);
  updateStats();updateChart();addFeed(r);addRow(r);
}
function updateStats(){
  document.getElementById('sR').textContent=rounds.length;
  if(!rounds.length)return;
  document.getElementById('sA').textContent=Math.round(rounds.filter(r=>r.correct).length/rounds.length*100)+'%';
  document.getElementById('sE').textContent=(rounds.reduce((a,r)=>a+r.emergence_index,0)/rounds.length).toFixed(3);
  document.getElementById('sB').textContent=rounds[rounds.length-1].token_budget;
}
function avg(arr){return arr.reduce((a,v)=>a+v,0)/arr.length;}
function updateChart(){
  const c=document.getElementById('chart');
  c.innerHTML='';
  [100,50,25,10].forEach(b=>{
    const s=bstats[b],ei=s?avg(s.ei):0,ac=s?s.c/s.t:0,pend=!s;
    const row=document.createElement('div');row.className='br';
    row.innerHTML=`<div class="bl">Budget ${b}w</div>
<div class="bt">
  <div class="brow ei" style="width:${pend?0:ei*100}%">${pend?'':(ei*100).toFixed(0)+'%'}</div>
  <div class="brow ac" style="width:${pend?0:ac*100}%">${pend?'':(ac*100).toFixed(0)+'%'}</div>
</div>
<div class="bm">${s?s.t+' rounds':'pending'}</div>`;
    c.appendChild(row);
  });
}
function addFeed(r){
  const f=document.getElementById('feed');
  const i=document.createElement('div');i.className='fi '+(r.correct?'ok':'ng');
  const m=r.sender_message.length>120?r.sender_message.slice(0,120)+'…':r.sender_message;
  i.innerHTML=`<div class="fh"><span class="fc">${r.concept}</span><span class="fb">${r.token_budget}w</span></div>
<div class="fm">"${m}"</div>
<div class="ff"><span class="fg ${r.correct?'ok':'ng'}">${r.correct?'✓':'✗'} "${r.receiver_guess}"</span><span class="fe">EI ${r.emergence_index.toFixed(3)}</span></div>`;
  f.prepend(i);
}
function addRow(r){
  const tb=document.getElementById('tbl'),tr=document.createElement('tr');
  const m=r.sender_message.length>60?r.sender_message.slice(0,60)+'…':r.sender_message;
  tr.innerHTML=`<td>${r.round_num}</td><td style="color:var(--accent);font-weight:700">${r.concept}</td><td>${r.token_budget}</td><td title="${r.sender_message}">${m}</td><td>${r.receiver_guess}</td><td><span class="tag ${r.correct?'tok':'tng'}">${r.correct?'CORRECT':'WRONG'}</span></td><td style="color:var(--accent2)">${r.emergence_index.toFixed(3)}</td><td>${r.message_tokens}</td>`;
  tb.appendChild(tr);
}
function reset(){
  rounds=[];bstats={};
  document.getElementById('feed').innerHTML='<div class="empty">Rounds appear here…</div>';
  document.getElementById('tbl').innerHTML='';
  document.getElementById('chart').innerHTML='<div class="empty">Start to see results</div>';
  ['sR','sA','sE','sB'].forEach(id=>document.getElementById(id).textContent=id==='sR'?'0':'—');
  document.getElementById('dot').className='dot';document.getElementById('stxt').textContent='Ready';
}
</script>
</body>
</html>"""

@app.route("/")
def index(): return HTML

@app.route("/run")
def run_stream():
    def gen():
        def cb(rd, _interp=None): Q.put(json.dumps(rd))
        def worker():
            try: run(callback=cb)
            finally: Q.put("__DONE__")
        threading.Thread(target=worker, daemon=True).start()
        while True:
            item = Q.get()
            if item == "__DONE__":
                yield 'data: {"done":true}\n\n'; break
            yield f"data: {item}\n\n"
    return Response(gen(), content_type="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.route("/results")
def results():
    try:
        with open("logs/results.json") as f: return jsonify(json.load(f))
    except: return jsonify({"error":"No results yet."})

if __name__ == "__main__":
    print("Dashboard → http://localhost:5000")
    app.run(debug=False, port=5000, threaded=True)