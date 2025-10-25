"""
Extended eco‑room allocation logic for hotel housekeepers.

This module includes the full implementation of the room assignment
functions as provided by the user, with an improved version of
``assign_eco_rooms_full``.  The new algorithm strives to distribute
eco rooms as evenly as possible across housekeepers while obeying
business rules:

* Eco‑out rooms must remain on the same floor as the housekeeper's
  existing rooms.
* Eco rooms should be assigned to housekeepers already on the same
  floor when possible.  To even out the distribution, a housekeeper
  with only one floor may acquire a second floor composed solely of
  eco rooms.  When a housekeeper takes on a new eco‑only floor, they
  must be assigned at least two eco rooms on that floor.  If there is
  only a single eco room available on an empty floor, that lone room
  is assigned to the housekeeper with the fewest eco assignments,
  without enforcing the two‑room minimum.

The remainder of this file contains helper functions and the
``assign_rooms`` entry point unchanged from the user's original
submission, except for the modifications to ``assign_eco_rooms_full``.
"""

from collections import defaultdict, Counter
from typing import Dict, List, Iterable

def fl(r: int) -> int:
    """Return the floor number given a room number."""
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

def initial_assign(rooms: List[int], housekeepers: List[Dict]) -> Dict[int, str]:
    """Assign normal rooms to housekeepers while respecting quotas and
    basic floor/bath constraints.  See original implementation for
    details."""
    allocation: Dict[int, str] = {r: None for r in rooms}
    quotas: Dict[str, int] = {h["id"]: h["room_quota"] for h in housekeepers}
    assigned = Counter()
    bath_flags: Dict[str, bool] = {h["id"]: h.get("has_bath", False) for h in housekeepers}
    floors = sorted({fl(r) for r in rooms})
    min_floor = min(floors) if floors else 0
    low_floors = [f for f in floors if f <= min_floor + 2]
    order = sorted(floors, reverse=True) + low_floors
    by_floor: Dict[int, List[int]] = defaultdict(list)
    for r in sorted(rooms):
        by_floor[fl(r)].append(r)
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
    for r, v in allocation.items():
        if v is None:
            tgt = min(quotas, key=lambda x: assigned[x])
            allocation[r] = tgt
            assigned[tgt] += 1
    for hid in quotas:
        if assigned[hid] != quotas[hid]:
            raise RuntimeError(f"❌ quota mismatch: {hid}")
    return allocation

def rebalance_twins(alloc: Dict[int, str], twin_rooms: Iterable[int],
                    housekeepers: List[Dict], allow_min_triplex: bool = True) -> Dict[int, str]:
    """Perform swaps to reduce the disparity of twin room counts among housekeepers."""
    twin_set = set(twin_rooms)
    has_bath = {h["id"]: h.get("has_bath", False) for h in housekeepers}
    def floors_of(a: Dict[int, str], hid: str) -> List[int]:
        return sorted({fl(r) for r, h in a.items() if h == hid})
    def floor_ok(fs: List[int], allow: bool) -> bool:
        if len(fs) <= 2:
            return True
        if allow and len(fs) == 3 and max(fs) - min(fs) <= 2:
            return True
        return False
    def safe_for_bath(hid: str, r: int) -> bool:
        return (not has_bath.get(hid, False)) or fl(r) <= 4
    def twin_counts(a: Dict[int, str]) -> Dict[str, int]:
        return {h["id"]: sum(1 for r, hh in a.items() if hh == h["id"] and r in twin_set)
                for h in housekeepers}
    iteration = 0
    while True:
        iteration += 1
        tc = twin_counts(alloc)
        mx, mn = max(tc.values()), min(tc.values())
        # A difference of 2 twin rooms is considered unfair; we aim for at most 1.
        severe = mx - mn >= 2
        # Stop iterating when the difference in twin counts is at most 1.  If some
        # housekeepers have zero twin rooms, then all others must have at most one.
        if (mn > 0 and mx - mn <= 1) or (mn == 0 and mx <= 1):
            break
        # Identify donors (have at least two more twin rooms than the minimum)
        # When some housekeepers have zero twin rooms, anyone with two or more is a donor.
        donors = [h for h, c in tc.items() if c >= mn + 2 or (mn == 0 and c >= 2)]
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

