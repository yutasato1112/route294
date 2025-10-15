"""
sidewind.py (2025-10-15 floorfix02)
ツイン0〜2を許容しつつ、フロア制約（2F以内・飛び階なし）を優先的に保持する版。

優先順位:
  1) ツイン偏り3以上の解消（最優先、制約緩和可）
  2) quota(通常部屋)は常に厳守（swapのみ）
  3) ツイン数が0〜2の範囲ならOK、それ以上は再調整
  4) フロア数は常に2以内・飛び階禁止（bath条件付き）
  5) has_bath=True の人は4F以下限定
"""

from collections import defaultdict, Counter

# =========================
# ヘルパ関数群
# =========================
def fl(r): return r // 100

def house_rooms(allocation, hid):
    return [r for r, h in allocation.items() if h == hid]

def house_floors(allocation, hid):
    return sorted({fl(r) for r in house_rooms(allocation, hid)})

def twin_count(allocation, twin_set, hid):
    return sum(1 for r in house_rooms(allocation, hid) if r in twin_set)

def quota_ok(counts, quotas):
    return all(counts.get(hid,0) == quotas[hid] for hid in quotas)

def clone(d): return dict(d)

def safe_swap(allocation, a_room, b_room):
    ha = allocation[a_room]
    hb = allocation[b_room]
    allocation[a_room], allocation[b_room] = hb, ha


# =========================
# 初期割当
# =========================
def initial_assign(rooms, housekeepers):
    allocation = {r: None for r in rooms}
    quotas = {h["id"]: h["room_quota"] for h in housekeepers}
    bath_flags = {h["id"]: h["has_bath"] for h in housekeepers}

    floors = sorted({fl(r) for r in rooms})
    by_floor = defaultdict(list)
    for r in rooms:
        by_floor[fl(r)].append(r)
    for f in floors:
        by_floor[f].sort()

    lows = [h for h in housekeepers if h["has_bath"]]
    others = [h for h in housekeepers if not h["has_bath"]]

    for h in lows:
        hid = h["id"]
        need = quotas[hid]
        for f in [2,3,4]:
            while need > 0 and by_floor[f]:
                r = by_floor[f].pop(0)
                allocation[r] = hid
                need -= 1
        quotas[hid] = need

    order = [5,6,7,8,9,10,2,3,4]
    idx = 0
    cyc = [h["id"] for h in others]
    while any(by_floor[f] for f in order):
        hid = cyc[idx % len(cyc)]
        if quotas[hid] <= 0:
            idx += 1
            continue
        for f in order:
            if by_floor[f]:
                r = by_floor[f].pop(0)
                allocation[r] = hid
                quotas[hid] -= 1
                break
        if quotas[hid] == 0:
            idx += 1

    remain = [r for r,v in allocation.items() if v is None]
    for r in remain:
        for h in housekeepers:
            hid = h["id"]
            if quotas[hid] > 0:
                allocation[r] = hid
                quotas[hid] -= 1
                break
    return allocation


