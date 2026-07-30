import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi import HTTPException, status

router = APIRouter()

ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "vocalKart-admin-secret-2492")

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
</style>
</head>
<body>
<h1>VocalKart Admin</h1>
<p class="sub" id="status">Loading...</p>
<div id="requests"></div>
<div id="toast" class="toast"></div>
<script>
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

async function load(){
  try{
    const r=await fetch('/api/admin/list-requests?request_id='+encodeURIComponent(REQUEST_ID));
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
      body:JSON.stringify({request_id:id, action})
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

load();
setInterval(load,5000);
</script>
</body>
</html>"""

@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    request_id = request.query_params.get("request_id", "")
    ar = request.app.state.access_requests
    record = ar.get(request_id)
    if not record or record['status'] != 'pending':
        return HTMLResponse("<h1>401 Unauthorized</h1><p>Invalid or expired request.</p>", status_code=status.HTTP_401_UNAUTHORIZED)
    html = ADMIN_HTML.replace("__REQUEST_ID__", request_id)
    return HTMLResponse(html)



# Imports & Router Setup (Lines 1-7)
# import os
# Reads ADMIN_SECRET from environment variables for authentication.
# from fastapi import APIRouter, Request
# from fastapi.responses import HTMLResponse
# from fastapi import HTTPException, status
# - APIRouter — a mini-app that can be mounted into the main FastAPI app (registered in token_server.py)
# - Request — gives access to incoming HTTP request data (query params, headers, etc.)
# - HTMLResponse — tells FastAPI to return raw HTML instead of JSON
# - HTTPException / status — for returning proper HTTP error codes
# router = APIRouter()
# Creates the router instance. All endpoints defined with @router.get(...) will be included when token_server.py does app.include_router(admin_router).
# Config (Line 9)
# ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "vocalKart-admin-secret-2492")
# Reads the secret from .env. Falls back to a default if not set — so the admin panel still works without configuration (though you should change it for security).
# HTML Template (Line 11)
# ADMIN_HTML = ""  # Will be filled with the full HTML later
# Currently empty placeholder. You'll put the complete admin panel UI here.
# The Route (Lines 13-19)
# @router.get("/admin", response_class=HTMLResponse)
# - @router.get(...) — registers this function to handle GET /admin requests
# - response_class=HTMLResponse — tells FastAPI to return this as HTML (not JSON)
# async def admin_panel(request: Request):
# Takes the incoming request object to read query parameters.
#     secret = request.query_params.get("secret", "")
# Reads the ?secret= from the URL. For example: https://vocalkart.com/admin?secret=vocalKart-admin-secret-2492
#     if secret != ADMIN_SECRET:
#         return HTMLResponse("<h1>401 Unauthorized</h1><p>Invalid admin secret.</p>", status_code=status.HTTP_401_UNAUTHORIZED)
# Authentication gate — if the secret in the URL doesn't match ADMIN_SECRET from .env, return a 401 error page. This ensures only someone who knows the secret can access the admin panel.
#     html = ADMIN_HTML.replace("__ADMIN_SECRET__", secret)

# Secret injection — replaces the __ADMIN_SECRET__ placeholder in the HTML with the actual secret value. This embeds the secret into the JavaScript so the admin panel JS can use it for subsequent API calls (like list-requests and respond-request).
#     return HTMLResponse(html)
# Returns the final HTML page to the browser.

# Summary: 
# The admin panel is a password-protected page.
# You visit /admin?secret=your-secret, it validates the secret, injects it into the HTML, and serves the admin UI.
# The JS in the HTML then uses that secret to make authenticated API calls to list and respond to requests.




