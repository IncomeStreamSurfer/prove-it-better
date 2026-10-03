#!/usr/bin/env python3
"""Hard checks that need no opinion. Standard library only.

  python checks.py links output.txt            # do the URLs in this text load?
  python checks.py links - < output.txt
  python checks.py quotes quotes.txt --corpus source.txt
                                               # does each quote (one per line) appear verbatim in the source?
Add --json for machine-readable output. Put the one-line summary into judge.py's
current_check / challenger_check fields so the judge sees it.
"""
import argparse, concurrent.futures as cf, json, re, sys, unicodedata, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def read(path):
    return sys.stdin.read() if path == "-" else open(path, encoding="utf-8", errors="replace").read()


def url_loads(url, timeout=12):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if r.status < 400:
                    return True, r.status
        except urllib.error.HTTPError as e:
            if method == "GET":
                return False, e.code
        except Exception as e:
            if method == "GET":
                return False, type(e).__name__
    return False, "unknown"


def cmd_links(args):
    text = read(args.file)
    urls = list(dict.fromkeys(u.rstrip(".,;:)]'\"") for u in re.findall(r"https?://[^\s<>\"'\])]+", text)))
    with cf.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(url_loads, urls))
    bad = [(u, s) for u, (ok, s) in zip(urls, res) if not ok]
    ok_n = len(urls) - len(bad)
    if args.json:
        print(json.dumps({"total": len(urls), "load": ok_n, "failed": bad}, indent=2))
    else:
        print(f"{ok_n}/{len(urls)} links load")
        for u, s in bad:
            print(f"  FAIL {s} {u}")


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().strip('"').strip()


def cmd_quotes(args):
    corpus = norm(read(args.corpus))
    quotes = [q for q in (l.strip() for l in read(args.file).splitlines()) if q]
    missing = [q for q in quotes if norm(q) not in corpus]
    found = len(quotes) - len(missing)
    if args.json:
        print(json.dumps({"total": len(quotes), "found": found, "missing": missing}, indent=2))
    else:
        print(f"{found}/{len(quotes)} quotes appear verbatim in the source")
        for q in missing:
            print(f"  MISSING {q[:120]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("links", help="check that every URL in a text loads")
    a.add_argument("file")
    a.add_argument("--json", action="store_true")
    a.set_defaults(fn=cmd_links)
    b = sub.add_parser("quotes", help="check that quotes appear verbatim in a source text")
    b.add_argument("file", help="one quote per line")
    b.add_argument("--corpus", required=True)
    b.add_argument("--json", action="store_true")
    b.set_defaults(fn=cmd_quotes)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
