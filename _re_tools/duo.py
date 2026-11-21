import argparse, sys, types
sys.path.insert(0, "_re_tools")
import verify

ap = argparse.ArgumentParser()
ap.add_argument("pyc"); ap.add_argument("src"); ap.add_argument("name")
ap.add_argument("--from", dest="start", type=int, default=0)
ap.add_argument("--n", type=int, default=40)
a = ap.parse_args()

orig = dict(verify.walk(verify.load_pyc(a.pyc)))
text = open(a.src, encoding="utf-8").read()
new = dict(verify.walk(compile(text, a.src, "exec", dont_inherit=True)))
A = verify.signature(orig[a.name], True)
B = verify.signature(new[a.name], True)
d = verify.first_diff(A, B)
if d: print("FIRST DIFF @%d  orig=%s  new=%s  (len %d vs %d)" % (d[0], d[1], d[2], len(A), len(B)))
else: print("EXACT (len %d vs %d)" % (len(A), len(B)))
s = max(0, a.start)
for i in range(s, min(len(A), len(B), s + a.n)):
    x = A[i]; y = B[i]
    mark = "  " if x == y else "!!"
    print("%s%4d | %-24s %-20s | %-24s %-20s" % (mark, i, x[0], x[1][:20], y[0], y[1][:20]))