# =========================
# ツイン再配分（偏り優先）
# =========================
def rebalance_twins(allocation, twin_rooms, housekeepers, allow_min_triplex=True):
    twin_set = set(twin_rooms)
    has_bath = {h["id"]: h["has_bath"] for h in housekeepers}

    def floors_of(alloc,hid): return sorted({fl(r) for r,h in alloc.items() if h==hid})
    def floor_ok(fs, allow_triplex):
        if len(fs) <= 2: return True
        if allow_triplex and len(fs)==3 and (max(fs)-min(fs)<=2): return True
        return False
    def safe_for_bath(hid, room_after):
        return (not has_bath.get(hid, False)) or (fl(room_after) <= 4)

    def twin_counts(alloc):
        return {h["id"]: sum(1 for r, hh in alloc.items() if hh==h["id"] and r in twin_set)
                for h in housekeepers}

    def can_swap_big_gap(alloc, rA, rB, allow_triplex, severe=False):
        hA, hB = alloc[rA], alloc[rB]
        if not (safe_for_bath(hA, rB) and safe_for_bath(hB, rA)): return False
        tmp = clone(alloc); safe_swap(tmp, rA, rB)
        fsA, fsB = floors_of(tmp,hA), floors_of(tmp,hB)
        if severe: return True  # 偏り3以上はフロア制約を一時緩和
        return floor_ok(fsA, allow_triplex) and floor_ok(fsB, allow_triplex)

    def can_swap_normal(alloc, rA, rB):
        hA, hB = alloc[rA], alloc[rB]
        if not (safe_for_bath(hA, rB) and safe_for_bath(hB, rA)): return False
        tmp = clone(alloc); safe_swap(tmp, rA, rB)
        for hid in [hA,hB]:
            fs = floors_of(tmp,hid)
            if len(fs)>2 or (max(fs)-min(fs)>2): return False
        return True

    # -------------------------------
    # Phase A: 偏り3以上の解消（最優先）
    # -------------------------------
    iteration = 0
    while True:
        iteration += 1
        tc = twin_counts(allocation)
        mx, mn = max(tc.values()), min(tc.values())
        zero_and_threeplus = (mn == 0 and mx >= 3)
        severe = (mx - mn >= 3)

        if not zero_and_threeplus and ((mn > 0 and mx - mn <= 2) or (mn == 0 and mx <= 2)):
            break

        donors = [hid for hid,c in tc.items() if c >= mn + 3 or (mn==0 and c>=3)]
        receivers = [hid for hid,c in tc.items() if c == mn]

        swapped = False
        for hB in donors:
            twin_rooms_B = [r for r,h in allocation.items() if h==hB and r in set(twin_rooms)]
            for hA in receivers:
                normal_rooms_A = [r for r,h in allocation.items() if h==hA and r not in set(twin_rooms)]
                base_f = min(floors_of(allocation,hB) or [0])
                normal_rooms_A.sort(key=lambda r: abs(fl(r)-base_f))
                for rB in twin_rooms_B:
                    for rA in normal_rooms_A:
                        if can_swap_big_gap(allocation, rA, rB, allow_min_triplex, severe):
                            safe_swap(allocation, rA, rB)
                            print(f"[PASS1-{iteration}] twin swap {rB}({hB}) → {rA}({hA}) (severe={severe})")
                            swapped = True
                            break
                    if swapped: break
                if swapped: break
            if swapped: break
        if not swapped:
            break

    # -------------------------------
    # Phase B: 微調整（差1まで）
    # -------------------------------
    improved = True
    while improved:
        improved = False
        tc = twin_counts(allocation)
        mx, mn = max(tc.values()), min(tc.values())
        if mx - mn <= 1:
            break
        high = [hid for hid,c in tc.items() if c > mn + 1]
        low  = [hid for hid,c in tc.items() if c == mn]
        for rB,hB in allocation.items():
            if hB not in high or rB not in set(twin_rooms): continue
            for rA,hA in allocation.items():
                if hA not in low or rA in set(twin_rooms): continue
                if can_swap_normal(allocation,rA,rB):
                    safe_swap(allocation,rA,rB)
                    print(f"[PASS2] fine-tune {rB}({hB}) → {rA}({hA})")
                    improved = True
                    break
            if improved: break

    return allocation


