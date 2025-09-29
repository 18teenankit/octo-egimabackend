from __future__ import annotations
import urllib.request, json

def main():
    with urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=3) as r:
        data = json.loads(r.read().decode())
    print('OK', data)

if __name__ == '__main__':
    main()
