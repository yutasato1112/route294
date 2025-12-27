"""
ホテル清掃指示書 自動振り分けシステム v28
Twin Quota指定優先版

修正点:
1. twin_quota指定ありのHKを絶対優先
2. twin_quota=-1（auto）のHKは調整用バッファとして使用
"""

from collections import defaultdict
from typing import Dict, List, Set, Any
import random


def assign_rooms(
    rooms: Dict[int, Any],
    eco_rooms: List[int],
    eco_out_rooms: List[int],
    twin_rooms: List[int],
    bath_rooms: List[int],
    housekeepers: List[Dict],
    single_time: int,
    twin_time: int,
    eco_time: int,
    bath_time: int
) -> Dict[int, int]:
    allocator = _RoomAllocator(
        list(rooms.keys()),
        eco_rooms,
        eco_out_rooms,
        twin_rooms,
        housekeepers
    )
    
    best_result = None
    best_score = float('-inf')
    
    for attempt in range(1000):
        hk_to_rooms = allocator.allocate(strategy=attempt)
        score, errors = allocator.evaluate_solution(hk_to_rooms)
        
        if score > best_score:
            best_score = score
            best_result = hk_to_rooms
        
        if errors == 0:
            break
        
        allocator.allocation = {h: [] for h in allocator.hk_ids}
    
    result = {}
    for hk_id, room_list in best_result.items():
        for room in room_list:
            result[room] = hk_id
    
    return result


def _fl(room: int) -> int:
    return room // 100


