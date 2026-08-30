# Vercel Python runtime loads the ASGI app from here.
# (Targeted at `api/main.py` via vercel.json functions config.)
from .main import app as asgi_app

# some runtimes look for `app`
app = asgi_app