# =========================
# フロア圧縮（偏りを壊さないガード付き・0〜2許容）
# =========================
def compress_floors(allocation, twin_rooms, housekeepers, max_iter=200):
    twin_set = set(twin_rooms)

    def twin_stats(alloc):
        counts = [twin_count(alloc, twin_set, h["id"]) for h in housekeepers]
        if not counts: return (0,0,0)
        return (max(counts)-min(counts), min(counts), max(counts))

    base_twin = twin_stats(allocation)

    def total_violation(alloc):
        over2 = 0
        far = 0
        span_sum = 0
        for h in housekeepers:
            hid = h["id"]
            fs = house_floors(alloc, hid)
            if not fs:
                continue
            if len(fs) > 2:
                over2 += (len(fs) - 2)
            span = max(fs) - min(fs)
            span_sum += span
            if span > 2:
                far += 1
        return (over2, far, span_sum)

    base_vio = total_violation(allocation)
    improved = True
    steps = 0

    while improved and steps < max_iter:
        improved = False
        steps += 1
        best_delta = (0,0,0)
        best_pair = None

        rooms = list(allocation.keys())
        for i in range(len(rooms)):
            rA = rooms[i]
            hA = allocation[rA]
            for j in range(i+1, len(rooms)):
                rB = rooms[j]
                hB = allocation[rB]
                if hA == hB:
                    continue

                tmp = clone(allocation)
                safe_swap(tmp, rA, rB)
                vio = total_violation(tmp)
                tv_diff, tv_mn, tv_mx = twin_stats(tmp)

                # --- ツイン公平性ガード（0〜2許容） ---
                if tv_mx - tv_mn > 2:
                    continue
                if tv_mn == 0 and tv_mx >= 3:
                    continue

                # 改善量を比較（over2 > far > span）
                delta = (
                    base_vio[0] - vio[0],
                    base_vio[1] - vio[1],
                    base_vio[2] - vio[2]
                )

                # フロア改善を優先
                if (delta[0] > 0 or delta[1] > 0 or delta[2] > 0):
                    if delta > best_delta:
                        best_delta = delta
                        best_pair = (rA, rB)

        if best_pair:
            rA, rB = best_pair
            safe_swap(allocation, rA, rB)
            base_vio = total_violation(allocation)
            improved = True

    return allocation



# =========================
# 公開API: assign_rooms
# =========================
def assign_rooms(rooms, eco_rooms, eco_out_rooms, twin_rooms, bath_rooms, housekeepers,
                 time_single, time_twin, time_eco, time_bath):
    allocation = initial_assign(rooms, housekeepers)
    quotas = {h["id"]: h["room_quota"] for h in housekeepers}
    counts = Counter(allocation.values())
    if not quota_ok(counts, quotas):
        raise RuntimeError("initial_assign quota mismatch")

    allocation = rebalance_twins(allocation, twin_rooms, housekeepers, allow_min_triplex=False)

    def spread(alloc):
        cs = [twin_count(alloc, set(twin_rooms), h["id"]) for h in housekeepers]
        return max(cs)-min(cs), min(cs), max(cs)

    before = spread(allocation)
    allocation_try = rebalance_twins(clone(allocation), twin_rooms, housekeepers, allow_min_triplex=True)
    after = spread(allocation_try)

    if (before[1]==0 and before[2]>=3 and not (after[1]==0 and after[2]>=3)) or (after < before):
        allocation = allocation_try

    counts = Counter(allocation.values())
    if not quota_ok(counts, quotas):
        raise RuntimeError("TWIN-BAL quota mismatch")

    allocation = compress_floors(allocation, twin_rooms, housekeepers)

    diff, mn, mx = (lambda a: (
        max([twin_count(a,set(twin_rooms),h["id"]) for h in housekeepers]) -
        min([twin_count(a,set(twin_rooms),h["id"]) for h in housekeepers]),
        min([twin_count(a,set(twin_rooms),h["id"]) for h in housekeepers]),
        max([twin_count(a,set(twin_rooms),h["id"]) for h in housekeepers])
    ))(allocation)

    if (mn == 0 and mx >= 3) or (diff > 2):
        allocation = rebalance_twins(allocation, twin_rooms, housekeepers, allow_min_triplex=True)

    counts = Counter(allocation.values())
    if not quota_ok(counts, quotas):
        raise RuntimeError("FLOOR-FIX quota mismatch")

    print("TWIN-BAL + FLOOR-FIX done (quota preserved)")
    return allocation