class _RoomAllocator:
    def __init__(self, rooms, eco_rooms, eco_out_rooms, twin_rooms, housekeepers):
        self.eco_rooms = set(eco_rooms) | set(eco_out_rooms)
        self.eco_out_rooms = set(eco_out_rooms)
        self.twin_rooms = set(twin_rooms)
        self.normal_rooms = sorted(rooms)
        
        self.floor_rooms = defaultdict(list)
        for r in self.normal_rooms:
            self.floor_rooms[_fl(r)].append(r)
        self.floors = sorted(self.floor_rooms.keys())
        
        self.hk_ids = [hk['id'] for hk in housekeepers]
        self.room_quotas = {hk['id']: hk['room_quota'] for hk in housekeepers}
        self.has_bath = {hk['id']: hk.get('has_bath', False) for hk in housekeepers}
        
        # Twin Quota: -1はauto、0以上は指定値
        self.twin_quota_specified = {}  # 指定されたか
        self.twin_quotas = {}
        self._calculate_twin_quotas(housekeepers)
        
        self.bath_hks = [h for h in self.hk_ids if self.has_bath[h]]
        self.normal_hks = [h for h in self.hk_ids if not self.has_bath[h]]
        
        self.allocation = {h: [] for h in self.hk_ids}
    
    def _calculate_twin_quotas(self, housekeepers):
        normal_twin_count = len([r for r in self.normal_rooms if r in self.twin_rooms])
        fixed, auto = 0, []
        for hk in housekeepers:
            if hk.get('twin_quota', -1) >= 0:
                self.twin_quotas[hk['id']] = hk['twin_quota']
                self.twin_quota_specified[hk['id']] = True
                fixed += hk['twin_quota']
            else:
                self.twin_quota_specified[hk['id']] = False
                auto.append(hk)
        
        remaining = normal_twin_count - fixed
        if auto and remaining > 0:
            total = sum(h['room_quota'] for h in auto)
            for hk in auto:
                self.twin_quotas[hk['id']] = round(remaining * hk['room_quota'] / total)
            allocated = sum(self.twin_quotas[h['id']] for h in auto)
            diff = remaining - allocated
            sorted_hks = sorted(auto, key=lambda h: h['room_quota'], reverse=True)
            for i in range(abs(diff)):
                self.twin_quotas[sorted_hks[i % len(sorted_hks)]['id']] += 1 if diff > 0 else -1
        elif auto:
            for hk in auto:
                self.twin_quotas[hk['id']] = 0
    
    def _count_normal(self, hk_id):
        return len([r for r in self.allocation[hk_id] if r not in self.eco_rooms])
    
    def _count_twins(self, hk_id):
        return sum(1 for r in self.allocation[hk_id] if r in self.twin_rooms and r not in self.eco_rooms)
    
    def _get_floors(self, hk_id):
        return set(_fl(r) for r in self.allocation[hk_id] if r not in self.eco_rooms)
    
    def _remaining_quota(self, hk_id):
        return self.room_quotas[hk_id] - self._count_normal(hk_id)
    
    def evaluate_solution(self, hk_to_rooms: Dict[int, List[int]]):
        score = 0
        total_errors = 0
        
        for hk_id in self.hk_ids:
            rooms = hk_to_rooms[hk_id]
            normal = [r for r in rooms if r not in self.eco_rooms]
            
            room_diff = abs(len(normal) - self.room_quotas[hk_id])
            score -= room_diff * 10000
            total_errors += room_diff
            
            floors = set(_fl(r) for r in normal)
            floor_excess = max(0, len(floors) - 2)
            score -= floor_excess * 1000
            total_errors += floor_excess
            
            # Twin Quota（指定ありのみカウント）
            if self.twin_quota_specified[hk_id]:
                twins = sum(1 for r in normal if r in self.twin_rooms)
                twin_diff = abs(twins - self.twin_quotas[hk_id])
                score -= twin_diff * 100
                total_errors += twin_diff
        
        return score, total_errors
    
    def allocate(self, strategy: int = 0) -> Dict[int, List[int]]:
        self.allocation = {h: [] for h in self.hk_ids}
        used = set()
        
        strategy_type = strategy % 20
        
        if strategy_type == 0:
            hk_queue = list(self.bath_hks) + list(self.normal_hks)
        elif strategy_type == 1:
            hk_queue = list(self.bath_hks) + sorted(self.normal_hks, key=lambda h: self.twin_quotas[h], reverse=True)
        elif strategy_type == 2:
            hk_queue = list(self.bath_hks) + sorted(self.normal_hks, key=lambda h: self.twin_quotas[h])
        elif strategy_type == 3:
            hk_queue = list(self.bath_hks) + sorted(self.normal_hks, key=lambda h: self.room_quotas[h], reverse=True)
        elif strategy_type == 4:
            hk_queue = list(self.bath_hks) + sorted(self.normal_hks, key=lambda h: self.room_quotas[h])
        elif strategy_type == 5:
            hk_queue = list(self.bath_hks) + list(reversed(self.normal_hks))
        elif strategy_type == 6:
            hk_queue = list(self.bath_hks) + sorted(self.normal_hks, 
                key=lambda h: self.twin_quotas[h] / max(1, self.room_quotas[h]), reverse=True)
        elif strategy_type == 7:
            hk_queue = list(self.bath_hks) + sorted(self.normal_hks, 
                key=lambda h: self.twin_quotas[h] / max(1, self.room_quotas[h]))
        else:
            normal_shuffled = list(self.normal_hks)
            random.seed(strategy)
            random.shuffle(normal_shuffled)
            hk_queue = list(self.bath_hks) + normal_shuffled
        
        reverse_floors = (strategy // 20) % 2 == 1
        
        for hk_id in hk_queue:
            self._allocate_hk(hk_id, used, reverse_floors)
        
        self._fallback_allocation_strict(used)
        
        # Twin調整（指定ありHKを優先）
        self._adjust_twin_quotas_priority()
        
        self._allocate_eco_rooms()
        
        return {h: sorted(self.allocation[h]) for h in self.hk_ids}
    
    def _allocate_hk(self, hk_id: int, used: Set[int], reverse_floors: bool = False):
        quota = self.room_quotas[hk_id]
        twin_quota = self.twin_quotas[hk_id]
        is_bath = self.has_bath[hk_id]
        
        if is_bath:
            available_floors = [f for f in self.floors if f <= 4]
        else:
            available_floors = list(self.floors)
        
        if reverse_floors:
            available_floors = list(reversed(available_floors))
        
        start_floor = None
        for f in available_floors:
            avail = [r for r in self.floor_rooms[f] if r not in used]
            if avail:
                start_floor = f
                break
        
        if start_floor is None:
            return
        
        assigned = 0
        twins_assigned = 0
        hk_floors = []
        
        scan_floors = available_floors if not reverse_floors else list(reversed(sorted(available_floors)))
        
        for floor in scan_floors:
            if not reverse_floors and floor < start_floor:
                continue
            if reverse_floors and floor > start_floor:
                continue
            if assigned >= quota:
                break
            if len(hk_floors) >= 2:
                break
            
            if hk_floors and floor not in hk_floors:
                if abs(floor - hk_floors[0]) > 2:
                    break
            
            available = [r for r in self.floor_rooms[floor] if r not in used]
            if not available:
                continue
            
            twins_here = sorted([r for r in available if r in self.twin_rooms])
            singles_here = sorted([r for r in available if r not in self.twin_rooms])
            
            twins_needed = max(0, twin_quota - twins_assigned)
            for room in twins_here[:twins_needed]:
                if assigned >= quota:
                    break
                self.allocation[hk_id].append(room)
                used.add(room)
                assigned += 1
                twins_assigned += 1
                if floor not in hk_floors:
                    hk_floors.append(floor)
            
            for room in singles_here:
                if assigned >= quota:
                    break
                self.allocation[hk_id].append(room)
                used.add(room)
                assigned += 1
                if floor not in hk_floors:
                    hk_floors.append(floor)
            
            for room in twins_here[twins_needed:]:
                if room in used:
                    continue
                if assigned >= quota:
                    break
                self.allocation[hk_id].append(room)
                used.add(room)
                assigned += 1
                twins_assigned += 1
                if floor not in hk_floors:
                    hk_floors.append(floor)
    
    def _fallback_allocation_strict(self, used: Set[int]):
        remaining = [r for r in self.normal_rooms if r not in used]
        
        for room in sorted(remaining):
            floor = _fl(room)
            is_twin = room in self.twin_rooms
            
            candidates = [h for h in self.hk_ids if self._remaining_quota(h) > 0]
            candidates = [h for h in candidates if not (self.has_bath[h] and floor > 4)]
            
            if not candidates:
                continue
            
            def score(h):
                s = 0
                current = self._get_floors(h)
                if floor in current:
                    s += 1000
                elif len(current) < 2:
                    if not current:
                        s += 500
                    elif abs(floor - min(current)) <= 2 or abs(floor - max(current)) <= 2:
                        s += 500
                s += self._remaining_quota(h) * 10
                if is_twin and self._count_twins(h) < self.twin_quotas[h]:
                    s += 5
                elif not is_twin and self._count_twins(h) >= self.twin_quotas[h]:
                    s += 5
                return s
            
            hk_id = max(candidates, key=score)
            self.allocation[hk_id].append(room)
            used.add(room)
    
    def _adjust_twin_quotas_priority(self):
        """Twin調整（指定ありHKを優先的に調整）"""
        for _ in range(2000):
            changed = False
            
            # 指定ありHKでTwin過剰/不足を探す
            for hk_id in self.hk_ids:
                if not self.twin_quota_specified[hk_id]:
                    continue
                
                current = self._count_twins(hk_id)
                target = self.twin_quotas[hk_id]
                
                if current > target:
                    # Twinが多すぎる → 他のHK（autoも含む）に渡す
                    my_twins = [r for r in self.allocation[hk_id] 
                               if r in self.twin_rooms and r not in self.eco_rooms]
                    for my_twin in my_twins:
                        if self._count_twins(hk_id) <= target:
                            break
                        # スワップ相手を探す（指定ありでTwin不足、またはauto）
                        for other in self.hk_ids:
                            if other == hk_id:
                                continue
                            # autoのHKは常にスワップ相手になれる
                            if self.twin_quota_specified[other] and self._count_twins(other) >= self.twin_quotas[other]:
                                continue
                            other_singles = [r for r in self.allocation[other] 
                                           if r not in self.twin_rooms and r not in self.eco_rooms]
                            for other_single in other_singles:
                                if self._can_swap(hk_id, other, my_twin, other_single):
                                    self._do_swap(hk_id, other, my_twin, other_single)
                                    changed = True
                                    break
                            if changed:
                                break
                        if changed:
                            break
                
                elif current < target:
                    # Twinが足りない → 他のHK（autoまたはTwin過剰）から取る
                    my_singles = [r for r in self.allocation[hk_id] 
                                 if r not in self.twin_rooms and r not in self.eco_rooms]
                    for my_single in my_singles:
                        if self._count_twins(hk_id) >= target:
                            break
                        for other in self.hk_ids:
                            if other == hk_id:
                                continue
                            # autoのHKからは取れる、指定ありはTwin過剰の場合のみ
                            if self.twin_quota_specified[other] and self._count_twins(other) <= self.twin_quotas[other]:
                                continue
                            other_twins = [r for r in self.allocation[other] 
                                          if r in self.twin_rooms and r not in self.eco_rooms]
                            for other_twin in other_twins:
                                if self._can_swap(hk_id, other, my_single, other_twin):
                                    self._do_swap(hk_id, other, my_single, other_twin)
                                    changed = True
                                    break
                            if changed:
                                break
                        if changed:
                            break
                
                if changed:
                    break
            
            if not changed:
                break
    
    def _can_swap(self, hk1, hk2, room1, room2):
        f1, f2 = _fl(room1), _fl(room2)
        
        if self.has_bath[hk1] and f2 > 4:
            return False
        if self.has_bath[hk2] and f1 > 4:
            return False
        
        floors1_after = set()
        for r in self.allocation[hk1]:
            if r != room1 and r not in self.eco_rooms:
                floors1_after.add(_fl(r))
        floors1_after.add(f2)
        
        if len(floors1_after) > 2:
            return False
        if len(floors1_after) == 2:
            f_list = sorted(floors1_after)
            if f_list[1] - f_list[0] > 2:
                return False
        
        floors2_after = set()
        for r in self.allocation[hk2]:
            if r != room2 and r not in self.eco_rooms:
                floors2_after.add(_fl(r))
        floors2_after.add(f1)
        
        if len(floors2_after) > 2:
            return False
        if len(floors2_after) == 2:
            f_list = sorted(floors2_after)
            if f_list[1] - f_list[0] > 2:
                return False
        
        return True
    
    def _do_swap(self, hk1, hk2, room1, room2):
        self.allocation[hk1].remove(room1)
        self.allocation[hk2].remove(room2)
        self.allocation[hk1].append(room2)
        self.allocation[hk2].append(room1)
    
    def _allocate_eco_rooms(self):
        for room in sorted(self.eco_out_rooms):
            candidates = [h for h in self.hk_ids if _fl(room) in self._get_floors(h)]
            if candidates:
                self.allocation[min(candidates, key=lambda h: len(self.allocation[h]))].append(room)
        
        eco_only = self.eco_rooms - self.eco_out_rooms
        for room in sorted(eco_only):
            candidates = [h for h in self.hk_ids if _fl(room) in self._get_floors(h)]
            if not candidates:
                candidates = list(self.hk_ids)
            if candidates:
                self.allocation[min(candidates, key=lambda h: len(self.allocation[h]))].append(room)


if __name__ == "__main__":
    from collections import defaultdict
    
    # 新テストケース
    rooms = {204: None, 205: None, 207: None, 208: None, 209: None, 210: None, 215: None, 216: None, 217: None, 305: None, 312: None, 313: None, 314: None, 315: None, 316: None, 404: None, 406: None, 409: None, 410: None, 412: None, 413: None, 415: None, 416: None, 417: None, 502: None, 505: None, 507: None, 508: None, 509: None, 510: None, 513: None, 515: None, 516: None, 517: None, 601: None, 602: None, 603: None, 604: None, 605: None, 606: None, 617: None, 702: None, 711: None, 712: None, 713: None, 714: None, 717: None, 804: None, 805: None, 806: None, 807: None, 808: None, 811: None, 812: None, 813: None, 815: None, 816: None, 817: None, 902: None, 903: None, 906: None, 907: None, 908: None, 912: None, 913: None, 915: None, 1002: None, 1003: None, 1004: None, 1005: None, 1006: None, 1007: None, 1016: None, 1017: None}
    eco_rooms = [206, 212, 308, 511, 512, 710, 715]
    eco_out_rooms = [212, 511, 715]
    twin_rooms = [214, 216, 217, 314, 316, 317, 414, 416, 417, 514, 516, 517, 614, 616, 617, 714, 716, 717, 814, 816, 817, 914, 916, 917, 1014, 1016, 1017]
    housekeepers = [{'id': 1, 'room_quota': 7, 'twin_quota': -1, 'has_bath': True}, {'id': 2, 'room_quota': 8, 'twin_quota': 2, 'has_bath': True}, {'id': 3, 'room_quota': 8, 'twin_quota': 2, 'has_bath': True}, {'id': 4, 'room_quota': 10, 'twin_quota': -1, 'has_bath': False}, {'id': 5, 'room_quota': 10, 'twin_quota': -1, 'has_bath': False}, {'id': 6, 'room_quota': 10, 'twin_quota': -1, 'has_bath': False}, {'id': 7, 'room_quota': 10, 'twin_quota': -1, 'has_bath': False}, {'id': 8, 'room_quota': 11, 'twin_quota': -1, 'has_bath': False}]
    
    all_eco = set(eco_rooms) | set(eco_out_rooms)
    
    result = assign_rooms(rooms, eco_rooms, eco_out_rooms, twin_rooms, [], housekeepers, 24, 28, 5, 50)
    
    print("=" * 80)
    print("v28 新テストケース")
    print("=" * 80)
    
    hk_rooms = defaultdict(list)
    for room, hk_id in result.items():
        hk_rooms[hk_id].append(room)
    
    errors = []
    for hk_id in sorted(hk_rooms.keys()):
        assigned = hk_rooms[hk_id]
        normal = [r for r in assigned if r not in all_eco]
        twins = sum(1 for r in normal if r in twin_rooms)
        floors = sorted(set(r // 100 for r in normal))
        hk = housekeepers[hk_id - 1]
        quota = hk['room_quota']
        twin_quota = hk['twin_quota']
        bath = "🛁" if hk['has_bath'] else "  "
        
        q_ok = "✓" if len(normal) == quota else "✗"
        t_ok = "✓" if twin_quota < 0 or twins == twin_quota else "✗"
        f_ok = "✓" if len(floors) <= 2 else "✗"
        
        tq_str = str(twin_quota) if twin_quota >= 0 else "auto"
        
        if len(floors) > 2:
            errors.append(f"HK{hk_id}: Floor")
        if len(normal) != quota:
            errors.append(f"HK{hk_id}: Room")
        if twin_quota >= 0 and twins != twin_quota:
            errors.append(f"HK{hk_id}: Twin({twins}/{twin_quota})")
        
        print(f"{bath} HK{hk_id:2d}: {len(normal):2d}/{quota}室{q_ok} Twin:{twins}/{tq_str}{t_ok} Floor:{floors}{f_ok}")
    
    if errors:
        print(f"\n❌ {len(errors)}件: {errors}")
    else:
        print("\n✅ 全制約OK")