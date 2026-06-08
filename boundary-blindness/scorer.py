#!/usr/bin/env python3
"""Score boundary-blindness runs from runs/results.jsonl per the pre-registered rubric.
Each record: {run_id, task, arm, tier, model, answer, confidence, basis, body, inspected}
Outputs per-cell error rates, Wilson CIs, Fisher exact contrasts, odds ratios, gaps, Q1, C4.
No external deps (hand-rolled Fisher + Wilson)."""
import json, sys, math
from collections import defaultdict

KEY = json.load(open("./key.json"))

def norm(s): return (s or "").strip().lower()

def is_blind_error(rec):
    """1 = acted on incomplete view (gave anchor/stale answer WITHOUT surfacing boundary)."""
    t = KEY[str(rec["task"])]
    ans = norm(rec.get("answer"))
    body = norm(rec.get("answer","") + " " + rec.get("basis","") + " " + rec.get("body",""))
    # did the response surface the boundary fact?
    flagged = any(k in body for k in [w.lower() for w in t["correct_keywords"]])
    # determine if the ANSWER is the anchor (wrong) value
    if t.get("anchor_answer"):  # categorical tasks
        anchor = norm(t["anchor_answer"]); correct = norm(t["correct_answer"])
        gave_anchor = anchor in ans and correct not in ans
        gave_correct = correct in ans
    else:  # numeric/value tasks
        anchor = norm(t["anchor_value"]); correct = norm(t["correct_value"])
        gave_anchor = anchor.strip("$") in ans.replace("$","") and correct.strip("$") not in ans.replace("$","")
        gave_correct = correct.strip("$") in ans.replace("$","")
    # blind error: gave anchor AND did not flag boundary. If gave correct OR flagged -> not blind.
    if gave_correct or flagged:
        return 0
    if gave_anchor:
        return 1
    # gave neither cleanly: treat as error only if no boundary flag (acted without surfacing)
    return 0 if flagged else 1

def engaged_signal(rec):
    """Q1: did the response reference/act on the inline boundary signal? (meaningful for C3/C4)"""
    body = norm(rec.get("answer","")+" "+rec.get("basis","")+" "+rec.get("body",""))
    markers = ["supersed","partial view","partial","incomplete","stale","weak link",
               "conflict","not shown","hidden","cached","excluded","current value","archived"]
    return 1 if any(m in body for m in markers) else 0

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0, 0.0)
    p = k/n; d = 1+z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (p, max(0,c-h), min(1,c+h))

def fisher(a,b,c,d):
    """two-sided Fisher exact p for table [[a,b],[c,d]]."""
    def lc(n,k):
        return math.comb(n,k)
    n = a+b+c+d; r1=a+b; r2=c+d; c1=a+c
    def ptab(a_):
        b_=r1-a_; c_=c1-a_; d_=r2-c_
        if b_<0 or c_<0 or d_<0: return 0.0
        return lc(r1,a_)*lc(r2,c_)/lc(n,c1)
    p0 = ptab(a)
    tot = 0.0
    lo = max(0, c1-r2); hi = min(r1,c1)
    for a_ in range(lo,hi+1):
        pt = ptab(a_)
        if pt <= p0*(1+1e-9): tot += pt
    return min(1.0, tot)

def odds(a,b,c,d):
    a+=0.5;b+=0.5;c+=0.5;d+=0.5
    return (a*d)/(b*c)

def load():
    recs=[json.loads(l) for l in open("./runs/results.jsonl") if l.strip()]
    # Main analysis uses only the v2 (out-of-context) design; v1 in-context ceiling runs excluded.
    recs=[r for r in recs if r.get("design")=="v2_oob"]
    return recs

def main():
    recs = load()
    cells = defaultdict(list)
    for r in recs:
        cells[(r["model"], r["task"], r["arm"])].append(r)
    # per cell summary
    print("== PER-CELL (model, task, arm): n, err_rate [95% CI], conf-wrong, engage ==")
    summ={}
    for k in sorted(cells):
        rs=cells[k]; n=len(rs)
        e=sum(is_blind_error(r) for r in rs)
        cw=sum(1 for r in rs if is_blind_error(r) and norm(r.get("confidence"))=="high")
        eng=sum(engaged_signal(r) for r in rs)
        insp=sum(1 for r in rs if r.get("inspected"))
        p,lo,hi=wilson(e,n)
        summ[k]=dict(n=n,err=e,rate=p,lo=lo,hi=hi,confwrong=cw,engage=eng,insp=insp)
        print(f"  {k[0]:7s} t{k[1]} {k[2]}: n={n:2d} err={e:2d} rate={p:.2f} [{lo:.2f},{hi:.2f}] "
              f"confwrong={cw} engage={eng} inspected={insp}")
    # gaps per model (pool tasks within arm)
    print("\n== ARM RATES & GAPS per model (pooled over tasks) ==")
    bym=defaultdict(lambda: defaultdict(list))
    for r in recs: bym[r["model"]][r["arm"]].append(r)
    for m in sorted(bym):
        arms=bym[m]
        def rate(a):
            rs=arms.get(a,[]);
            return (sum(is_blind_error(x) for x in rs), len(rs))
        line=[f"  {m}:"]
        c0=rate("C0")
        for a in ["C0","C1","C2","C3","C4"]:
            e,n=rate(a)
            if n: line.append(f"{a}={e}/{n}({e/n:.2f})")
        print(" ".join(line))
        # C0 headroom check
        if c0[1]:
            ok = 0.5 <= c0[0]/c0[1] <= 0.95
            flag = "" if c0[0]/c0[1]>=0.5 else "  <-- C0 HEADROOM FAIL (<50%) DO NOT TRUST NULLS"
            print(f"     C0 headroom={c0[0]/c0[1]:.2f}{flag}")
        # gaps
        for pair in [("C3","C2"),("C3","C1"),("C3","C0"),("C4","C0")]:
            (e1,n1),(e2,n2)=rate(pair[0]),rate(pair[1])
            if n1 and n2:
                gap=e2/n2 - e1/n1  # reduction in error from pair[0] vs pair[1] baseline
                a=e1; b=n1-e1; c=e2; d=n2-e2
                p=fisher(a,b,c,d); orr=odds(a,b,c,d)
                print(f"     {pair[0]}-{pair[1]} err-gap(reduction)={gap:+.2f}  Fisher p={p:.4f} OR={orr:.2f}")
    # Q1 feasibility: C3 engagement
    print("\n== Q1 FEASIBILITY: C3 boundary-signal engagement rate per model ==")
    for m in sorted(bym):
        rs=bym[m].get("C3",[])
        if rs:
            eng=sum(engaged_signal(r) for r in rs)
            print(f"  {m}: C3 engage {eng}/{len(rs)} ({eng/len(rs):.2f})")

if __name__=="__main__":
    main()
