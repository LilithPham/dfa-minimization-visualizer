class DFAMinimizer:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states          # list: ['q0', 'q1', 'q2',...]
        self.alphabet = alphabet      # list: ['0', '1']
        self.transitions = transitions # dict: {('q0', '0'): 'q1', ...}
        self.start_state = start_state # string: 'q0'
        self.final_states = final_states # list: ['q1', 'q3']
        
        # Mảng này cực kỳ quan trọng để làm UI tương tác
        self.history = [] 

    def get_reachable_states(self):
        """Bước 1: BFS để tìm các state có thể chạm tới từ start_state"""
        reachable = {self.start_state}
        queue = [self.start_state]
        
        while queue:
            current = queue.pop(0)
            for symbol in self.alphabet:
                next_state = self.transitions.get((current, symbol))
                if next_state and next_state not in reachable:
                    reachable.add(next_state)
                    queue.append(next_state)
                    
        inaccessible = set(self.states) - reachable
        self.history.append({
            "step_name": "Bước 1: Xóa các node cô lập (Inaccessible States)",
            "description": f"Tìm thấy các node có thể đi tới: {reachable}. Xóa các node: {inaccessible if inaccessible else 'Không có'}",
            "reachable": list(reachable)
        })
        return list(reachable)

    def initialize_table(self, reachable_states):
        """Bước 2: Tạo bảng tam giác và đánh dấu Base Case (Đích - Không Đích)"""
        # Tạo danh sách các cặp (p, q) duy nhất
        pairs = []
        for i in range(len(reachable_states)):
            for j in range(i + 1, len(reachable_states)):
                pairs.append((reachable_states[i], reachable_states[j]))
        
        marked = set()
        # Đánh dấu những cặp có 1 đứa là Final, 1 đứa không phải Final
        for p, q in pairs:
            p_in_F = p in self.final_states
            q_in_F = q in self.final_states
            if p_in_F != q_in_F:  # Phép XOR: một True một False
                marked.add((p, q))
                marked.add((q, p)) # Đánh dấu cả 2 chiều cho dễ tra cứu
                
        self.history.append({
            "step_name": "Bước 2: Đánh dấu Base Case",
            "description": "Đánh dấu (X) các cặp chứa 1 node là Đích và 1 node Không Phải Đích.",
            "marked_pairs": list(marked)
        })
        return pairs, marked

    def mark_procedure(self, pairs, marked):
        """Bước 3: Vòng lặp dò mìn (Thuật toán chính)"""
        changed = True
        iteration = 1
        
        while changed:
            changed = False
            for p, q in pairs:
                if (p, q) not in marked:
                    # Kiểm tra xem tương lai của tụi nó có dẫn vào ô đã bị (X) không
                    for a in self.alphabet:
                        p_next = self.transitions.get((p, a))
                        q_next = self.transitions.get((q, a))
                        
                        if p_next and q_next and (p_next, q_next) in marked:
                            marked.add((p, q))
                            marked.add((q, p))
                            changed = True
                            
                            self.history.append({
                                "step_name": f"Bước 3 (Vòng {iteration}): Dò mìn",
                                "description": f"Đánh dấu cặp ({p}, {q}) vì khi đọc chữ '{a}', chúng đi tới cặp ({p_next}, {q_next}) đã bị đánh dấu.",
                                "marked_pairs": list(marked)
                            })
                            break # Chuyển sang cặp tiếp theo
            iteration += 1
            
        return marked

    def run(self):
        """Hàm tổng kích hoạt toàn bộ luồng chạy"""
        self.history = [] # Reset lịch sử
        reachable = self.get_reachable_states()
        pairs, marked = self.initialize_table(reachable)
        final_marked = self.mark_procedure(pairs, marked)
        
        # Những cặp không bị đánh dấu chính là Equivalent States
        equivalent_pairs = [ (p,q) for p,q in pairs if (p,q) not in final_marked ]
        self.history.append({
            "step_name": "Bước 4: Chốt hạ (Reduce)",
            "description": f"Thuật toán kết thúc. Các cặp node giống nhau để gộp là: {equivalent_pairs if equivalent_pairs else 'Không có'}",
            "equivalent_pairs": equivalent_pairs
        })
        return self.history