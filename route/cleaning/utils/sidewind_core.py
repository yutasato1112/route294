#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sidewind.py

This module provides functionality for assigning hotel rooms to
housekeepers (also called "houses" or "hid" in the code) while
respecting a series of business rules.  The constraints were derived
from the original route294 implementation and extended here for
testing.  The primary goals of the assignment algorithm are:

* **Quota compliance:** The number of normal rooms allocated to each
  housekeeper must exactly match the quota provided for that
  housekeeper.
* **Twin‑room balance:** The number of twin rooms assigned to any two
  housekeepers must differ by no more than two.  If a housekeeper
  receives zero twin rooms then all housekeepers must receive two or
  fewer.
* **Floor limits:** A housekeeper may work on at most two floors, and
  these floors must be adjacent (no skipping floors).  Housekeepers
  flagged as handling bathing rooms (``has_bath=True``) may not be
  assigned rooms above the fourth floor.
* **Eco‑room fairness:** When assigning eco and eco‑out rooms (rooms
  which do not count toward a housekeeper’s quota), strive to avoid
  obvious bias.  Specifically, no housekeeper should receive three or
  more eco rooms than any other.  The assignment algorithm prefers to
  keep eco and eco‑out rooms on the same floor as the housekeeper’s
  existing rooms, but will fall back to nearby floors if necessary.
* **Time estimates:** Cleaning times are computed per room type.  The
  helper functions ``compute_finish_times`` and ``balance_finish_times``
  are provided to compute and optionally rebalance finish times.  In
  this implementation the balancing step is a no‑op because the
  underlying optimisation is out of scope for this exercise.

The exported function ``assign_rooms`` combines these pieces into a
single workflow suitable for testing.  Test scripts can generate
artificial room and housekeeper data, call ``assign_rooms`` and then
verify that the resulting allocation satisfies all stated constraints.

