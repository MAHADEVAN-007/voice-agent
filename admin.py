import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")

ADMIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>VocalKart Admin</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0a0a0a;color:#e5e5e5;padding:20px}
  h1{color:#60a5fa;margin-bottom:8px}
  .sub{color:#737373;font-size:14px;margin-bottom:24px}
  .card{background:#1a1a1a;border:1px solid #262626;border-radius:12px;padding:16px;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;gap:16px}
  .card .phone{font-size:16px;font-weight:600}
  .card .time{color:#737373;font-size:13px}
  .card .actions{display:flex;gap:8px}
  .btn{color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:14px;font-weight:600;cursor:pointer;transition:opacity .2s}
  .btn:hover{opacity:.8}
  .btn-approve{background:#16a34a}
  .btn-reject{background:#dc2626}
  .empty{text-align:center;padding:60px 20px;color:#525252}
  .empty h2{font-size:20px;margin-bottom:6px;color:#a3a3a3}
  .toast{position:fixed;bottom:20px;right:20px;background:#1a1a1a;border:1px solid #262626;border-radius:8px;padding:12px 20px;font-size:14px;opacity:0;transition:opacity .3s}
  .toast.show{opacity:1}
  #login{max-width:360px;margin:80px auto;background:#1a1a1a;border:1px solid #262626;border-radius:12px;padding:24px;text-align:center}
  #login input{width:100%;padding:12px;border-radius:8px;border:1px solid #262626;background:#0a0a0a;color:#e5e5e5;font-size:15px;margin-bottom:12px}
  #login button{width:100%;padding:12px;border:none;border-radius:8px;background:#60a5fa;color:#fff;font-size:15px;font-weight:600;cursor:pointer}
</style>
</head>
<body>
<h1>VocalKart Admin</h1>
<p class="sub">Pending access requests</p>
<div id="login">
  <input type="password" id="secret" placeholder="Admin secret" autocomplete="off">
  <button onclick="login()">Login</button>
</div>
<div id="panel" style="display:none">
  <p class="sub" id="status">Loading...</p>
  <div id="requests"></div>
</div>
<div id="toast" class="toast"></div>
<script>
let SECRET='';
const REQUEST_ID="__REQUEST_ID__";
const DIV=document.getElementById('requests');
const STATUS=document.getElementById('status');
const TOAST=document.getElementById('toast');
let toastTimer;

function showToast(msg,ok){
  TOAST.textContent=msg;
  TOAST.style.borderColor=ok?'#16a34a':'#dc2626';
  TOAST.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>TOAST.classList.remove('show'),3000);
}

async function login(){
  const inp=document.getElementById('secret').value.trim();
  SECRET=inp;
  const ok=await check();
  if(ok){
    document.getElementById('login').style.display='none';
    document.getElementById('panel').style.display='block';
    load();
    setInterval(load,5000);
  }else{
    showToast('Invalid secret',false);
  }
}

async function check(){
  try{
    const r=await fetch('/api/admin/list-requests',{headers:{'X-Admin-Secret':SECRET}});
    return r.ok;
  }catch(e){return false}
}

async function load(){
  try{
    const r=await fetch('/api/admin/list-requests',{headers:{'X-Admin-Secret':SECRET}});
    if(!r.ok){STATUS.textContent='Auth error';return}
    const data=await r.json();
    const pending=data.requests.filter(r=>r.status==='pending');
    if(!pending.length){
      DIV.innerHTML='<div class="empty"><h2>No pending requests</h2><p>All caught up!</p></div>';
      STATUS.textContent='0 pending';
      return;
    }
    STATUS.textContent=pending.length+' pending';
    DIV.innerHTML=pending.map(r=>{
      const t=new Date(r.created_at).toLocaleString();
      return '<div class="card" data-id="'+r.id+'">'+
        '<div><div class="phone">'+esc(r.phone_number)+'</div><div class="time">'+t+'</div></div>'+
        '<div class="actions">'+
          '<button class="btn btn-approve" onclick="respond(\\''+r.id+'\\',\\'approved\\')">Approve</button>'+
          '<button class="btn btn-reject" onclick="respond(\\''+r.id+'\\',\\'rejected\\')">Reject</button>'+
        '</div></div>';
    }).join('');
  }catch(e){
    STATUS.textContent='Network error';
  }
}

function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}

async function respond(id,action){
  try{
    const r=await fetch('/api/admin/respond-request',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({request_id:id, action, secret:SECRET})
    });
    if(r.ok){
      showToast(action==='approved'?'Approved ✓':'Rejected ✗',true);
      load();
    }else{
      const e=await r.json();
      showToast('Error: '+(e.detail||r.status),false);
    }
  }catch(e){
    showToast('Network error',false);
  }
}

if(REQUEST_ID){
  fetch('/api/request-status/'+encodeURIComponent(REQUEST_ID))
    .then(r=>r.json())
    .then(d=>{if(d.status==='approved'){window.location.href='/'}})
    .catch(()=>{});
}
</script>
</body>
</html>"""

@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    request_id = request.query_params.get("request_id", "")
    html = ADMIN_HTML.replace("__REQUEST_ID__", request_id)
    return HTMLResponse(html)


