#!/usr/bin/env python3
"""Approval gate. request / approve / check. Standard library only."""
import argparse, hashlib, json, os, sys, time, uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.environ.get("CONTENT_OS_APPROVALS", os.path.join(ROOT, "approvals"))

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def load_all():
    if not os.path.isdir(DIR):
        return []
    out = []
    for n in os.listdir(DIR):
        if n.endswith(".json"):
            out.append(json.load(open(os.path.join(DIR, n))))
    return out

def request(asset, action, destination):
    if not os.path.isfile(asset):
        sys.exit(f"asset not found: {asset}")
    os.makedirs(DIR, exist_ok=True)
    rec = dict(id=uuid.uuid4().hex[:8], asset=os.path.abspath(asset), sha256=sha(asset),
               action=action, destination=destination, status="pending",
               requested=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(rec, open(os.path.join(DIR, rec["id"] + ".json"), "w"), indent=2)
    print(rec["id"])

def approve(rid, by):
    p = os.path.join(DIR, rid + ".json")
    if not os.path.isfile(p):
        sys.exit(f"no such request: {rid}")
    rec = json.load(open(p))
    rec.update(status="approved", approved_by=by, approved=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(rec, open(p, "w"), indent=2)
    print("approved", rid)

def check(asset, action):
    if not os.path.isfile(asset):
        print("DENIED: asset not found"); return 1
    h, a = sha(asset), os.path.abspath(asset)
    for r in load_all():
        if r["asset"] == a and r["action"] == action and r["status"] == "approved":
            if r["sha256"] == h:
                print("OK", r["id"]); return 0
            print(f"DENIED: asset changed since approval {r['id']}"); return 1
    print("DENIED: no approved record"); return 1

def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("request"); r.add_argument("asset"); r.add_argument("--action", required=True); r.add_argument("--destination", default="")
    p = sp.add_parser("approve"); p.add_argument("id"); p.add_argument("--by", required=True)
    c = sp.add_parser("check"); c.add_argument("asset"); c.add_argument("--action", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "request": request(a.asset, a.action, a.destination)
    elif a.cmd == "approve": approve(a.id, a.by)
    else: return check(a.asset, a.action)
    return 0

if __name__ == "__main__":
    sys.exit(main())
