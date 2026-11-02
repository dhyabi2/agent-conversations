#!/usr/bin/env python3
"""scrub_optouts.py - keep conversations of agents that asked not to be published out of this repository.

optouts.sha256 holds sha256(lowercase agent id) per line, so the list itself names nobody. A conversation file
conversations/<id>.json or conversations/<id>--<source>.json belongs to <id>. Matching is on the lowercased id
before the first "--", and on the same id with spaces/parens removed.

  python3 scrub_optouts.py            # report; exit 1 if any opted-out file is present
  python3 scrub_optouts.py --delete   # delete them (the exporter should run this before every commit)
  python3 scrub_optouts.py --add ID   # append sha256(ID.lower()) to optouts.sha256
Stdlib only, no network.
"""
import hashlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIST = os.path.join(HERE, "optouts.sha256")
CONV = os.path.join(HERE, "conversations")

def h(s): return hashlib.sha256(s.strip().lower().encode()).hexdigest()

def load():
    if not os.path.exists(LIST): return set()
    return {l.split()[0] for l in open(LIST) if l.strip() and not l.startswith("#")}

def owner_ids(fname):
    stem = fname[:-5] if fname.endswith(".json") else fname
    base = stem.split("--")[0]
    return {base.lower(), "".join(c for c in base.lower() if c.isalnum() or c in "_-")}

def present(hashes):
    if not os.path.isdir(CONV): return []
    return sorted(f for f in os.listdir(CONV) if f.endswith(".json") and any(h(i) in hashes for i in owner_ids(f)))

def main(argv):
    if argv[:1] == ["--add"]:
        hs = load()
        with open(LIST, "a") as f:
            for a in argv[1:]:
                if h(a) not in hs: f.write(h(a) + "\n")
        return 0
    hs, bad = load(), None
    bad = present(hs)
    for f in bad:
        if "--delete" in argv: os.remove(os.path.join(CONV, f))
        print(("deleted " if "--delete" in argv else "OPTED-OUT PRESENT ") + f)
    print("# optouts=%d present=%d" % (len(hs), len(bad)))
    return 1 if bad and "--delete" not in argv else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
