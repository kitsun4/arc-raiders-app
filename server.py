from flask import Flask, Response, request
import requests
import os

app = Flask(__name__)

METAFORGE_URL = "https://metaforge.app/arc-raiders/event-timers"

@app.route('/')
def index():
    """Serve the main page"""
    try:
        # Fetch the original MetaForge page
        response = requests.get(METAFORGE_URL, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        
        html = response.text
        
        # Inject PWA code
        pwa_injection = '''
    <meta name="theme-color" content="#000000">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="ARC Raiders">
    <link rel="manifest" href="/manifest.json">
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }
    </script>
</head>'''
        
        html = html.replace('</head>', pwa_injection)
        
        return Response(html, mimetype='text/html')
        
    except Exception as e:
        error_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #1a1a2e;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .error {{
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid red;
            border-radius: 10px;
            padding: 20px;
            margin: 20px;
        }}
        button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <h1>🎮 ARC Raiders Event Tracker</h1>
    <div class="error">
        <h2>Error Loading Page</h2>
        <p>Could not fetch data from MetaForge</p>
        <p>Error: {str(e)}</p>
        <p><button onclick="location.reload()">Retry</button></p>
    </div>
</body>
</html>'''
        return Response(error_html, status=500, mimetype='text/html')

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    manifest_json = '''{
    "name": "ARC Raiders Event Timers",
    "short_name": "ARC Raiders",
    "description": "Track ARC Raiders events and timers",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#000000",
    "theme_color": "#000000",
    "orientation": "portrait",
    "icons": [{
        "src": "https://metaforge.app/favicon.ico",
        "sizes": "192x192",
        "type": "image/png"
    }]
}'''
    return Response(manifest_json, mimetype='application/json')

@app.route('/sw.js')
def service_worker():
    """Serve service worker"""
    sw_content = '''
self.addEventListener('install', (event) => {
    console.log('Service Worker installed');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker activated');
    return self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return new Response('Offline - Please check your connection', {
                headers: { 'Content-Type': 'text/plain' }
            });
        })
    );
});
'''
    return Response(sw_content, mimetype='application/javascript')

@app.route('/<path:path>')
def proxy(path):
    """Proxy other requests to MetaForge"""
    try:
        proxied_url = f"https://metaforge.app/{path}"
        response = requests.get(proxied_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        
        return Response(response.content, 
                       status=response.status_code,
                       content_type=response.headers.get('Content-Type', 'text/html'))
    except:
        return Response('Not Found', status=404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