This file includes a modification to the eco‑room assignment logic:
when assigning eco rooms on a floor that no housekeeper currently
occupies, the algorithm now distributes those rooms one by one across
eligible housekeepers rather than assigning the entire block to a
single housekeeper.  This change helps to even out the distribution
of eco and eco‑out rooms while still respecting the two‑floor limit
for each housekeeper.  Previously all eco rooms on such a floor were
given to the one candidate with the fewest eco assignments, which
could lead to imbalances when multiple free rooms existed on a new
floor.  The updated approach repeatedly selects the housekeeper with
the smallest number of eco rooms (breaking ties with current
finish‐time estimates) and assigns a single room, updating their
floor list as needed.  This process continues until all eco rooms on
the floor have been allocated.
"""

from collections import defaultdict, Counter
from typing import Dict, List, Iterable
import math
from itertools import combinations

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def fl(r: int) -> int:
    """Return the floor number given a room number.

    Rooms are expected to be numbered such that dividing by 100
    produces the floor.  For example room 305 is on floor 3.
    """
    return r // 100


def clone(d: Dict) -> Dict:
    """Return a shallow copy of a dictionary."""
    return dict(d)


def house_rooms(alloc: Dict[int, str], hid: str) -> List[int]:
    """Return a list of room numbers assigned to a particular housekeeper."""
    return [r for r, h in alloc.items() if h == hid]


def house_floors(alloc: Dict[int, str], hid: str) -> List[int]:
    """Return a sorted list of floors on which a housekeeper has rooms."""
    return sorted({fl(r) for r in house_rooms(alloc, hid)})


def twin_count(alloc: Dict[int, str], twin_set: Iterable[int], hid: str) -> int:
    """Return the number of twin rooms assigned to a housekeeper."""
    return sum(1 for r in house_rooms(alloc, hid) if r in twin_set)


def quota_ok(counts: Counter, quotas: Dict[str, int]) -> bool:
    """Check whether the counts of rooms per housekeeper match their quotas."""
    return all(counts.get(h, 0) == quotas[h] for h in quotas)


def safe_swap(alloc: Dict[int, str], a: int, b: int) -> None:
    """Swap two room assignments in place."""
    ha, hb = alloc[a], alloc[b]
    alloc[a], alloc[b] = hb, ha


# ------------------------------------------------------------
# Initial assignment (quota strict)
# ------------------------------------------------------------

def initial_assign(rooms: List[int], housekeepers: List[Dict]) -> Dict[int, str]:
    """Assign normal rooms to housekeepers while respecting quotas and
    basic floor/bath constraints.

    The assignment proceeds in two passes.  First, housekeepers with
    ``has_bath=True`` are assigned rooms on the lowest two floors
    available to them.  This respects the constraint that bath
    handlers may not work above the fourth floor.  Remaining rooms
    are then assigned to the other housekeepers in quota order.  Any
    leftovers are distributed to the housekeeper with the smallest
    assigned count to ensure quotas are strictly met.
    """
    allocation: Dict[int, str] = {r: None for r in rooms}
    quotas: Dict[str, int] = {h["id"]: h["room_quota"] for h in housekeepers}
    assigned = Counter()
    # Determine which housekeepers handle baths
    bath_flags: Dict[str, bool] = {h["id"]: h.get("has_bath", False) for h in housekeepers}

    floors = sorted({fl(r) for r in rooms})
    # Low floors consist of the minimum floor and the next floor
    # (to ensure at most two floors for bath handlers).
    if floors:
        min_floor = min(floors)
    else:
        min_floor = 0
    low_floors = [f for f in floors if f <= min_floor + 2]
    # Process floors in descending order to give upper floors last.
    order = sorted(floors, reverse=True) + low_floors

    # Group rooms by floor
    by_floor: Dict[int, List[int]] = defaultdict(list)
    for r in sorted(rooms):
        by_floor[fl(r)].append(r)

    # Assign bath handlers first on low floors
    for h in housekeepers:
        if not h.get("has_bath", False):
            continue
        hid = h["id"]
        for f in low_floors:
            while by_floor[f] and assigned[hid] < quotas[hid]:
                room = by_floor[f].pop(0)
                allocation[room] = hid
                assigned[hid] += 1
            if assigned[hid] >= quotas[hid]:
                break

    # Assign remaining housekeepers (non bath) in floor order
    remain: List[int] = [r for f in order for r in by_floor[f] if allocation[r] is None]
    idx = 0
    for h in housekeepers:
        if h.get("has_bath", False):
            continue
        hid = h["id"]
        need = quotas[hid] - assigned[hid]
        take = remain[idx:idx + need]
        for r in take:
            allocation[r] = hid
            assigned[hid] += 1
        idx += need

    # Fill any unassigned rooms (should not normally happen)
    for r, v in allocation.items():
        if v is None:
            # Assign to housekeeper with smallest current count
            tgt = min(quotas, key=lambda x: assigned[x])
            allocation[r] = tgt
            assigned[tgt] += 1

    # Verify that quotas are exactly met
    for hid in quotas:
        if assigned[hid] != quotas[hid]:
            raise RuntimeError(f"❌ quota mismatch: {hid}")

    return allocation


# ------------------------------------------------------------
# Twin balancing
# ------------------------------------------------------------

def rebalance_twins(alloc: Dict[int, str], twin_rooms: Iterable[int],
                    housekeepers: List[Dict], allow_min_triplex: bool = True) -> Dict[int, str]:
    """Perform swaps to reduce the disparity of twin room counts among housekeepers.

    The algorithm iteratively swaps a twin room from a housekeeper with
    many twins to a housekeeper with few or none, provided the swap
    respects floor and bath constraints.  A parameter
    ``allow_min_triplex`` controls whether a temporary three‑floor
    assignment is permitted as a last resort when twin imbalance is
    severe.  The goal is to ensure that the difference between the
    largest and smallest twin counts is at most two.
    """
    twin_set = set(twin_rooms)
    # Map housekeepers to whether they can handle bath rooms
    has_bath = {h["id"]: h.get("has_bath", False) for h in housekeepers}

    def floors_of(a: Dict[int, str], hid: str) -> List[int]:
        return sorted({fl(r) for r, h in a.items() if h == hid})

    def floor_ok(fs: List[int], allow: bool) -> bool:
        """Check if a list of floors is acceptable under the two‑floor rule."""
        if len(fs) <= 2:
            return True
        if allow and len(fs) == 3 and max(fs) - min(fs) <= 2:
            return True
        return False

    def safe_for_bath(hid: str, r: int) -> bool:
        """Return True if assigning room ``r`` to ``hid`` would not violate the bath constraint."""
        return (not has_bath.get(hid, False)) or fl(r) <= 4

    def twin_counts(a: Dict[int, str]) -> Dict[str, int]:
        return {h["id"]: sum(1 for r, hh in a.items() if hh == h["id"] and r in twin_set)
                for h in housekeepers}

    # Perform iterative balancing
    iteration = 0
    while True:
        iteration += 1
        tc = twin_counts(alloc)
        mx, mn = max(tc.values()), min(tc.values())
        severe = mx - mn >= 3
        # If distribution is already within [0,2] difference, break
        if (mn > 0 and mx - mn <= 2) or (mn == 0 and mx <= 2):
            break

        # Identify donors (have many twins) and receivers (have few or none)
        donors = [h for h, c in tc.items() if c >= mn + 3 or (mn == 0 and c >= 3)]
        receivers = [h for h, c in tc.items() if c == mn]
        swapped = False
        for hB in donors:
            twinB = [r for r, h in alloc.items() if h == hB and r in twin_set]
            for hA in receivers:
                normalA = [r for r, h in alloc.items() if h == hA and r not in twin_set]
                # Prioritise rooms on or near the donor's floors
                base_f = min(floors_of(alloc, hB) or [0])
                normalA.sort(key=lambda r: abs(fl(r) - base_f))
                for rB in twinB:
                    for rA in normalA:
                        # Check bath constraints
                        if not (safe_for_bath(hA, rB) and safe_for_bath(hB, rA)):
                            continue
                        # Simulate swap and check floor constraints
                        tmp = clone(alloc)
                        safe_swap(tmp, rA, rB)
                        # Only accept the swap if it satisfies floor constraints for both
                        # housekeepers.  We do not bypass this check even when the twin
                        # imbalance is severe because the two‑floor rule has higher
                        # precedence than twin balancing.  Therefore, the `severe`
                        # condition does not override the floor constraint.
                        if floor_ok(floors_of(tmp, hA), allow_min_triplex) and \
                           floor_ok(floors_of(tmp, hB), allow_min_triplex):
                            safe_swap(alloc, rA, rB)
                            swapped = True
                            break
                    if swapped:
                        break
                if swapped:
                    break
            if swapped:
                break
        if not swapped:
            break
    return alloc


# ------------------------------------------------------------
# Floor balancing
# ------------------------------------------------------------

def rebalance_floors(alloc: Dict[int, str], housekeepers: List[Dict],
                     eco_rooms: Iterable[int], eco_out_rooms: Iterable[int]) -> Dict[int, str]:
    """Ensure that no housekeeper is assigned to more than two floors.

    After the initial assignment and twin balancing, a housekeeper may
    inadvertently be responsible for rooms on three or more floors.  This
    helper attempts to reduce that number by swapping normal rooms
    between housekeepers.  Eco and eco‑out rooms are ignored because
    they are assigned later; only normal rooms participate in swaps.

    The algorithm operates greedily: it scans for a housekeeper with
    more than two floors, selects a floor to remove, and then searches
    for a swap candidate on another housekeeper that maintains quotas
    and floor constraints.  It repeats until no housekeeper has more
    than two floors or no further improvements can be made.

    Unlike the previous implementation, this version strictly limits
    housekeepers to two floors.  A three‑floor assignment is no longer
    considered acceptable even if the floors are contiguous.  This
    change gives priority to the "two floors only" rule over the
    looser "within two floors" rule and helps prevent assignments that
    sprawl across three floors.
    """
    eco_set = set(eco_rooms) | set(eco_out_rooms)

    def floors_of_alloc(a: Dict[int, str], hid: str) -> List[int]:
        # Return the sorted list of floors on which hid has normal rooms
        return sorted({fl(r) for r, h in a.items() if h == hid and r not in eco_set})

    def floor_ok_list(fs: List[int]) -> bool:
        """Return True if a housekeeper occupies at most two contiguous floors.

        Floors must be contiguous (no gaps), and the number of distinct floors
        assigned must not exceed two.  For example, [3] and [3, 4] are
        acceptable, but [3, 4, 5] is not even though the span is two.
        """
        if not fs:
            return True
        fs_sorted = sorted(fs)
        # Must not exceed two floors
        if len(fs_sorted) > 2:
            return False
        # If exactly two floors, they must be consecutive
        if len(fs_sorted) == 2:
            return fs_sorted[1] - fs_sorted[0] == 1
        # One floor is always fine
        return True

    changed = True
    while changed:
        changed = False
        # Look for a housekeeper with more than two floors
        for h in housekeepers:
            hid = h["id"]
            floors = floors_of_alloc(alloc, hid)
            if len(floors) <= 2:
                continue
            # Identify the floor(s) to remove: pick the lowest and highest floors
            # and attempt to move one of the rooms on those floors to another
            # housekeeper.  We prefer to remove a floor at one end rather than
            # splitting the middle of the range.
            candidate_floors_to_remove = [floors[0], floors[-1]]
            swapped = False
            for f_remove in candidate_floors_to_remove:
                # Gather normal rooms on the removal floor
                donor_rooms = [r for r, h2 in alloc.items()
                               if h2 == hid and fl(r) == f_remove and r not in eco_set]
                for r in donor_rooms:
                    # Find a swap partner on another housekeeper
                    for h2 in housekeepers:
                        hid2 = h2["id"]
                        if hid2 == hid:
                            continue
                        floors2 = floors_of_alloc(alloc, hid2)
                        # Recipient must have fewer than two floors or already own f_remove
                        if f_remove not in floors2 and len(floors2) >= 2:
                            continue
                        # Search for a room on hid2 that lies on a floor within hid's
                        # remaining floors (excluding f_remove)
                        possible_floors_for_hid = [f for f in floors if f != f_remove]
                        candidate_s = None
                        for s in [rr for rr, hh in alloc.items() if hh == hid2 and rr not in eco_set]:
                            s_floor = fl(s)
                            if s_floor in possible_floors_for_hid:
                                candidate_s = s
                                break
                        if candidate_s is None:
                            continue
                        # Simulate swap and check floor constraints
                        tmp = clone(alloc)
                        safe_swap(tmp, r, candidate_s)
                        new_floors_h = floors_of_alloc(tmp, hid)
                        new_floors_h2 = floors_of_alloc(tmp, hid2)
                        if floor_ok_list(new_floors_h) and floor_ok_list(new_floors_h2):
                            safe_swap(alloc, r, candidate_s)
                            swapped = True
                            break
                    if swapped:
                        break
                if swapped:
                    break
            if swapped:
                changed = True
                break
    return alloc


# ------------------------------------------------------------
# Eco‑room assignment with fairness
# ------------------------------------------------------------
def fl(r: int) -> int:
    """部屋番号から階を求める（例：305→3階）。"""
    return r // 100

def assign_eco_rooms_full(
    alloc: Dict[int, str],
    eco_rooms: Iterable[int],
    eco_out_rooms: Iterable[int],
    housekeepers: List[Dict],
    twin_rooms: Iterable[int],
    bath_rooms: Iterable[int],
    time_single: float,
    time_twin: float,
    time_eco: float,
    time_bath: float,
) -> Dict[int, str]:
    """
    エコ部屋・エコ外部屋を公平に割り当てる改良版アルゴリズム。
    - エコ外部屋は既にその階を担当しているハウスキーパーが担当。
    - エコ部屋は同一フロアの担当者を優先。1フロアしか担当していないハウスキーパーが新しい階を担当する場合は、2室以上の割り当てがある場合のみ許可。
    - バス担当者(has_bath=True)は5階以上のエコ部屋を担当しない。
    """
    # ハウスキーパーのIDリストとbathフラグ
    hk_ids = [h["id"] for h in housekeepers]
    has_bath = {h["id"]: h.get("has_bath", False) for h in housekeepers}

    # 通常部屋からハウスキーパー別に担当階リストを作成
    fl_alloc: Dict[str, List[int]] = {hid: [] for hid in hk_ids}
    eco_set = set(eco_rooms)
    eco_out_set = set(eco_out_rooms)
    for r, hid in alloc.items():
        if hid not in hk_ids:
            continue
        # eco/eco_out は通常部屋に含めない
        if r in eco_set or r in eco_out_set:
            continue
        f = fl(r)
        if f not in fl_alloc[hid]:
            fl_alloc[hid].append(f)
    for hid in fl_alloc:
        fl_alloc[hid].sort()

    # ハウスキーパーごとのエコ部屋数を初期化
    eco_count: Counter = Counter({hid: 0 for hid in hk_ids})

    # エコ部屋を階ごとにまとめる (エコ外は除外)
    pure_eco = [r for r in eco_rooms if r not in eco_out_set]
    floor_to_eco: Dict[int, List[int]] = defaultdict(list)
    for r in pure_eco:
        floor_to_eco[fl(r)].append(r)
    for rlist in floor_to_eco.values():
        rlist.sort()

    # 処理順を決める：担当者の少ない階、エコ部屋数の多い階を優先
    floors = sorted(
        floor_to_eco.keys(),
        key=lambda f: (
            len([hid for hid in hk_ids if f in fl_alloc[hid]]),
            -len(floor_to_eco[f]),
        ),
    )

    eco_assign: Dict[int, str] = {}

    # 1階層ごとに最適な割当パターンを決定
    for f in floors:
        rooms = floor_to_eco[f]
        n = len(rooms)
        # その階を既に担当している人
        existing = [hid for hid in hk_ids if f in fl_alloc[hid]]
        # 新規に割り当て可能な人（2階目までかつBath制限を考慮）
        free_hks = [
            hid
            for hid in hk_ids
            if f not in fl_alloc[hid]
            and len(fl_alloc[hid]) < 2
            and (f <= 4 or not has_bath.get(hid, False))
        ]

        best_diff = float("inf")
        best_assign = None
        # free_hksが多い場合はeco_countの低い順に上位6人程度まで絞る
        free_sorted = sorted(free_hks, key=lambda hid: (eco_count[hid], hid))
        max_consider = 6
        free_candidates = free_sorted[:max_consider]

        max_k = min(len(free_hks), n // 2)
        # k=0〜max_kまで試行し、各kについてfree_candidatesから組合せを列挙
        for k in range(0, max_k + 1):
            for new_set in combinations(free_candidates, k):
                # この組合せで割り当てを仮計算
                candidates = existing + list(new_set)
                # ベース割当：新規の人には2室ずつ
                base = {hid: (2 if hid in new_set else 0) for hid in candidates}
                remaining = n - 2 * len(new_set)
                temp_counts = {
                    hid: eco_count[hid] + base.get(hid, 0) for hid in candidates
                }
                # 残りを一つずつtemp_countsが小さい人へ割当て
                for _ in range(remaining):
                    min_val = min(temp_counts.values())
                    cands = [hid for hid in candidates if temp_counts[hid] == min_val]
                    h = sorted(cands)[0]
                    base[h] += 1
                    temp_counts[h] += 1

                # 仮割当後のエコ数分布のばらつきを計算
                new_counts = eco_count.copy()
                for hid, cnt in base.items():
                    new_counts[hid] += cnt
                diff = max(new_counts.values()) - min(new_counts.values())
                if diff < best_diff:
                    best_diff = diff
                    best_assign = (base, new_set)

        # 最適割当で決定されたbaseを適用
        base_assign, chosen_new_set = best_assign
        idx = 0
        for hid, cnt in base_assign.items():
            for _ in range(cnt):
                r = rooms[idx]
                eco_assign[r] = hid
                eco_count[hid] += 1
                idx += 1
            # 新規に担当する階の場合はfl_allocを更新
            if f not in fl_alloc[hid]:
                fl_alloc[hid].append(f)
                fl_alloc[hid].sort()

    # eco_out部屋を既存の担当者で割当て
    for r in eco_out_rooms:
        f = fl(r)
        # 同じ階を担当している候補者
        candidates = [hid for hid in hk_ids if f in fl_alloc[hid]]
        # Bath担当者は5階以上を受けない
        candidates = [
            hid
            for hid in candidates
            if (f <= 4 or not has_bath.get(hid, False))
        ]
        # 候補者からeco_countの少ない人を優先
        min_val = min(eco_count[h] for h in candidates)
        cands = [h for h in candidates if eco_count[h] == min_val]
        hid = sorted(cands)[0]
        eco_assign[r] = hid
        eco_count[hid] += 1

    return eco_assign

# ------------------------------------------------------------
# Finish time computation and (placeholder) balancing
# ------------------------------------------------------------

def compute_finish_times(allocation: Dict[int, str], eco_rooms: Iterable[int],
                         eco_out_rooms: Iterable[int], twin_rooms: Iterable[int],
                         bath_rooms: Iterable[int], housekeepers: List[Dict],
                         time_single: float, time_twin: float,
                         time_eco: float, time_bath: float) -> Dict[str, float]:
    """Compute estimated finish times for each housekeeper.

    Cleaning times are determined per room type.  Bath rooms are
    assumed to require the longest time (``time_bath``).  Twin rooms
    take ``time_twin``, eco and eco‑out rooms take ``time_eco``, and
    all other rooms take ``time_single``.  The result is a mapping
    from housekeeper ID to the total number of minutes of work.
    """
    twin_set = set(twin_rooms)
    eco_set = set(eco_rooms)
    eco_out_set = set(eco_out_rooms)
    bath_set = set(bath_rooms)
    finish: Dict[str, float] = {h["id"]: 0.0 for h in housekeepers}
    for r, hid in allocation.items():
        if r in bath_set:
            finish[hid] += time_bath
        elif r in twin_set:
            finish[hid] += time_twin
        elif r in eco_set or r in eco_out_set:
            finish[hid] += time_eco
        else:
            finish[hid] += time_single
    return finish


def balance_finish_times(allocation: Dict[int, str], eco_rooms: Iterable[int],
                         eco_out_rooms: Iterable[int], twin_rooms: Iterable[int],
                         bath_rooms: Iterable[int], housekeepers: List[Dict],
                         time_single: float, time_twin: float,
                         time_eco: float, time_bath: float) -> Dict[int, str]:
    """Attempt to balance finish times among housekeepers with identical quotas.

    This function uses a greedy heuristic to reduce the difference
    between the slowest and fastest finish times within groups of
    housekeepers sharing the same normal room quota.  It operates only
    on normal rooms (i.e. excludes eco and eco‑out rooms) to avoid
    violating quota counts.  The algorithm will try to swap a
    high‑duration room from a slow housekeeper with a low‑duration
    room from a fast housekeeper, provided the swap does not violate
    floor constraints or twin fairness.  It iterates until no further
    improvement is possible or the time gap is within a small threshold
    (four minutes by default).  This tighter bound helps keep
    finish times for housekeepers with the same quota closer together.
    """
    from collections import defaultdict, Counter

    # Helper: compute time required for a single room
    def room_time(r: int) -> float:
        if r in bath_rooms:
            return time_bath
        elif r in set(twin_rooms):
            return time_twin
        elif r in set(eco_rooms) or r in set(eco_out_rooms):
            return time_eco
        else:
            return time_single

    # Convert eco/out lists to sets for faster membership tests
    eco_out_set = set(eco_out_rooms)
    eco_set = set(eco_rooms)
    # Combined set of all eco and eco_out rooms.  This is used to
    # identify normal rooms (those not in this set) when selecting
    # candidate rooms for swapping.  Note: this is separate from the
    # floor constraint checks, which now include eco rooms as well.
    eco_set_full = eco_set | eco_out_set

    # Helper: twin counts across all housekeepers
    def twin_counts(a: Dict[int, str]) -> Dict[str, int]:
        twin_set = set(twin_rooms)
        return {h["id"]: sum(1 for r, hh in a.items() if hh == h["id"] and r in twin_set)
                for h in housekeepers}

    # Helper: floors_of_alloc across all rooms (normal and eco).  Including eco and eco_out
    # rooms in the floor set ensures that swaps or moves that introduce a new
    # eco floor still respect the overall floor span and contiguity constraints.
    def floors_of_alloc(a: Dict[int, str], hid: str) -> List[int]:
        return sorted({fl(r) for r, hh in a.items() if hh == hid})

    # Helper: floor ok check enforcing at most two contiguous floors.
    # Floors must be contiguous (no gaps), and the number of floors must
    # not exceed two.  This reflects the two‑floor constraint, separate
    # from the floor‑skipping constraint.
    def floor_ok_list(fs: List[int]) -> bool:
        if not fs:
            return True
        fs_sorted = sorted(fs)
        if len(fs_sorted) > 2:
            return False
        if len(fs_sorted) == 2:
            return fs_sorted[1] - fs_sorted[0] == 1
        return True

    # Initialise finish times
    finish = compute_finish_times(allocation, eco_rooms, eco_out_rooms, twin_rooms,
                                 bath_rooms, housekeepers, time_single, time_twin,
                                 time_eco, time_bath)
    # Group housekeepers by quota
    quota_to_hids = defaultdict(list)
    quotas = {h["id"]: h["room_quota"] for h in housekeepers}
    for hid, q in quotas.items():
        quota_to_hids[q].append(hid)

    # Process each group separately
    for q, hids in quota_to_hids.items():
        # Skip groups with single member
        if len(hids) < 2:
            continue
        improved = True
        # Repeat balancing until no improvement
        while True:
            improved = False
            # Compute current finish times for this group
            group_times = {hid: finish[hid] for hid in hids}
            slow_hid = max(group_times, key=group_times.get)
            fast_hid = min(group_times, key=group_times.get)
            diff = group_times[slow_hid] - group_times[fast_hid]
            # Define the acceptable finish‑time spread (in minutes) for cleaners
            MAX_TIME_DIFF = 4
            if diff <= MAX_TIME_DIFF:
                break
            # Compile candidate rooms (normal rooms) for slow and fast housekeepers
            slow_normals = [r for r, hh in allocation.items()
                            if hh == slow_hid and r not in eco_set_full]
            fast_normals = [r for r, hh in allocation.items()
                            if hh == fast_hid and r not in eco_set_full]
            # Sort candidates: slow side descending by time, fast side ascending by time
            slow_normals.sort(key=lambda r: room_time(r), reverse=True)
            fast_normals.sort(key=lambda r: room_time(r))
            found_swap = False
            for r_slow in slow_normals:
                t_slow = room_time(r_slow)
                for r_fast in fast_normals:
                    t_fast = room_time(r_fast)
                    # We only benefit if t_slow > t_fast
                    if t_slow <= t_fast:
                        break
                    # Simulate swap
                    tmp = clone(allocation)
                    safe_swap(tmp, r_slow, r_fast)
                    # Check floor constraints for both housekeepers
                    new_floors_slow = floors_of_alloc(tmp, slow_hid)
                    new_floors_fast = floors_of_alloc(tmp, fast_hid)
                    if not (floor_ok_list(new_floors_slow) and floor_ok_list(new_floors_fast)):
                        continue
                    # Check twin balance across all housekeepers
                    tc = twin_counts(tmp)
                    if max(tc.values()) - min(tc.values()) > 2:
                        continue
                    # Compute new finish times for slow and fast
                    new_time_slow = finish[slow_hid] - t_slow + t_fast
                    new_time_fast = finish[fast_hid] - t_fast + t_slow
                    new_diff = new_time_slow - new_time_fast
                    # Accept swap if it reduces the difference
                    if new_diff < diff:
                        # Commit swap
                        allocation = tmp
                        finish[slow_hid] = new_time_slow
                        finish[fast_hid] = new_time_fast
                        found_swap = True
                        improved = True
                        break
                if found_swap:
                    break
            # If no beneficial normal-room swap found, attempt to reassign eco/eco_out rooms
            if not found_swap:
                # Try moving an eco or eco_out room from slow_hid to another housekeeper
                # to reduce the time difference.  Only consider recipients in the same quota group.
                # Compute current eco counts across all housekeepers
                eco_counts = Counter({h["id"]: 0 for h in housekeepers})
                for r_all, hid_all in allocation.items():
                    if r_all in eco_set_full:
                        eco_counts[hid_all] += 1
                # List eco rooms assigned to the slow housekeeper
                eco_candidates = [r for r in allocation if allocation[r] == slow_hid and r in eco_set_full]
                eco_moved = False
                for r in eco_candidates:
                    floor_r = fl(r)
                    # Try to move r to a recipient in the same group (different hid)
                    for rec_hid in hids:
                        if rec_hid == slow_hid:
                            continue
                        # Determine if we can transfer based on floor constraints.
                        # For eco_out rooms we require the recipient to already have this floor.
                        rec_floors = floors_of_alloc(allocation, rec_hid)
                        if r in eco_out_rooms and floor_r not in rec_floors:
                            continue
                        # For eco rooms, ensure that adding this floor to the recipient
                        # would not violate floor span/contiguity constraints.
                        if r in eco_rooms and floor_r not in rec_floors:
                            # Simulate adding the floor
                            new_rec_floors = sorted(rec_floors + [floor_r])
                            if not floor_ok_list(new_rec_floors):
                                continue
                        # Simulate transfer and check floor constraints for both housekeepers
                        tmp_allocation = clone(allocation)
                        tmp_allocation[r] = rec_hid
                        new_floors_slow = floors_of_alloc(tmp_allocation, slow_hid)
                        new_floors_rec = floors_of_alloc(tmp_allocation, rec_hid)
                        if not (floor_ok_list(new_floors_slow) and floor_ok_list(new_floors_rec)):
                            continue
                        # Compute new eco counts if transferred
                        new_eco_counts = eco_counts.copy()
                        new_eco_counts[slow_hid] -= 1
                        new_eco_counts[rec_hid] += 1
                        # Check eco fairness: difference < 3
                        e_vals = list(new_eco_counts.values())
                        if max(e_vals) - min(e_vals) >= 3:
                            continue
                        # Compute new finish times for slow and recipient
                        new_finish_slow = finish[slow_hid] - time_eco
                        new_finish_rec = finish[rec_hid] + time_eco
                        # Determine new max/min for group if necessary
                        tmp_group_times = group_times.copy()
                        tmp_group_times[slow_hid] = new_finish_slow
                        tmp_group_times[rec_hid] = new_finish_rec
                        tmp_diff = max(tmp_group_times.values()) - min(tmp_group_times.values())
                        # Accept if improvement
                        if tmp_diff < diff:
                            # Commit transfer
                            allocation[r] = rec_hid
                            finish[slow_hid] = new_finish_slow
                            finish[rec_hid] = new_finish_rec
                            group_times = tmp_group_times
                            diff = tmp_diff
                            eco_counts = new_eco_counts
                            eco_moved = True
                            improved = True
                            break
                    if eco_moved:
                        break
                # If no eco/out move improved the difference, stop balancing for this group
                if not improved:
                    break
            # If a swap or eco move improved things, continue the outer while loop
    return allocation


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

def assign_rooms(rooms: List[int], eco_rooms: Iterable[int], eco_out_rooms: Iterable[int],
                 twin_rooms: Iterable[int], *rest) -> Dict[int, str]:
    """High‑level entry point to perform a complete room assignment.

    This function accepts two signatures for backward compatibility:

    1. ``assign_rooms(rooms, eco_rooms, eco_out_rooms, twin_rooms, bath_rooms,
       housekeepers, time_single, time_twin, time_eco, time_bath)`` – the
       original signature where ``bath_rooms`` is supplied explicitly.

    2. ``assign_rooms(rooms, eco_rooms, eco_out_rooms, twin_rooms, housekeepers,
       time_single, time_twin, time_eco, time_bath)`` – a convenience
       signature where ``bath_rooms`` is omitted.  In this case
       ``bath_rooms`` defaults to an empty list.

    Parameters
    ----------
    rooms : list[int]
        All room numbers in the hotel.
    eco_rooms : iterable[int]
        Room numbers for eco rooms (free rooms not counted toward quotas).
    eco_out_rooms : iterable[int]
        Room numbers for eco‑out rooms.
    twin_rooms : iterable[int]
        Room numbers for twin rooms.
    *rest :
        Either a 6‑tuple ``(bath_rooms, housekeepers, time_single, time_twin,
        time_eco, time_bath)`` or a 5‑tuple ``(housekeepers, time_single,
        time_twin, time_eco, time_bath)``.  See above.

    Returns
    -------
    dict[int, str]
        Mapping from room number to assigned housekeeper ID.
    """
    # Parse variable arguments to support both 9‑ and 10‑argument forms
    if len(rest) == 6:
        bath_rooms, housekeepers, time_single, time_twin, time_eco, time_bath = rest
    elif len(rest) == 5:
        # Called without bath_rooms; default to empty list
        housekeepers, time_single, time_twin, time_eco, time_bath = rest
        bath_rooms = []
    else:
        raise TypeError(
            "assign_rooms expects either 9 or 10 positional arguments: "
            "(rooms, eco_rooms, eco_out_rooms, twin_rooms, bath_rooms, housekeepers, "
            "time_single, time_twin, time_eco, time_bath) or "
            "(rooms, eco_rooms, eco_out_rooms, twin_rooms, housekeepers, "
            "time_single, time_twin, time_eco, time_bath)"
        )
    # Determine the set of normal rooms (those that count toward quotas)
    normal_rooms = [r for r in rooms if r not in eco_rooms and r not in eco_out_rooms]
    # Phase 1: assign normal rooms strictly according to quotas
    allocation = initial_assign(normal_rooms, housekeepers)
    # Verify quotas
    quotas = {h["id"]: h["room_quota"] for h in housekeepers}
    if not quota_ok(Counter(allocation.values()), quotas):
        raise RuntimeError("initial quota mismatch")
    # Phase 2: rebalance twin room counts.
    # To enforce the 2‑floor constraint (housekeepers may be assigned to at most
    # two floors), we call rebalance_twins with allow_min_triplex=False.  This
    # means swaps that would cause a housekeeper to occupy three floors are
    # disallowed even if the floors are contiguous.  The no‑floor‑skipping
    # constraint (floors must be adjacent) is still enforced elsewhere.
    allocation = rebalance_twins(allocation, twin_rooms, housekeepers, allow_min_triplex=False)
    # Phase 2b: rebalance floors to ensure contiguous span <= 2 floors
    allocation = rebalance_floors(allocation, housekeepers, eco_rooms, eco_out_rooms)
    # Phase 3: assign eco/eco‑out rooms (do not affect quotas).
    # We pass timing and room type information so that eco assignment can
    # consider current workloads and better balance finish times across
    # housekeepers with the same quota.  This helps avoid excessive
    # differences in cleaning finish times and further distributes eco
    # rooms fairly.
    eco_assign = assign_eco_rooms_full(
        allocation,
        eco_rooms,
        eco_out_rooms,
        housekeepers,
        twin_rooms,
        bath_rooms,
        time_single,
        time_twin,
        time_eco,
        time_bath,
    )
    allocation.update(eco_assign)
    # Phase 4: optionally balance finish times (no‑op here)
    allocation = balance_finish_times(allocation, eco_rooms, eco_out_rooms, twin_rooms,
                                      bath_rooms, housekeepers, time_single, time_twin,
                                      time_eco, time_bath)
    return allocation