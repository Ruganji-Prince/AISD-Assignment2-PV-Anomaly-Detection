"""Azure-only cross-origin adapter; original inference application is unchanged."""
import json
import os
from urllib.parse import urlsplit
from fastapi.middleware.cors import CORSMiddleware
from web.app import app as inference_app

DEFAULT_ORIGINS = ["https://pv-anomaly-detection-prince-r-k.vercel.app",
                   "http://localhost:8080", "http://127.0.0.1:8080"]

def trusted_origins(value=None):
    origins = DEFAULT_ORIGINS if value is None else json.loads(value)
    if not isinstance(origins, list) or not origins:
        raise ValueError("An explicit nonempty frontend-origin list is required")
    for origin in origins:
        if not isinstance(origin,str) or "*" in origin:
            raise ValueError("Wildcard origins are prohibited")
        url=urlsplit(origin)
        if url.username or url.password or url.query or url.fragment or url.path or not url.netloc:
            raise ValueError("Origins must contain only scheme and host/port")
        local=url.hostname in {"localhost","127.0.0.1"}
        if not ((local and url.scheme=="http") or (url.scheme=="https" and url.hostname.endswith(".vercel.app"))):
            raise ValueError("Only explicit Vercel HTTPS and local development origins are permitted")
    return list(dict.fromkeys(origins))

ORIGINS=trusted_origins(os.environ.get("PV_FRONTEND_ORIGINS"))
app=CORSMiddleware(inference_app,allow_origins=ORIGINS,allow_methods=["GET","POST"],
                   allow_headers=["Content-Type"],allow_credentials=False,
                   expose_headers=["Server-Timing","X-PV-Instance","X-PV-Initialized","Retry-After"],max_age=600)
