class DFAMinimizer:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states
        self.history = [] 

    def get_reachable_states(self):
        """Phase 1: Remove inaccessible states using Breadth-First Search (BFS)"""
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
            "step_name": "Phase 1: State Reachability Analysis",
            "description": f"Identified reachable states: {reachable}. Removed inaccessible states: {inaccessible if inaccessible else 'None'}.",
            "reachable": list(reachable)
        })
        return list(reachable)

    def initialize_table(self, reachable_states):
        """Phase 2: Generate state pairs and mark base cases (Distinguishable by λ)"""
        pairs = []
        for i in range(len(reachable_states)):
            for j in range(i + 1, len(reachable_states)):
                pairs.append((reachable_states[i], reachable_states[j]))
        
        marked = set()
        for p, q in pairs:
            # A pair is distinguishable if one is a final state and the other is not
            if (p in self.final_states) != (q in self.final_states):
                marked.add((p, q))
                marked.add((q, p))
                
        self.history.append({
            "step_name": "Phase 2: Base Case Marking",
            "description": "Marked pairs where exactly one state is a Final State (F).",
            "marked_pairs": list(marked)
        })
        return pairs, marked

    def mark_procedure(self, pairs, marked):
        """Phase 3: Iterative Table-Filling (Marking) Algorithm"""
        changed = True
        iteration = 1
        
        while changed:
            changed = False
            for p, q in pairs:
                if (p, q) not in marked:
                    for a in self.alphabet:
                        p_next = self.transitions.get((p, a))
                        q_next = self.transitions.get((q, a))
                        
                        if p_next and q_next and (p_next, q_next) in marked:
                            marked.add((p, q))
                            marked.add((q, p))
                            changed = True
                            
                            self.history.append({
                                "step_name": f"Phase 3 (Iteration {iteration}): Marking Process",
                                "description": f"Marked ({p}, {q}) because input '{a}' leads to a previously marked pair ({p_next}, {q_next}).",
                                "marked_pairs": list(marked)
                            })
                            break
            iteration += 1
            
        return marked

    def run(self):
        """Execute complete minimization and construct the final Reduced DFA"""
        self.history = [] 
        reachable = self.get_reachable_states()
        pairs, marked = self.initialize_table(reachable)
        final_marked = self.mark_procedure(pairs, marked)
        
        # Phase 4: Construct Equivalence Classes
        equiv_classes = []
        for state in reachable:
            placed = False
            for eq_class in equiv_classes:
                rep = list(eq_class)[0]
                # If a pair is not marked, the states are indistinguishable
                if (state, rep) not in final_marked:
                    eq_class.add(state)
                    placed = True
                    break
            if not placed:
                equiv_classes.append({state})
                
        # Generate new state names and mapping
        state_map = {}
        for eq_class in equiv_classes:
            new_name = "_".join(sorted(list(eq_class)))
            for s in eq_class:
                state_map[s] = new_name
                
        # Reconstruct Reduced DFA Components
        reduced_states = list(set(state_map.values()))
        reduced_start = state_map[self.start_state]
        reduced_finals = list(set([state_map[f] for f in self.final_states if f in state_map]))
        
        reduced_transitions = {}
        for (src, symbol), dst in self.transitions.items():
            if src in state_map and dst in state_map:
                reduced_transitions[(state_map[src], symbol)] = state_map[dst]

        # Extract indistinguishable pairs for UI display
        equivalent_pairs = [ (p,q) for p,q in pairs if (p,q) not in final_marked ]
        
        self.history.append({
            "step_name": "Phase 4: Reduced DFA Construction",
            "description": "The minimization process is complete. Equivalent states have been merged into combined nodes.",
            "equivalent_pairs": equivalent_pairs,
            "reduced_dfa": {
                "states": reduced_states,
                "transitions": reduced_transitions,
                "start_state": reduced_start,
                "final_states": reduced_finals
            }
        })
        return self.history
class NFAToDFAConverter:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = [a for a in alphabet if a != 'e'] # Bỏ epsilon khỏi bảng chữ cái DFA
        self.transitions = transitions # Dictionary dạng: (src, sym): [dst1, dst2]
        self.start_state = start_state
        self.final_states = final_states

    def epsilon_closure(self, state_set):
        """Tìm tất cả các state có thể tới được bằng nhánh Epsilon (e)"""
        closure = set(state_set)
        stack = list(state_set)
        while stack:
            s = stack.pop()
            if (s, 'e') in self.transitions:
                for dest in self.transitions[(s, 'e')]:
                    if dest not in closure:
                        closure.add(dest)
                        stack.append(dest)
        return frozenset(closure)

    def move(self, state_set, symbol):
        """Tìm các state có thể tới được khi đọc 1 symbol"""
        result = set()
        for s in state_set:
            if (s, symbol) in self.transitions:
                result.update(self.transitions[(s, symbol)])
        return frozenset(result)

    def run(self):
        history = []
        # Bước 1: Tìm Trạng thái bắt đầu của DFA = Epsilon Closure của q0 NFA
        dfa_start = self.epsilon_closure([self.start_state])
        unmarked_states = [dfa_start]
        dfa_states = [dfa_start]
        dfa_transitions = {}

        history.append({
            "step_name": "Phase 1: Initialization",
            "description": f"Compute ε-closure of Start State '{self.start_state}' -> Initial DFA State: {set(dfa_start)}"
        })

        # Bước 2: Vòng lặp Subset Construction
        step_count = 2
        while unmarked_states:
            current_subset = unmarked_states.pop(0)

            for symbol in self.alphabet:
                # Công thức: Epsilon_Closure(Move(Current, Symbol))
                move_res = self.move(current_subset, symbol)
                target_subset = self.epsilon_closure(move_res)

                if not target_subset:
                    continue # Nếu rỗng thì bỏ qua (hoặc hiểu là rơi vào TRAP)

                if target_subset not in dfa_states:
                    dfa_states.append(target_subset)
                    unmarked_states.append(target_subset)

                dfa_transitions[(current_subset, symbol)] = target_subset
                
                history.append({
                    "step_name": f"Phase {step_count}: Process Symbol '{symbol}'",
                    "description": f"From {set(current_subset)} read '{symbol}' -> Move to {set(move_res)} -> ε-closure -> New State {set(target_subset)}"
                })
                step_count += 1

        # Bước 3: Định dạng lại output cho dễ vẽ đồ thị
        def format_name(s_set):
            return "{" + ", ".join(sorted(list(s_set))) + "}"

        final_q = [format_name(s) for s in dfa_states]
        final_start = format_name(dfa_start)
        final_f = [format_name(s) for s in dfa_states if any(fs in s for fs in self.final_states)]
        
        final_delta = {}
        for (src, sym), dst in dfa_transitions.items():
            final_delta[(format_name(src), sym)] = format_name(dst)

        history.append({
            "step_name": "Final Phase: Equivalent DFA Generated",
            "description": "All subsets evaluated. Final states are those containing any of the original NFA final states.",
            "converted_dfa": {
                "q": final_q, "sigma": self.alphabet, "q0": final_start, "f": final_f, "delta": final_delta
            }
        })
        return history