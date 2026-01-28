"""
ホテル清掃指示書 自動振り分けシステム v40
- パフォーマンス改善
- 3フロアは最小限（やむを得ない場合のみ、3フロア目はエコのみ）
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
    
    for attempt in range(200):
        hk_to_rooms = allocator.allocate(strategy=attempt)
        score, errors = allocator.evaluate_solution(hk_to_rooms)
        
        if score > best_score:
            best_score = score
            best_result = hk_to_rooms
        
        allocator.allocation = {h: [] for h in allocator.hk_ids}
    
    result = _renumber_hks(best_result, housekeepers)
    return result


def _renumber_hks(hk_to_rooms, housekeepers):
    hk_info = []
    has_bath_map = {hk['id']: hk.get('has_bath', False) for hk in housekeepers}
    
    for hk_id, rooms in hk_to_rooms.items():
        min_floor = min(r // 100 for r in rooms) if rooms else 999
        is_bath = has_bath_map.get(hk_id, False)
        hk_info.append((hk_id, is_bath, min_floor))
    
    hk_info.sort(key=lambda x: (0 if x[1] else 1, x[2]))
    
    old_to_new = {}
    for new_id, (old_id, _, _) in enumerate(hk_info, 1):
        old_to_new[old_id] = new_id
    
    result = {}
    for hk_id, rooms in hk_to_rooms.items():
        new_hk_id = old_to_new[hk_id]
        for room in rooms:
            result[room] = new_hk_id
    
    return result


def _fl(room):
    return room // 100


class _RoomAllocator:
    MAX_HK_PER_FLOOR = 3
    
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
        
        self.twin_quota_specified = {}
        self.twin_quotas = {}
        self._calculate_twin_quotas(housekeepers)
        
        self.bath_hks = [h for h in self.hk_ids if self.has_bath[h]]
        self.normal_hks = [h for h in self.hk_ids if not self.has_bath[h]]
        
        self.allocation = {h: [] for h in self.hk_ids}
        
        self.eco_floor_counts = defaultdict(int)
        for r in self.eco_rooms:
            self.eco_floor_counts[_fl(r)] += 1
    
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
    
    def _count_eco(self, hk_id):
        return sum(1 for r in self.allocation[hk_id] if r in self.eco_rooms)
    
    def _get_floors(self, hk_id):
        return set(_fl(r) for r in self.allocation[hk_id] if r not in self.eco_rooms)
    
    def _get_all_floors(self, hk_id):
        return set(_fl(r) for r in self.allocation[hk_id])
    
    def _remaining_quota(self, hk_id):
        return self.room_quotas[hk_id] - self._count_normal(hk_id)
    
    def _count_hks_on_floor(self, floor):
        count = 0
        for h in self.hk_ids:
            if floor in self._get_all_floors(h):
                count += 1
        return count
    
    def _can_add_floor(self, hk_id, new_floor):
        """通常部屋のフロア追加可否（2フロア以内 + フロア間距離2以内）"""
        if self.has_bath[hk_id] and new_floor > 4:
            return False
        
        current = self._get_floors(hk_id)
        all_current = self._get_all_floors(hk_id)
        
        if new_floor in all_current:
            return True
        
        if len(current) >= 2:
            return False
        
        if len(current) == 1:
            existing = list(current)[0]
            if abs(new_floor - existing) > 2:
                return False
        
        if self._count_hks_on_floor(new_floor) >= self.MAX_HK_PER_FLOOR:
            return False
        
        return True
    
    def _can_add_eco_floor(self, hk_id, eco_floor):
        """
        エコ部屋のフロア追加可否
        - 基本は2フロア以内
        - やむを得ない場合のみ3フロア目（エコのみ）を許容
        """
        if self.has_bath[hk_id] and eco_floor > 4:
            return False
        
        all_floors = self._get_all_floors(hk_id)
        normal_floors = self._get_floors(hk_id)
        
        if eco_floor in all_floors:
            return True
        
        if self._count_hks_on_floor(eco_floor) >= self.MAX_HK_PER_FLOOR:
            return False
        
        # 2フロア未満なら追加可能
        if len(all_floors) < 2:
            return True
        
        # 2フロアある場合、3フロア目はエコのみとして許容（やむを得ない場合）
        if len(all_floors) == 2 and len(normal_floors) <= 2:
            return True
        
        return False
    
    def evaluate_solution(self, hk_to_rooms):
        score = 0
        total_errors = 0
        
        floor_hk_count = defaultdict(set)
        for hk_id in self.hk_ids:
            rooms = hk_to_rooms[hk_id]
            for r in rooms:
                floor_hk_count[_fl(r)].add(hk_id)
        
        three_floor_count = 0
        
        for hk_id in self.hk_ids:
            rooms = hk_to_rooms[hk_id]
            normal = [r for r in rooms if r not in self.eco_rooms]
            
            room_diff = abs(len(normal) - self.room_quotas[hk_id])
            score -= room_diff * 10000
            total_errors += room_diff
            
            # 通常部屋のフロアは2以内
            floors = set(_fl(r) for r in normal)
            floor_excess = max(0, len(floors) - 2)
            score -= floor_excess * 5000
            total_errors += floor_excess
            
            # 全フロアは3以内
            all_floors = set(_fl(r) for r in rooms)
            if len(all_floors) > 3:
                score -= (len(all_floors) - 3) * 3000
                total_errors += len(all_floors) - 3
            
            # 3フロアには大きなペナルティ（最小限にする）
            if len(all_floors) == 3:
                three_floor_count += 1
                score -= 2000  # 3フロアへの大きなペナルティ
            
            # ツイン偏りペナルティ
            twins = sum(1 for r in normal if r in self.twin_rooms)
            twin_diff = abs(twins - self.twin_quotas[hk_id])
            score -= twin_diff * 100
            if self.twin_quota_specified.get(hk_id, False):
                total_errors += twin_diff
        
        # エコの偏りペナルティ
        eco_counts = [sum(1 for r in hk_to_rooms[h] if r in self.eco_rooms) for h in self.hk_ids]
        if eco_counts:
            eco_diff = max(eco_counts) - min(eco_counts)
            score -= eco_diff * 500
        
        # ツインの偏りペナルティ（全体）- 強化
        twin_counts = [sum(1 for r in hk_to_rooms[h] if r in self.twin_rooms and r not in self.eco_rooms) for h in self.hk_ids]
        if twin_counts:
            twin_diff = max(twin_counts) - min(twin_counts)
            score -= twin_diff * 800  # ペナルティ強化
            if twin_diff > 2:
                score -= (twin_diff - 2) * 1500  # 差が2を超えると追加ペナルティ
        
        for floor, hks in floor_hk_count.items():
            if len(hks) > self.MAX_HK_PER_FLOOR:
                excess = len(hks) - self.MAX_HK_PER_FLOOR
                score -= excess * 800
                total_errors += excess
        
        return score, total_errors
    
    def allocate(self, strategy=0):
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
        else:
            normal_shuffled = list(self.normal_hks)
            random.seed(strategy)
            random.shuffle(normal_shuffled)
            hk_queue = list(self.bath_hks) + normal_shuffled
        
        reverse_floors = (strategy // 20) % 2 == 1
        
        for hk_id in hk_queue:
            self._allocate_hk(hk_id, used, reverse_floors)
        
        self._fallback_allocation(used)
        self._adjust_twin_balance()
        self._allocate_eco_rooms()
        
        return {h: sorted(self.allocation[h]) for h in self.hk_ids}
    
    def _allocate_hk(self, hk_id, used, reverse_floors=False):
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
            if avail and self._count_hks_on_floor(f) < self.MAX_HK_PER_FLOOR:
                start_floor = f
                break
        
        if start_floor is None:
            return
        
        assigned = 0
        twins_assigned = 0
        
        # 開始フロア
        available = [r for r in self.floor_rooms[start_floor] if r not in used]
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
        
        for room in singles_here:
            if assigned >= quota:
                break
            self.allocation[hk_id].append(room)
            used.add(room)
            assigned += 1
        
        for room in twins_here[twins_needed:]:
            if room in used or assigned >= quota:
                continue
            self.allocation[hk_id].append(room)
            used.add(room)
            assigned += 1
            twins_assigned += 1
        
        if assigned >= quota:
            return
        
        # 2フロア目
        for floor in available_floors:
            if floor == start_floor or assigned >= quota:
                continue
            if not self._can_add_floor(hk_id, floor):
                continue
            
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
            
            for room in singles_here:
                if assigned >= quota:
                    break
                self.allocation[hk_id].append(room)
                used.add(room)
                assigned += 1
            
            for room in twins_here[twins_needed:]:
                if room in used or assigned >= quota:
                    continue
                self.allocation[hk_id].append(room)
                used.add(room)
                assigned += 1
                twins_assigned += 1
    
    def _fallback_allocation(self, used):
        remaining = [r for r in self.normal_rooms if r not in used]
        
        for room in sorted(remaining):
            floor = _fl(room)
            is_twin = room in self.twin_rooms
            
            candidates = [h for h in self.hk_ids 
                         if self._remaining_quota(h) > 0 and self._can_add_floor(h, floor)]
            
            if not candidates:
                candidates = [h for h in self.hk_ids 
                             if self._remaining_quota(h) > 0 
                             and not (self.has_bath[h] and floor > 4)]
            
            if not candidates:
                continue
            
            def score(h):
                s = 0
                current = self._get_floors(h)
                all_current = self._get_all_floors(h)
                
                if floor in all_current:
                    s += 1000
                elif len(current) < 2:
                    if not current:
                        s += 500
                    elif abs(floor - min(current)) <= 2 or abs(floor - max(current)) <= 2:
                        s += 800
                
                s += self._remaining_quota(h) * 10
                
                if is_twin and self._count_twins(h) < self.twin_quotas[h]:
                    s += 5
                
                return s
            
            hk_id = max(candidates, key=score)
            self.allocation[hk_id].append(room)
            used.add(room)
    
    def _adjust_twin_balance(self):
        """ツイン平等化（チェーンスワップ対応）"""
        # 指定されたtwin_quotaを優先
        for _ in range(50):
            changed = False
            
            for hk_id in self.hk_ids:
                if not self.twin_quota_specified.get(hk_id, False):
                    continue
                
                current = self._count_twins(hk_id)
                target = self.twin_quotas[hk_id]
                
                if current >= target:
                    continue
                
                my_singles = [r for r in self.allocation[hk_id] 
                             if r not in self.twin_rooms and r not in self.eco_rooms]
                
                for other in self.hk_ids:
                    if other == hk_id or self._count_twins(hk_id) >= target:
                        break
                    
                    if self.twin_quota_specified.get(other, False):
                        if self._count_twins(other) <= self.twin_quotas[other]:
                            continue
                    
                    other_twins = [r for r in self.allocation[other] 
                                  if r in self.twin_rooms and r not in self.eco_rooms]
                    
                    for my_single in list(my_singles):
                        if self._count_twins(hk_id) >= target:
                            break
                        for other_twin in list(other_twins):
                            if self._can_swap(hk_id, other, my_single, other_twin):
                                self._do_swap(hk_id, other, my_single, other_twin)
                                my_singles.remove(my_single)
                                changed = True
                                break
            
            if not changed:
                break
        
        # 全体の均等化（直接交換 + チェーンスワップ）
        for _ in range(150):
            twin_counts = {h: self._count_twins(h) for h in self.hk_ids}
            max_twin = max(twin_counts.values())
            min_twin = min(twin_counts.values())
            
            if max_twin - min_twin <= 1:
                break
            
            changed = False
            max_hks = [h for h in self.hk_ids if twin_counts[h] == max_twin]
            min_hks = [h for h in self.hk_ids if twin_counts[h] == min_twin]
            
            # 直接交換を試す
            for max_hk in max_hks:
                if changed:
                    break
                my_twins = [r for r in self.allocation[max_hk] 
                           if r in self.twin_rooms and r not in self.eco_rooms]
                
                for min_hk in min_hks:
                    if max_hk == min_hk:
                        continue
                    other_singles = [r for r in self.allocation[min_hk] 
                                   if r not in self.twin_rooms and r not in self.eco_rooms]
                    
                    for my_twin in my_twins:
                        for other_single in other_singles:
                            if self._can_swap(max_hk, min_hk, my_twin, other_single):
                                self._do_swap(max_hk, min_hk, my_twin, other_single)
                                changed = True
                                break
                        if changed:
                            break
                    if changed:
                        break
            
            # 直接交換できない場合、チェーンスワップ
            if not changed:
                for max_hk in max_hks:
                    if changed:
                        break
                    my_twins = [r for r in self.allocation[max_hk] 
                               if r in self.twin_rooms and r not in self.eco_rooms]
                    
                    for min_hk in min_hks:
                        if changed:
                            break
                        if max_hk == min_hk:
                            continue
                        
                        other_singles = [r for r in self.allocation[min_hk] 
                                       if r not in self.twin_rooms and r not in self.eco_rooms]
                        
                        # 中間HKを経由
                        for mid_hk in self.hk_ids:
                            if mid_hk in [max_hk, min_hk]:
                                continue
                            
                            mid_singles = [r for r in self.allocation[mid_hk] 
                                          if r not in self.twin_rooms and r not in self.eco_rooms]
                            mid_twins = [r for r in self.allocation[mid_hk] 
                                        if r in self.twin_rooms and r not in self.eco_rooms]
                            
                            # max_hk -> mid_hk: ツイン→シングル
                            for my_twin in my_twins:
                                if changed:
                                    break
                                for mid_single in mid_singles:
                                    if not self._can_swap(max_hk, mid_hk, my_twin, mid_single):
                                        continue
                                    
                                    # mid_hk -> min_hk: ツイン→シングル
                                    for mid_twin in mid_twins:
                                        for other_single in other_singles:
                                            if self._can_swap(mid_hk, min_hk, mid_twin, other_single):
                                                # 両方の交換を実行
                                                self._do_swap(max_hk, mid_hk, my_twin, mid_single)
                                                self._do_swap(mid_hk, min_hk, mid_twin, other_single)
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
        
        # hk1のスワップ後フロア
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
        
        # hk2のスワップ後フロア
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
        """エコ部屋をバランス良く配分（2フロア優先、やむを得ない場合のみ3フロア）"""
        total_eco = len(self.eco_rooms)
        avg_eco = total_eco / len(self.hk_ids) if self.hk_ids else 0
        
        # エコ外部屋の割り当て
        for room in sorted(self.eco_out_rooms):
            floor = _fl(room)
            candidates = [h for h in self.hk_ids if floor in self._get_floors(h)]
            
            if candidates:
                hk_id = min(candidates, key=lambda h: (self._count_eco(h), h))
                self.allocation[hk_id].append(room)
            else:
                available = [h for h in self.hk_ids 
                            if len(self._get_all_floors(h)) < 2 
                            and self._count_hks_on_floor(floor) < self.MAX_HK_PER_FLOOR
                            and not (self.has_bath[h] and floor > 4)]
                if available:
                    hk_id = min(available, key=lambda h: (self._count_eco(h), h))
                    self.allocation[hk_id].append(room)
        
        # その他のエコ部屋（エコが多いフロアから処理してバランスを取る）
        eco_only = sorted(self.eco_rooms - self.eco_out_rooms, 
                         key=lambda r: (-self.eco_floor_counts[_fl(r)], r))
        
        for room in eco_only:
            floor = _fl(room)
            
            # 現在のエコ数を計算
            eco_counts = {h: self._count_eco(h) for h in self.hk_ids}
            min_eco = min(eco_counts.values())
            
            # エコが少ないHKを優先的に選ぶ
            candidates = []
            
            # 優先順位1: 既存フロアを持ち、エコが最小〜平均未満のHK
            candidates = [h for h in self.hk_ids 
                         if floor in self._get_all_floors(h)
                         and eco_counts[h] < avg_eco]
            
            # 優先順位2: 2フロア未満でエコが少ないHK
            if not candidates:
                candidates = [h for h in self.hk_ids 
                             if len(self._get_all_floors(h)) < 2
                             and eco_counts[h] <= min_eco + 2
                             and self._count_hks_on_floor(floor) < self.MAX_HK_PER_FLOOR
                             and not (self.has_bath[h] and floor > 4)]
            
            # 優先順位3: エコが少ないHKに3フロア目として追加
            if not candidates:
                candidates = [h for h in self.hk_ids 
                             if self._can_add_eco_floor(h, floor)
                             and eco_counts[h] <= min_eco + 2]
            
            # 優先順位4: 既存フロアを持つHK（エコ数関係なく）
            if not candidates:
                candidates = [h for h in self.hk_ids 
                             if floor in self._get_all_floors(h)]
            
            # 優先順位5: 3フロア目として追加可能な全HK
            if not candidates:
                candidates = [h for h in self.hk_ids 
                             if self._can_add_eco_floor(h, floor)]
            
            if not candidates:
                candidates = list(self.hk_ids)
            
            # エコが最も少ないHKを選択
            hk_id = min(candidates, key=lambda h: (eco_counts[h], len(self._get_all_floors(h)), h))
            self.allocation[hk_id].append(room)