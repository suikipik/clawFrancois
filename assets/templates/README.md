# Web Interface Templates

This directory contains HTML templates for the web-based interface of clawdFrancois.

## Files

- **index.html** - Main chat interface with logo branding
  - Mobile-responsive design
  - Dark gradient theme with clawdFrancois branding
  - Real-time message display
  - Status indicator for connection state

## Logo Integration

The templates reference the logo from `/static/logo.png` at runtime:

```html
<img src="/static/logo.png" alt="clawdFrancois Logo">
```

When serving these templates, ensure the static files middleware is configured to serve assets from the `assets/` directory.

## Usage in Flask/FastAPI

### Flask Example
```python
from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, 
    template_folder='assets/templates',
    static_folder='assets')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('assets', path)
```

### FastAPI Example
```python
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="assets"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("assets/templates/index.html")
```

## Customization

The HTML template includes:
- CSS variables for easy theming
- Mobile-first responsive design
- Placeholder JavaScript for backend integration
- Accessibility considerations (alt text, semantic HTML)

Modify the style section to match your branding preferences or add additional functionality as needed.
