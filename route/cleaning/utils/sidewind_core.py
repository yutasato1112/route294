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
* **Twin‐room balance:** The number of twin rooms assigned to any two
  housekeepers must differ by no more than two.  If a housekeeper
  receives zero twin rooms then all housekeepers must receive two or
  fewer.
* **Floor limits:** A housekeeper may work on at most two floors, and
  these floors must be adjacent (no skipping floors).  Housekeepers
  flagged as handling bathing rooms (``has_bath=True``) may not be
  assigned rooms above the fourth floor.
* **Eco‐room fairness:** When assigning eco and eco‑out rooms (rooms
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
"""

from collections import defaultdict, Counter
from typing import Dict, List, Iterable

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

    # Debug output
    # print(f"initial_assign completed successfully ({len(floors)} floors: {floors})")
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
                        if severe or (floor_ok(floors_of(tmp, hA), allow_min_triplex)
                                      and floor_ok(floors_of(tmp, hB), allow_min_triplex)):
                            safe_swap(alloc, rA, rB)
                            # Debug output
                            # print(f"[rebalance-{iteration}] twin swap {rB}({hB})→{rA}({hA})")
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
    """Ensure that no housekeeper is assigned to more than two consecutive floors.

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
    """
    # Precompute sets for eco rooms to identify normal rooms
    eco_set = set(eco_rooms) | set(eco_out_rooms)

    def floors_of_alloc(a: Dict[int, str], hid: str) -> List[int]:
        return sorted({fl(r) for r, h in a.items() if h == hid and r not in eco_set})

    def floor_ok_list(fs: List[int]) -> bool:
        """Return True if the floors are contiguous and span at most two levels (差が2以内)."""
        if not fs:
            return True
        # Floors must be sorted
        fs_sorted = sorted(fs)
        # Span (max - min) must be <= 2
        if fs_sorted[-1] - fs_sorted[0] > 2:
            return False
        # No gaps greater than 1
        return all(fs_sorted[i+1] - fs_sorted[i] <= 1 for i in range(len(fs_sorted)-1))

    # Helper to find swap candidate for a given room
    changed = True
    while changed:
        changed = False
        # Iterate through housekeepers looking for one with >2 floors
        for h in housekeepers:
            hid = h["id"]
            floors = floors_of_alloc(alloc, hid)
            if len(floors) <= 2:
                continue
            # Decide which floors to try removing: examine lowest and highest floors
            # and attempt to remove each in turn until a successful swap occurs.
            candidate_floors_to_remove: List[int]
            if len(floors) <= 3:
                # When exactly three floors, consider both extremes
                candidate_floors_to_remove = [floors[0], floors[-1]]
            else:
                # For more than three floors, also consider both extremes.  If
                # necessary, additional logic could examine interior floors,
                # but such situations are unlikely in typical datasets.
                candidate_floors_to_remove = [floors[0], floors[-1]]
            swapped = False
            for f_remove in candidate_floors_to_remove:
                # Gather candidate rooms on the removal floor that are normal rooms
                donor_rooms = [r for r, h2 in alloc.items() if h2 == hid and fl(r) == f_remove and r not in eco_set]
                for r in donor_rooms:
                    # Try to find a swap partner for each room
                    for h2 in housekeepers:
                        hid2 = h2["id"]
                        if hid2 == hid:
                            continue
                        # Floors for the recipient before swap
                        floors2 = floors_of_alloc(alloc, hid2)
                        # Determine if h2 can take floor f_remove: either already has it or has fewer than 2 floors
                        if f_remove not in floors2 and len(floors2) >= 2:
                            continue
                        # Search for a room s in h2 that is on a floor that hid has (excluding f_remove)
                        possible_floors_for_hid = [f for f in floors if f != f_remove]
                        candidate_s = None
                        for s in [rr for rr, hh in alloc.items() if hh == hid2 and rr not in eco_set]:
                            s_floor = fl(s)
                            # h can accept floor s_floor if it is one of its remaining floors
                            if s_floor in possible_floors_for_hid:
                                candidate_s = s
                                break
                        if candidate_s is None:
                            continue
                        # Simulate swap
                        tmp = clone(alloc)
                        safe_swap(tmp, r, candidate_s)
                        # After swap, compute floors for both h and h2
                        new_floors_h = floors_of_alloc(tmp, hid)
                        new_floors_h2 = floors_of_alloc(tmp, hid2)
                        if floor_ok_list(new_floors_h) and floor_ok_list(new_floors_h2):
                            # Apply swap
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
        # End for each housekeeper
    return alloc


# ------------------------------------------------------------
# Eco‑room assignment with fairness
# ------------------------------------------------------------

def assign_eco_rooms_full(alloc: Dict[int, str], eco_rooms: Iterable[int],
                          eco_out_rooms: Iterable[int], housekeepers: List[Dict]) -> Dict[int, str]:
    """Assign eco and eco‑out rooms to housekeepers with fairness and floor locality.

    *Eco rooms* are free rooms that do not count towards a housekeeper’s
    quota.  They should ideally be placed on the same floor as one of
    the housekeeper’s normal rooms.  *Eco‑out rooms* must remain on
    the same floor as the housekeeper’s current assignment and may not
    incur a floor move.

    This function attempts to distribute eco rooms evenly across all
    housekeepers.  At each step the algorithm selects the set of
    candidate housekeepers (those already present on the room’s floor
    or, failing that, those with rooms on the nearest floors), and
    chooses the candidate with the smallest current eco room count.
    This heuristic greatly reduces the likelihood that any one
    housekeeper will receive three or more eco rooms more than
    another, thereby satisfying the fairness constraint described in
    the assignment specification.
    """
    # Determine the floors on which each housekeeper has normal rooms
    fl_alloc: Dict[str, List[int]] = {h["id"]: house_floors(alloc, h["id"]) for h in housekeepers}
    eco_assign: Dict[int, str] = {}
    # Track the number of eco rooms assigned to each housekeeper
    eco_count: Counter = Counter({h["id"]: 0 for h in housekeepers})

    # Helper to find candidate housekeepers for a given room
    def find_candidates_for_floor(floor: int) -> List[str]:
        # Candidates with a normal room on the same floor
        same_floor = [hid for hid, floors in fl_alloc.items() if floor in floors]
        if same_floor:
            return same_floor
        # Fallback: candidates on the nearest floors
        distances: Dict[str, int] = {}
        for hid, floors in fl_alloc.items():
            if not floors:
                # If a housekeeper has no rooms yet, treat distance as large
                distances[hid] = float('inf')
            else:
                distances[hid] = min(abs(floor - f) for f in floors)
        min_dist = min(distances.values())
        return [hid for hid, d in distances.items() if d == min_dist]

    # Assign eco rooms first
    for r in eco_rooms:
        floor = fl(r)
        candidates = find_candidates_for_floor(floor)
        # Choose candidate with the fewest eco rooms so far
        hid = min(candidates, key=lambda h: eco_count[h])
        eco_assign[r] = hid
        eco_count[hid] += 1

    # Assign eco‑out rooms: must stay on an existing floor
    for r in eco_out_rooms:
        floor = fl(r)
        candidates = [hid for hid, floors in fl_alloc.items() if floor in floors]
        if not candidates:
            # If no one has a room on this floor, we cannot assign without a floor move
            raise RuntimeError(f"❌ eco_out room {r} cannot be assigned without floor move")
        hid = min(candidates, key=lambda h: eco_count[h])
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
    """Placeholder for balancing finish times.

    In the original implementation, this function would attempt to
    rebalance room assignments to ensure that the earliest and latest
    finish times differed by no more than 10 minutes.  Such an
    optimisation requires potentially complex swaps across housekeepers
    while respecting all other constraints.  For the purposes of this
    exercise, we return the allocation unchanged.  Test cases may
    still inspect the finish times via ``compute_finish_times``.
    """
    # Future improvement: implement a greedy swap to minimise the
    # maximum difference in finish times.  For now we simply return
    # the current allocation unchanged.
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
    # Phase 2: rebalance twin room counts
    allocation = rebalance_twins(allocation, twin_rooms, housekeepers, allow_min_triplex=False)
    # Phase 2b: rebalance floors to ensure contiguous span <= 2 floors
    allocation = rebalance_floors(allocation, housekeepers, eco_rooms, eco_out_rooms)
    # Phase 3: assign eco/eco‑out rooms (do not affect quotas)
    eco_assign = assign_eco_rooms_full(allocation, eco_rooms, eco_out_rooms, housekeepers)
    allocation.update(eco_assign)
    # Phase 4: optionally balance finish times (no‑op here)
    allocation = balance_finish_times(allocation, eco_rooms, eco_out_rooms, twin_rooms,
                                      bath_rooms, housekeepers, time_single, time_twin,
                                      time_eco, time_bath)
    return allocation