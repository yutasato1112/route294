#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sidewind.py (2025-10-17 final-stable+eco-balance)
ツイン0〜2を許容しつつ、フロア制約（2F以内・飛び階なし）を優先的に保持。
エコ・エコ外はquota計算範囲外。通常部屋quota厳守。

優先順位:
  1) ツイン偏り3以上の解消（最優先・制約緩和可）
  2) quota(通常部屋)は常に厳守
  3) ツイン数が0〜2の範囲ならOK
  4) フロア数は常に2以内・飛び階禁止
  5) has_bath=True の人は4F以下限定
  6) 終了予定時刻は同一quota内で最速と最遅が10分差以内。
     完全達成不能時は差を最小化。
"""

from collections import defaultdict, Counter

# ------------------------------------------------------------
# ヘルパ関数
# ------------------------------------------------------------
def fl(r): return r // 100
def clone(d): return dict(d)

def house_rooms(alloc, hid):
    return [r for r, h in alloc.items() if h == hid]

def house_floors(alloc, hid):
    return sorted({fl(r) for r in house_rooms(alloc, hid)})

def twin_count(alloc, twin_set, hid):
    return sum(1 for r in house_rooms(alloc, hid) if r in twin_set)

def quota_ok(counts, quotas):
    return all(counts.get(h, 0) == quotas[h] for h in quotas)

def safe_swap(alloc, a, b):
    ha, hb = alloc[a], alloc[b]
    alloc[a], alloc[b] = hb, ha


# ------------------------------------------------------------
# 初期割当（quota厳守）
# ------------------------------------------------------------
def initial_assign(rooms, housekeepers):
    allocation = {r: None for r in rooms}
    quotas = {h["id"]: h["room_quota"] for h in housekeepers}
    assigned = Counter()
    bath_flags = {h["id"]: h["has_bath"] for h in housekeepers}

    floors = sorted({fl(r) for r in rooms})
    low = [f for f in floors if f <= min(floors) + 2]
    order = sorted(floors, reverse=True) + low

    by_floor = defaultdict(list)
    for r in sorted(rooms):
        by_floor[fl(r)].append(r)

    print(f"[DEBUG] rooms={len(rooms)}, total_quota={sum(quotas.values())}")

    # 下層優先（浴場担当）
    for h in housekeepers:
        if not h["has_bath"]:
            continue
        hid = h["id"]
        for f in low:
            while by_floor[f] and assigned[hid] < quotas[hid]:
                allocation[by_floor[f].pop(0)] = hid
                assigned[hid] += 1
            if assigned[hid] >= quotas[hid]:
                break

    # 残りハウス
    remain = [r for f in order for r in by_floor[f] if allocation[r] is None]
    idx = 0
    for h in housekeepers:
        if h["has_bath"]:
            continue
        hid = h["id"]
        need = quotas[hid] - assigned[hid]
        take = remain[idx:idx + need]
        for r in take:
            allocation[r] = hid
            assigned[hid] += 1
        idx += need

    # None補完
    for r, v in allocation.items():
        if v is None:
            tgt = min(quotas, key=lambda x: assigned[x])
            allocation[r] = tgt
            assigned[tgt] += 1

    # quota確認
    for hid in quotas:
        if assigned[hid] != quotas[hid]:
            raise RuntimeError(f"❌ quota mismatch: {hid}")

    print(f"initial_assign_dynamic completed successfully ({len(floors)} floors: {floors})")
    return allocation


# ------------------------------------------------------------
# ツイン偏り修正
# ------------------------------------------------------------
def rebalance_twins(alloc, twin_rooms, housekeepers, allow_min_triplex=True):
    twin_set = set(twin_rooms)
    has_bath = {h["id"]: h["has_bath"] for h in housekeepers}

    def floors_of(a, hid):
        return sorted({fl(r) for r, h in a.items() if h == hid})

    def floor_ok(fs, allow):
        if len(fs) <= 2: return True
        if allow and len(fs) == 3 and max(fs) - min(fs) <= 2: return True
        return False

    def safe_for_bath(hid, r):
        return (not has_bath.get(hid, False)) or fl(r) <= 4

    def twin_counts(a):
        return {h["id"]: sum(1 for r, hh in a.items() if hh == h["id"] and r in twin_set)
                for h in housekeepers}

    # --- main phase ---
    iteration = 0
    while True:
        iteration += 1
        tc = twin_counts(alloc)
        mx, mn = max(tc.values()), min(tc.values())
        severe = mx - mn >= 3
        if (mn > 0 and mx - mn <= 2) or (mn == 0 and mx <= 2):
            break

        donors = [h for h, c in tc.items() if c >= mn + 3 or (mn == 0 and c >= 3)]
        receivers = [h for h, c in tc.items() if c == mn]
        swapped = False
        for hB in donors:
            twinB = [r for r, h in alloc.items() if h == hB and r in twin_set]
            for hA in receivers:
                normalA = [r for r, h in alloc.items() if h == hA and r not in twin_set]
                base_f = min(floors_of(alloc, hB) or [0])
                normalA.sort(key=lambda r: abs(fl(r) - base_f))
                for rB in twinB:
                    for rA in normalA:
                        if not (safe_for_bath(hA, rB) and safe_for_bath(hB, rA)):
                            continue
                        tmp = clone(alloc)
                        safe_swap(tmp, rA, rB)
                        if severe or (floor_ok(floors_of(tmp, hA), allow_min_triplex)
                                      and floor_ok(floors_of(tmp, hB), allow_min_triplex)):
                            safe_swap(alloc, rA, rB)
                            print(f"[PASS1-{iteration}] twin swap {rB}({hB})→{rA}({hA})")
                            swapped = True
                            break
                    if swapped: break
                if swapped: break
            if swapped: break
        if not swapped: break
    return alloc


# ------------------------------------------------------------
# エコ・エコ外再割り当て（時間制約考慮版）
# ------------------------------------------------------------
def rebalance_eco(allocation, eco_rooms, eco_out_rooms, housekeepers,
                  time_single, time_twin, time_eco, time_bath,
                  twin_rooms, max_gap=10):

    eco_set = set(eco_rooms) | set(eco_out_rooms)
    has_bath = {h["id"]: h["has_bath"] for h in housekeepers}
    quotas = {h["id"]: h["room_quota"] for h in housekeepers}

    def _estimate_end(alloc):
        res = defaultdict(float)
        for r, h in alloc.items():
            if h is None: continue
            if r in twin_rooms:
                res[h] += time_twin
            elif r in eco_set:
                res[h] += time_eco
            else:
                res[h] += time_single
        for hk in housekeepers:
            if hk["has_bath"]:
                res[hk["id"]] += time_bath
        return res

    def floors_of(hid, a):
        return sorted({fl(r) for r, h in a.items() if h == hid})

    def floor_ok_after_move(r, giver, taker, a):
        tmp = clone(a); tmp[r] = taker
        def ok(fs): return len(fs) <= 2 and (not fs or max(fs) - min(fs) <= 1)
        fs_g, fs_t = floors_of(giver, tmp), floors_of(taker, tmp)
        if not (ok(fs_g) and ok(fs_t)): return False
        if has_bath.get(taker, False) and fl(r) > 4: return False
        return True

    end_times = _estimate_end(allocation)
    qgroups = defaultdict(list)
    for hk in housekeepers:
        qgroups[hk["room_quota"]].append(hk["id"])

    print("\n=== Eco再割当（時間制約）開始 ===")
    for q, hids in qgroups.items():
        gap = max(end_times[h] for h in hids) - min(end_times[h] for h in hids)
        if gap <= max_gap: continue
        print(f"⚠️ Quota {q} で{gap:.1f}分差 → エコ再配分開始")
        it = 0
        while gap > max_gap and it < 50:
            it += 1
            sorted_h = sorted(hids, key=lambda h: end_times[h])
            fast, slow = sorted_h[0], sorted_h[-1]
            eco_owned = [r for r, h in allocation.items() if h == slow and r in eco_set]
            if not eco_owned: break
            best = None; best_gain = 0; best_gap = gap
            for r in eco_owned:
                if not floor_ok_after_move(r, slow, fast, allocation): continue
                tmp = clone(allocation); tmp[r] = fast
                new = _estimate_end(tmp)
                new_gap = max(new[h] for h in hids) - min(new[h] for h in hids)
                gain = gap - new_gap
                if gain > best_gain:
                    best_gain = gain; best = (r, slow, fast); best_gap = new_gap
            if best and best_gain > 0.05:
                r, slow, fast = best
                allocation[r] = fast
                end_times = _estimate_end(allocation)
                gap = best_gap
                print(f"  [Eco★] {r} {slow}→{fast} 改善={best_gain:.1f} 差={gap:.1f}")
            else:
                print(f"  [DEBUG] 改善なし or 制約不適合 → 終了")
                break
    print("=== Eco再割当終了 ===")
    return allocation


# ------------------------------------------------------------
# 公開API
# ------------------------------------------------------------
def assign_rooms(rooms, eco_rooms, eco_out_rooms, twin_rooms, bath_rooms, housekeepers,
                 time_single, time_twin, time_eco, time_bath):

    # --- 通常部屋割当 ---
    normal_rooms = [r for r in rooms if r not in eco_rooms and r not in eco_out_rooms]
    allocation = initial_assign(normal_rooms, housekeepers)

    # --- エコ部屋を先に統合（重要） ---
    for r in eco_rooms + eco_out_rooms:
        allocation[r] = None

    quotas = {h["id"]: h["room_quota"] for h in housekeepers}
    if not quota_ok(Counter(allocation.values()), quotas):
        raise RuntimeError("initial quota mismatch")

    allocation = rebalance_twins(allocation, twin_rooms, housekeepers, allow_min_triplex=False)

    # --- 終了予定時刻制約を考慮したエコ再配分 ---
    allocation = rebalance_eco(
        allocation, eco_rooms, eco_out_rooms, housekeepers,
        time_single, time_twin, time_eco, time_bath, twin_rooms
    )

    # ------------------------------------------------------------
    # 結果出力
    # ------------------------------------------------------------
    def _estimate_end_times(alloc):
        res = defaultdict(float)
        for r, h in alloc.items():
            if h is None: continue
            if r in twin_rooms:
                res[h] += time_twin
            elif r in eco_rooms or r in eco_out_rooms:
                res[h] += time_eco
            else:
                res[h] += time_single
        for hk in housekeepers:
            if hk.get("has_bath", False):
                res[hk["id"]] += time_bath
        return res

    print("\n=== ハウス別終了見込み(分) ===")
    end_times = _estimate_end_times(allocation)
    for h in sorted(end_times):
        print(f"ハウス{h:2}: {end_times[h]:.1f}分")

    print("✅ TWIN-BAL + ECO-BAL + FLOOR-FIX done")
    return allocation
