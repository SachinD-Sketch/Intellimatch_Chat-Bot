import argparse
import json
import requests
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--query', required=True, help='Natural language request')
    ap.add_argument('--url', default='http://localhost:8002/chat')
    ap.add_argument('--skills', default='data/sample_skill_matrix.json')
    ap.add_argument('--availability', default='data/availability.json')
    ap.add_argument('--top-k', type=int, default=5)
    ap.add_argument('--send-http-data', action='store_true', help='If set, sends skill_matrix and availability in the HTTP payload. If omitted, API reads from data folder.')
    args = ap.parse_args()

    payload = {
        'query': args.query,
        'top_k': args.top_k,
    }

    if args.send_http_data:
        with open(args.skills, 'r', encoding='utf-8') as f:
            payload['skill_matrix'] = json.load(f)
        with open(args.availability, 'r', encoding='utf-8') as f:
            payload['availability'] = json.load(f)

    r = requests.post(args.url, json=payload, timeout=300)
    print(json.dumps(r.json(), indent=2))


if __name__ == '__main__':
    main()