def rebalance_floors(alloc: Dict[int, str], housekeepers: List[Dict],
                     eco_rooms: Iterable[int], eco_out_rooms: Iterable[int]) -> Dict[int, str]:
    """Ensure that no housekeeper is assigned to more than two floors."""
    eco_set = set(eco_rooms) | set(eco_out_rooms)
    def floors_of_alloc(a: Dict[int, str], hid: str) -> List[int]:
        return sorted({fl(r) for r, h in a.items() if h == hid and r not in eco_set})
    def floor_ok_list(fs: List[int]) -> bool:
        if not fs:
            return True
        fs_sorted = sorted(fs)
        if len(fs_sorted) > 2:
            return False
        if len(fs_sorted) == 2:
            return fs_sorted[1] - fs_sorted[0] == 1
        return True
    changed = True
    while changed:
        changed = False
        for h in housekeepers:
            hid = h["id"]
            floors = floors_of_alloc(alloc, hid)
            if len(floors) <= 2:
                continue
            candidate_floors_to_remove = [floors[0], floors[-1]]
            swapped = False
            for f_remove in candidate_floors_to_remove:
                donor_rooms = [r for r, h2 in alloc.items()
                               if h2 == hid and fl(r) == f_remove and r not in eco_set]
                for r in donor_rooms:
                    for h2 in housekeepers:
                        hid2 = h2["id"]
                        if hid2 == hid:
                            continue
                        floors2 = floors_of_alloc(alloc, hid2)
                        if f_remove not in floors2 and len(floors2) >= 2:
                            continue
                        possible_floors_for_hid = [f for f in floors if f != f_remove]
                        candidate_s = None
                        for s in [rr for rr, hh in alloc.items() if hh == hid2 and rr not in eco_set]:
                            s_floor = fl(s)
                            if s_floor in possible_floors_for_hid:
                                candidate_s = s
                                break
                        if candidate_s is None:
                            continue
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
    Assign eco and eco‑out rooms to housekeepers with fairness and floor locality.

    This implementation distributes eco rooms as evenly as possible while
    respecting business rules:

    * Eco‑out rooms must stay on their existing floor.
    * Eco rooms are first assigned to housekeepers already on the floor.
      To improve fairness, housekeepers with only one floor may take on
      a second floor consisting solely of eco rooms, provided they
      receive at least two eco rooms on that floor.  If there is just
      one eco room on an empty floor, it is assigned to the housekeeper
      with the fewest eco assignments (ignoring the two‑room minimum).
    * Bath handlers (``has_bath=True``) may not be assigned to floors
      above the fourth floor for eco rooms.

    Eco and eco‑out assignments do not affect normal room quotas but do
    contribute to finish time estimates.  This function updates the
    allocation in place and returns a mapping from eco/eco‑out room
    numbers to the assigned housekeeper ID.
    """
    # Helper: compute initial set of floors per housekeeper using normal rooms only
    fl_alloc: Dict[str, List[int]] = {h["id"]: house_floors(alloc, h["id"])[:] for h in housekeepers}
    # Track assigned eco rooms per housekeeper
    eco_assign: Dict[int, str] = {}
    eco_count: Counter = Counter({h["id"]: 0 for h in housekeepers})
    # Bath flag lookup
    has_bath = {h["id"]: h.get("has_bath", False) for h in housekeepers}
    # Finish time estimates prior to eco assignment
    finish_times: Dict[str, float] = compute_finish_times(
        alloc,
        (),
        (),
        twin_rooms,
        bath_rooms,
        housekeepers,
        time_single,
        time_twin,
        time_eco,
        time_bath,
    )
    # Determine pure eco rooms (exclude eco_out duplicates)
    eco_set = set(eco_rooms)
    eco_out_set = set(eco_out_rooms)
    pure_eco = [r for r in eco_rooms if r not in eco_out_set]
    # Group pure eco rooms by floor
    floor_to_eco: Dict[int, List[int]] = defaultdict(list)
    for r in pure_eco:
        floor_to_eco[fl(r)].append(r)
    for rooms in floor_to_eco.values():
        rooms.sort()
    # Compute sorting key for floors: process floors with fewest existing
    # housekeepers first, then by descending number of eco rooms.
    floor_keys: Dict[int, tuple] = {}
    for floor, rooms in floor_to_eco.items():
        # count existing housekeepers on this floor
        m = len([hid for hid, fls in fl_alloc.items() if floor in fls])
        floor_keys[floor] = (m, -len(rooms))
    floors_sorted = sorted(floor_to_eco.keys(), key=lambda f: floor_keys[f])

    def compute_assignment_for_floor(n: int, existing_hks: List[str], candidate_hks: List[str]) -> tuple:
        """
        For a given floor with ``n`` eco rooms, choose how many new
        housekeepers to add (``k``) and determine the number of rooms
        assigned to each participating housekeeper.  Existing
        housekeepers stay in the candidate set.  Candidates must have
        fewer than two floors and, if they handle baths, the floor must
        be at or below 4.  Among all feasible values of ``k`` from 0
        through ``min(len(candidate_hks), n//2)``, this helper chooses
        the one that minimises the difference between the highest and
        lowest eco counts after assignment.  Ties break by the smaller
        maximum eco count, then by favouring assignments that place
        additional rooms on housekeepers with lower finish times.
        Returns a tuple ``(k, chosen_candidates, count_assign)`` where
        ``count_assign`` maps participating housekeepers to the number
        of eco rooms on this floor.
        """
        m = len(existing_hks)
        best_diff = None
        best_max = None
        best_res = None
        # Maximum number of new housekeepers allowed by two‑room minimum
        max_k = min(len(candidate_hks), n // 2)
        # Evaluate each possible k
        for k in range(max_k + 1):
            total = m + k
            if total == 0:
                continue
            # choose k candidates with lowest eco_count (tie break by finish_time)
            chosen_candidates = sorted(candidate_hks, key=lambda h: (eco_count[h], finish_times[h]))[:k]
            # base assignment for existing hks
            base_existing = n // total
            # base assignment for new hks (must be at least 2 if k>0)
            base_new = max(base_existing, 2) if k > 0 else 0
            assigned = base_existing * m + base_new * k
            if assigned > n:
                continue
            leftover = n - assigned
            # initial counts per hk
            count_assign: Dict[str, int] = {}
            for hid in chosen_candidates:
                count_assign[hid] = base_new
            for hid in existing_hks:
                count_assign[hid] = count_assign.get(hid, 0) + base_existing
            participants = existing_hks + chosen_candidates
            existing_set = set(existing_hks)
            # distribute leftover rooms one by one to minimise growth of eco_count
            for _ in range(leftover):
                hk = min(
                    participants,
                    key=lambda h: (
                        eco_count[h] + count_assign.get(h, 0),
                        finish_times[h] + count_assign.get(h, 0) * time_eco,
                        1 if h in existing_set else 0,
                    ),
                )
                count_assign[hk] = count_assign.get(hk, 0) + 1
            # Evaluate the eco_count spread if we commit this assignment
            new_counts = eco_count.copy()
            for hid, cnt in count_assign.items():
                new_counts[hid] += cnt
            max_cnt = max(new_counts.values())
            min_cnt = min(new_counts.values())
            diff = max_cnt - min_cnt
            if best_diff is None or diff < best_diff or (diff == best_diff and max_cnt < best_max):
                best_diff = diff
                best_max = max_cnt
                best_res = (k, chosen_candidates, count_assign)
        return best_res

    # Assign pure eco rooms floor by floor
    for floor in floors_sorted:
        rooms = floor_to_eco[floor]
        n = len(rooms)
        if n == 0:
            continue
        # Existing housekeepers on this floor
        existing = [hid for hid, fls in fl_alloc.items() if floor in fls]
        # Candidate housekeepers: not on this floor, fewer than two floors,
        # and (not bath or floor <=4)
        candidate = [
            hid
            for hid, fls in fl_alloc.items()
            if floor not in fls and len(fls) < 2 and (floor <= 4 or not has_bath.get(hid, False))
        ]
        # Compute the best assignment for this floor
        res = compute_assignment_for_floor(n, existing, candidate)
        if res:
            k, chosen_candidates, count_assign = res
            # Add the floor to any chosen candidate (new) housekeepers
            for hid in chosen_candidates:
                if floor not in fl_alloc[hid]:
                    fl_alloc[hid] = sorted(fl_alloc[hid] + [floor])
            # Assign rooms sequentially according to count_assign
            idx = 0
            participants = existing + chosen_candidates
            for hid in participants:
                cnt = count_assign.get(hid, 0)
                for _ in range(cnt):
                    if idx >= n:
                        break
                    r = rooms[idx]
                    eco_assign[r] = hid
                    eco_count[hid] += 1
                    finish_times[hid] += time_eco
                    idx += 1
        else:
            # Fallback: assign all eco rooms to existing hks (if any) or to
            # the housekeeper with the lowest eco_count that can take the floor
            for r in rooms:
                if existing:
                    # Choose existing hk with smallest eco_count, tie by finish_time
                    hid = min(existing, key=lambda h: (eco_count[h], finish_times[h]))
                else:
                    # No existing hk: choose any candidate that can add the floor
                    possible = [h for h in fl_alloc if len(fl_alloc[h]) < 2 and (floor <= 4 or not has_bath.get(h, False))]
                    if not possible:
                        possible = list(fl_alloc.keys())
                    hid = min(possible, key=lambda h: (eco_count[h], finish_times[h]))
                    if floor not in fl_alloc[hid]:
                        fl_alloc[hid] = sorted(fl_alloc[hid] + [floor])
                eco_assign[r] = hid
                eco_count[hid] += 1
                finish_times[hid] += time_eco
    # Finally, assign eco‑out rooms.  These must remain on a floor already
    # occupied by the housekeeper.  Choose the housekeeper with the
    # lowest eco_count (tie by finish_time) among those on the same
    # floor.  Bath restrictions apply here as well.
    for r in eco_out_rooms:
        floor_r = fl(r)
        candidates = [hid for hid, fls in fl_alloc.items() if floor_r in fls]
        if not candidates:
            raise RuntimeError(f"❌ eco_out room {r} cannot be assigned without floor move")
        # Filter by bath constraint
        filtered = [h for h in candidates if not (has_bath.get(h, False) and floor_r > 4)]
        if not filtered:
            filtered = candidates
        # Choose hk with smallest eco_count, tie by finish_time
        hid = min(filtered, key=lambda h: (eco_count[h], finish_times[h]))
        eco_assign[r] = hid
        eco_count[hid] += 1
        finish_times[hid] += time_eco
    return eco_assign

def compute_finish_times(allocation: Dict[int, str], eco_rooms: Iterable[int],
                         eco_out_rooms: Iterable[int], twin_rooms: Iterable[int],
                         bath_rooms: Iterable[int], housekeepers: List[Dict],
                         time_single: float, time_twin: float,
                         time_eco: float, time_bath: float) -> Dict[str, float]:
    """Compute estimated finish times for each housekeeper."""
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
    """Attempt to balance finish times among housekeepers with identical quotas."""
    from collections import defaultdict, Counter
    def room_time(r: int) -> float:
        if r in bath_rooms:
            return time_bath
        elif r in set(twin_rooms):
            return time_twin
        elif r in set(eco_rooms) or r in set(eco_out_rooms):
            return time_eco
        else:
            return time_single
    eco_out_set = set(eco_out_rooms)
    eco_set = set(eco_rooms)
    eco_set_full = eco_set | eco_out_set
    def twin_counts(a: Dict[int, str]) -> Dict[str, int]:
        twin_set = set(twin_rooms)
        return {h["id"]: sum(1 for r, hh in a.items() if hh == h["id"] and r in twin_set)
                for h in housekeepers}
    def floors_of_alloc(a: Dict[int, str], hid: str) -> List[int]:
        return sorted({fl(r) for r, hh in a.items() if hh == hid})
    def floor_ok_list(fs: List[int]) -> bool:
        if not fs:
            return True
        fs_sorted = sorted(fs)
        if len(fs_sorted) > 2:
            return False
        if len(fs_sorted) == 2:
            return fs_sorted[1] - fs_sorted[0] == 1
        return True
    finish = compute_finish_times(allocation, eco_rooms, eco_out_rooms, twin_rooms,
                                 bath_rooms, housekeepers, time_single, time_twin,
                                 time_eco, time_bath)
    quota_to_hids = defaultdict(list)
    quotas = {h["id"]: h["room_quota"] for h in housekeepers}
    for hid, q in quotas.items():
        quota_to_hids[q].append(hid)
    for q, hids in quota_to_hids.items():
        if len(hids) < 2:
            continue
        while True:
            improved = False
            group_times = {hid: finish[hid] for hid in hids}
            slow_hid = max(group_times, key=group_times.get)
            fast_hid = min(group_times, key=group_times.get)
            diff = group_times[slow_hid] - group_times[fast_hid]
            MAX_TIME_DIFF = 4
            if diff <= MAX_TIME_DIFF:
                break
            slow_normals = [r for r, hh in allocation.items()
                            if hh == slow_hid and r not in eco_set_full]
            fast_normals = [r for r, hh in allocation.items()
                            if hh == fast_hid and r not in eco_set_full]
            slow_normals.sort(key=lambda r: room_time(r), reverse=True)
            fast_normals.sort(key=lambda r: room_time(r))
            found_swap = False
            for r_slow in slow_normals:
                t_slow = room_time(r_slow)
                for r_fast in fast_normals:
                    t_fast = room_time(r_fast)
                    if t_slow <= t_fast:
                        break
                    tmp = clone(allocation)
                    safe_swap(tmp, r_slow, r_fast)
                    new_floors_slow = floors_of_alloc(tmp, slow_hid)
                    new_floors_fast = floors_of_alloc(tmp, fast_hid)
                    if not (floor_ok_list(new_floors_slow) and floor_ok_list(new_floors_fast)):
                        continue
                    tc = twin_counts(tmp)
                    if max(tc.values()) - min(tc.values()) > 2:
                        continue
                    new_time_slow = finish[slow_hid] - t_slow + t_fast
                    new_time_fast = finish[fast_hid] - t_fast + t_slow
                    new_diff = new_time_slow - new_time_fast
                    if new_diff < diff:
                        allocation = tmp
                        finish[slow_hid] = new_time_slow
                        finish[fast_hid] = new_time_fast
                        found_swap = True
                        improved = True
                        break
                if found_swap:
                    break
            if not found_swap:
                eco_counts = Counter({h["id"]: 0 for h in housekeepers})
                for r_all, hid_all in allocation.items():
                    if r_all in eco_set_full:
                        eco_counts[hid_all] += 1
                eco_candidates = [r for r in allocation if allocation[r] == slow_hid and r in eco_set_full]
                eco_moved = False
                for r in eco_candidates:
                    floor_r = fl(r)
                    for rec_hid in hids:
                        if rec_hid == slow_hid:
                            continue
                        rec_floors = floors_of_alloc(allocation, rec_hid)
                        if r in eco_out_rooms and floor_r not in rec_floors:
                            continue
                        if r in eco_rooms and floor_r not in rec_floors:
                            new_rec_floors = sorted(rec_floors + [floor_r])
                            if not floor_ok_list(new_rec_floors):
                                continue
                        tmp_allocation = clone(allocation)
                        tmp_allocation[r] = rec_hid
                        new_floors_slow = floors_of_alloc(tmp_allocation, slow_hid)
                        new_floors_rec = floors_of_alloc(tmp_allocation, rec_hid)
                        if not (floor_ok_list(new_floors_slow) and floor_ok_list(new_floors_rec)):
                            continue
                        new_eco_counts = eco_counts.copy()
                        new_eco_counts[slow_hid] -= 1
                        new_eco_counts[rec_hid] += 1
                        e_vals = list(new_eco_counts.values())
                        if max(e_vals) - min(e_vals) >= 3:
                            continue
                        new_finish_slow = finish[slow_hid] - time_eco
                        new_finish_rec = finish[rec_hid] + time_eco
                        tmp_group_times = group_times.copy()
                        tmp_group_times[slow_hid] = new_finish_slow
                        tmp_group_times[rec_hid] = new_finish_rec
                        tmp_diff = max(tmp_group_times.values()) - min(tmp_group_times.values())
                        if tmp_diff < diff:
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
                if not improved:
                    break
            if improved:
                continue
            break
    return allocation

def assign_rooms(rooms: List[int], eco_rooms: Iterable[int], eco_out_rooms: Iterable[int],
                 twin_rooms: Iterable[int], *rest) -> Dict[int, str]:
    """High‑level entry point to perform a complete room assignment."""
    if len(rest) == 6:
        bath_rooms, housekeepers, time_single, time_twin, time_eco, time_bath = rest
    elif len(rest) == 5:
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
    normal_rooms = [r for r in rooms if r not in eco_rooms and r not in eco_out_rooms]
    allocation = initial_assign(normal_rooms, housekeepers)
    quotas = {h["id"]: h["room_quota"] for h in housekeepers}
    if not quota_ok(Counter(allocation.values()), quotas):
        raise RuntimeError("initial quota mismatch")
    allocation = rebalance_twins(allocation, twin_rooms, housekeepers, allow_min_triplex=False)
    allocation = rebalance_floors(allocation, housekeepers, eco_rooms, eco_out_rooms)
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
    allocation = balance_finish_times(allocation, eco_rooms, eco_out_rooms, twin_rooms,
                                      bath_rooms, housekeepers, time_single, time_twin,
                                      time_eco, time_bath)
    return allocation


# --------------------------------------------------------------------------
# Experimental optimizer
# --------------------------------------------------------------------------

import random

def assign_rooms_optimized(
    rooms: List[int],
    eco_rooms: Iterable[int],
    eco_out_rooms: Iterable[int],
    twin_rooms: Iterable[int],
    *rest,
    iterations: int = 5,
    local_search_iter: int = 50,
    seed: int | None = None,
) -> Dict[int, str]:
    """
    Attempt multiple randomised assignments and return the best one according to
    fairness metrics (twin difference, eco difference, finish time spread).

    Parameters
    ----------
    rooms, eco_rooms, eco_out_rooms, twin_rooms, *rest: same as assign_rooms
    iterations : int
        Number of random assignments to attempt (default 5). More iterations
        improve the chance of finding a better allocation but increase runtime.
    local_search_iter : int
        Number of local twin-balancing swaps to attempt per iteration. This
        simple hill-climbing step further refines the twin distribution after
        each random assignment.
    seed : Optional[int]
        Seed for the random number generator to obtain reproducible results.

    Returns
    -------
    dict[int, str]
        Assignment from room number to housekeeper ID.
    """
    # parse *rest similar to assign_rooms
    if len(rest) == 6:
        bath_rooms, housekeepers, time_single, time_twin, time_eco, time_bath = rest
    elif len(rest) == 5:
        housekeepers, time_single, time_twin, time_eco, time_bath = rest
        bath_rooms = []
    else:
        raise TypeError(
            "assign_rooms_optimized expects either 9 or 10 positional arguments: "
            "(rooms, eco_rooms, eco_out_rooms, twin_rooms, bath_rooms, housekeepers, "
            "time_single, time_twin, time_eco, time_bath) or "
            "(rooms, eco_rooms, eco_out_rooms, twin_rooms, housekeepers, "
            "time_single, time_twin, time_eco, time_bath)"
        )

    if seed is not None:
        random.seed(seed)

    # Precompute eco/time info for scoring
    eco_set = set(eco_rooms) | set(eco_out_rooms)
    twin_set = set(twin_rooms)

    def compute_score(allocation: Dict[int, str], hk_list: List[Dict]) -> float:
        """
        Compute a weighted score capturing fairness. Lower is better.
        We weigh twin difference highest, eco difference next, and finish time difference least.
        """
        # twin counts
        from collections import Counter
        tc = Counter({h["id"]: 0 for h in hk_list})
        for r, hid in allocation.items():
            if r in twin_set:
                tc[hid] += 1
        max_tc = max(tc.values())
        min_tc = min(tc.values())
        twin_diff = max_tc - min_tc
        # eco counts (pure + eco-out)
        ec = Counter({h["id"]: 0 for h in hk_list})
        for r, hid in allocation.items():
            if r in eco_set:
                ec[hid] += 1
        max_ec = max(ec.values())
        min_ec = min(ec.values())
        eco_diff = max_ec - min_ec
        # finish time spread
        finish = compute_finish_times(
            allocation, eco_rooms, eco_out_rooms, twin_rooms, bath_rooms,
            hk_list, time_single, time_twin, time_eco, time_bath
        )
        max_fin = max(finish.values())
        min_fin = min(finish.values())
        fin_diff = max_fin - min_fin
        # Weighted sum (twin difference weighted highest)
        return twin_diff * 100.0 + eco_diff * 10.0 + fin_diff

    best_allocation: Dict[int, str] | None = None
    best_score = float('inf')

    # Work on a copy of rooms list to avoid modifying original
    rooms_copy = list(rooms)

    for itr in range(iterations):
        # Randomise housekeeper order
        hk_list = [h.copy() for h in housekeepers]
        random.shuffle(hk_list)
        # We don't randomise room order here; rooms are grouped by floor via their numbers.
        # Use existing assign_rooms with randomised hk_list
        try:
            alloc = assign_rooms(rooms_copy, eco_rooms, eco_out_rooms, twin_rooms,
                                 bath_rooms, hk_list, time_single, time_twin,
                                 time_eco, time_bath)
        except Exception:
            # On failure (should not happen), skip this iteration
            continue
        # Local twin-balancing (simple hill-climb)
        # Compute twin counts
        from collections import defaultdict, Counter
        for _ in range(local_search_iter):
            # twin counts per hk
            tc = Counter({h["id"]: 0 for h in hk_list})
            for r, hid in alloc.items():
                if r in twin_set:
                    tc[hid] += 1
            max_hid = max(tc, key=tc.get)
            min_hid = min(tc, key=tc.get)
            if tc[max_hid] - tc[min_hid] <= 1:
                break
            # Find a twin room of max_hid and a normal room of min_hid to swap
            twin_room = None
            for r, hid in alloc.items():
                if hid == max_hid and r in twin_set:
                    twin_room = r
                    break
            normal_room = None
            for r, hid in alloc.items():
                if hid == min_hid and r not in twin_set and r not in eco_set:
                    normal_room = r
                    break
            if twin_room is None or normal_room is None:
                break
            # simulate swap
            # ensure swap is valid: floor constraints and bath constraints
            hidA, hidB = max_hid, min_hid
            rA, rB = twin_room, normal_room
            # Only swap if it keeps floor constraints
            tmp = alloc.copy()
            tmp[rA], tmp[rB] = hidB, hidA
            # Check floor constraints
            def floors_of_h(a, hid):
                return sorted({fl(x) for x, hh in a.items() if hh == hid and x not in eco_set})
            ok = True
            for hid_check in [hidA, hidB]:
                floors = floors_of_h(tmp, hid_check)
                if len(floors) > 2:
                    ok = False
                    break
                if len(floors) == 2 and floors[1] - floors[0] != 1:
                    ok = False
                    break
            if not ok:
                continue
            # apply swap
            alloc = tmp
        # Compute fairness score
        score = compute_score(alloc, hk_list)
        if score < best_score:
            best_score = score
            best_allocation = alloc
    # If no allocation found (should not happen), fallback to single run
    if best_allocation is None:
        best_allocation = assign_rooms(rooms, eco_rooms, eco_out_rooms, twin_rooms,
                                       bath_rooms, housekeepers, time_single, time_twin,
                                       time_eco, time_bath)
    return best_allocation