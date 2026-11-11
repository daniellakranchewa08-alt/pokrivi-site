"""Local server for the Покриви & Дърво site: static pages + inquiry API.

Run:  python3 server.py          (http://localhost:3000)
      PORT=8080 python3 server.py
"""
import json, os, re, threading
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'docs'
DB = ROOT / 'data' / 'inquiries.json'
PORT = int(os.environ.get('PORT', 3000))
LOCK = threading.Lock()
REQUIRED = ('fullName', 'phoneNumber', 'settlement', 'serviceType')


def read_db():
    try:
        return json.loads(DB.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC), **kwargs)

    def send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/api/inquiries':
            return self.send_json(200, read_db())
        # clean URLs: /za-nas -> /za-nas.html
        if path != '/' and '.' not in path.rsplit('/', 1)[-1] and (PUBLIC / (path.lstrip('/') + '.html')).is_file():
            self.path = path + '.html'
        return super().do_GET()

    def do_POST(self):
        if self.path != '/api/inquiry':
            return self.send_json(404, {'error': 'Not found'})
        length = int(self.headers.get('Content-Length') or 0)
        if length > 100_000:
            return self.send_json(413, {'error': 'Твърде голямо запитване'})
        try:
            data = json.loads(self.rfile.read(length) or b'{}')
        except json.JSONDecodeError:
            return self.send_json(400, {'error': 'Невалидни данни'})
        missing = [k for k in REQUIRED if not str(data.get(k, '')).strip()]
        if missing:
            return self.send_json(400, {'error': 'Липсващи полета: ' + ', '.join(missing)})
        if not re.fullmatch(r'[+0-9][0-9 \-]{6,}', str(data['phoneNumber']).strip()):
            return self.send_json(400, {'error': 'Невалиден телефон'})
        if data.get('consent') is not True:
            return self.send_json(400, {'error': 'Липсва съгласие за обработка на данните'})
        entry = {'id': int(datetime.now().timestamp() * 1000),
                 'createdAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                 **{k: str(data.get(k, '')).strip()[:2000] for k in (*REQUIRED, 'description')},
                 'consent': True}
        with LOCK:
            items = read_db(); items.append(entry)
            DB.parent.mkdir(parents=True, exist_ok=True)
            DB.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"New inquiry: {entry['fullName']} – {entry['phoneNumber']}", flush=True)
        return self.send_json(201, {'ok': True, 'id': entry['id']})


if __name__ == '__main__':
    print(f'Serving on http://localhost:{PORT}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
