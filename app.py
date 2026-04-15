"""
Automata Theory & Formal Languages - Midterm Project
Module: Interactive DFA Visualizer Suite
Description: Provides DFA Minimization using the Table-Filling Algorithm 
             and a Step-by-Step String Simulator with dynamic graph rendering.
             UI designed to match academic lecture slides strictly.

Student: Pham Minh Thu
Institution: Vietnamese-German University (VGU)
"""

import streamlit as st
import graphviz
import pandas as pd
import numpy as np
from dfa_logic import DFAMinimizer

# -----------------------------------------------------------------------------
# GLOBAL CONFIGURATION & SESSION PERSISTENCE
# -----------------------------------------------------------------------------
st.set_page_config(page_title="DFA Visualizer Suite - VGU", layout="wide")

if 'min_step' not in st.session_state: st.session_state.min_step = 0
if 'min_history' not in st.session_state: st.session_state.min_history = []
if 'original_dfa' not in st.session_state: st.session_state.original_dfa = None
if 'sim_step' not in st.session_state: st.session_state.sim_step = 0
if 'sim_trace' not in st.session_state: st.session_state.sim_trace = []
if 'sim_dfa' not in st.session_state: st.session_state.sim_dfa = None

# -----------------------------------------------------------------------------
# UTILITY & RENDERING FUNCTIONS
# -----------------------------------------------------------------------------
def parse_transitions(raw_text):
    """Parses user input text into a transition dictionary."""
    transitions = {}
    for line in raw_text.strip().split('\n'):
        if ':' in line:
            try:
                header, dst = line.split(':')
                src, sym = header.split(',')
                transitions[(src.strip(), sym.strip())] = dst.strip()
            except ValueError:
                continue
    return transitions

def render_graph(states, transitions, start, finals, active_node=None):
    """Generates a DOT graph representation of the DFA."""
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', size='8,5')
    
    dot.node('start_ptr', shape='none', label='')
    dot.edge('start_ptr', start)
    
    for s in states:
        shape = 'doublecircle' if s in finals else 'circle'
        if active_node and s == active_node:
            dot.node(s, shape=shape, style='filled', fillcolor='lightgreen')
        else:
            dot.node(s, shape=shape)
            
    edge_dict = {}
    for (src, symbol), dst in transitions.items():
        key = (src, dst)
        if key not in edge_dict: edge_dict[key] = []
        edge_dict[key].append(symbol)
        
    for (src, dst), symbols in edge_dict.items():
        dot.edge(src, dst, label=', '.join(symbols))
        
    return dot

def render_transition_table(states, alphabet, delta, finals):
    """Renders a clean pandas DataFrame for the Transition Table."""
    df = pd.DataFrame(index=states, columns=alphabet)
    for s in states:
        for a in alphabet:
            df.at[s, a] = delta.get((s, a), "-")
    
    # Highlight final states in the index for clarity
    df.index = [f"*{s} (Final)" if s in finals else s for s in states]
    return df

def get_all_pairs(states):
    """Generates all unique (p, q) pairs for the distinguishability table."""
    pairs = []
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            pairs.append((states[i], states[j]))
    return pairs

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.title("VGU Automata Lab")
module = st.sidebar.radio("Navigation Menu:", ["DFA Minimizer", "DFA String Simulator"])
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 CS Midterm Project")

# -----------------------------------------------------------------------------
# MODULE 1: DFA MINIMIZATION ENGINE
# -----------------------------------------------------------------------------
if module == "DFA Minimizer":
    st.title("DFA Minimization (Table-Filling Algorithm)")
    
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.header("1. Input Specification")
        q_in = st.text_input("States Q:", "q0, q1, q2, q3, q4")
        sigma_in = st.text_input("Alphabet Σ:", "0, 1")
        q0_in = st.text_input("Start State q0:", "q0")
        f_in = st.text_input("Final States F:", "q4")
        delta_in = st.text_area("Transitions (src,sym:dst):", 
"q0,0:q1\nq0,1:q3\nq1,0:q2\nq1,1:q4\nq2,0:q1\nq2,1:q4\nq3,0:q2\nq3,1:q4\nq4,0:q4\nq4,1:q4", height=200)
        
        if st.button("Run Minimization Algorithm", type="primary"):
            states = [s.strip() for s in q_in.split(",")]
            alphabet = [a.strip() for a in sigma_in.split(",")]
            start = q0_in.strip()
            finals = [i.strip() for i in f_in.split(",")]
            delta = parse_transitions(delta_in)
            
            st.session_state.original_dfa = {
                "q": states, "sigma": alphabet, "delta": delta, "q0": start, "f": finals
            }
            
            engine = DFAMinimizer(states, alphabet, delta, start, finals)
            st.session_state.min_history = engine.run()
            st.session_state.min_step = 0
            st.rerun()

    with right_col:
        st.header("2. Execution Visualizer")
        if not st.session_state.min_history:
            st.warning("Awaiting DFA definition. Please configure parameters on the left.")
        else:
            history = st.session_state.min_history
            idx = st.session_state.min_step
            current_step = history[idx]
            orig = st.session_state.original_dfa
            
            # Step Navigation
            btn1, btn2, progress_col = st.columns([1,1,2])
            with btn1:
                if st.button("Previous Step") and idx > 0:
                    st.session_state.min_step -= 1; st.rerun()
            with btn2:
                if st.button("Next Step") and idx < len(history)-1:
                    st.session_state.min_step += 1; st.rerun()
            with progress_col:
                st.progress((idx + 1) / len(history), f"Phase {idx+1} of {len(history)}")

            st.markdown("---")
            st.subheader(current_step['step_name'])
            st.info(current_step['description'])

            # Phase 1: Original Graph & Table
            if idx == 0:
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.write("**Transition Table:**")
                    st.table(render_transition_table(orig['q'], orig['sigma'], orig['delta'], orig['f']))
                with c2:
                    st.write("**State Transition Graph:**")
                    st.graphviz_chart(render_graph(orig['q'], orig['delta'], orig['q0'], orig['f']))
            
            # Phase 2 & 3: Distinguishability Grid (Slide-style)
            if 'marked_pairs' in current_step:
                st.write("**Distinguishability Table (Marking Process):**")
                
                # Retrieve all pairs from the current reachable states
                reachable = current_step.get('reachable', orig['q']) 
                if 'reachable' not in current_step:
                    # Fallback for phase 2 and 3 if reachable wasn't explicitly passed down
                    reachable = history[0]['reachable'] 
                    
                all_pairs = get_all_pairs(reachable)
                marked_set = set(tuple(p) for p in current_step['marked_pairs'])
                
                # Format pairs into strings with checkmarks
                display_pairs = []
                for p, q in all_pairs:
                    if (p, q) in marked_set or (q, p) in marked_set:
                        display_pairs.append(f"({p}, {q}) ✅")
                    else:
                        display_pairs.append(f"({p}, {q})")
                
                # Reshape into a visually appealing 2D Grid (4 columns)
                cols_count = 4
                while len(display_pairs) % cols_count != 0:
                    display_pairs.append("") # Pad empty cells
                grid = np.array(display_pairs).reshape(-1, cols_count)
                
                # BUG FIX: Use varying spaces to bypass Pandas duplicate column name error
                empty_cols = [" " * i for i in range(1, cols_count + 1)]
                df_grid = pd.DataFrame(grid, columns=empty_cols)
                
                st.table(df_grid)
            
            # Phase 4: Final Reduced DFA
            if 'reduced_dfa' in current_step:
                r = current_step['reduced_dfa']
                
                st.write("**Equivalent State Partitions (Equivalence Classes):**")
                partition_cols = st.columns(len(r['states']))
                for i, combined_state in enumerate(r['states']):
                    # Parse combined state names (e.g., "q1_q2_q3" -> "{q1, q2, q3}")
                    pretty_name = "{" + combined_state.replace('_', ', ') + "}"
                    partition_cols[i].success(f"**Partition {i+1}**\n\n{pretty_name}")
                
                st.markdown("---")
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.write("**Minimized Transition Table:**")
                    st.table(render_transition_table(r['states'], orig['sigma'], r['transitions'], r['final_states']))
                with c2:
                    st.write("**Minimized DFA Graph:**")
                    st.graphviz_chart(render_graph(r['states'], r['transitions'], r['start_state'], r['final_states']))

# -----------------------------------------------------------------------------
# MODULE 2: DFA STRING SIMULATOR
# -----------------------------------------------------------------------------
elif module == "DFA String Simulator":
    st.title("DFA Execution Trace Simulator")
    
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.header("1. Simulator Configuration")
        q_in = st.text_input("States Q:", "q0, q1, q2, q3, q4")
        sigma_in = st.text_input("Alphabet Σ:", "0, 1")
        q0_in = st.text_input("Start State q0:", "q0")
        f_in = st.text_input("Final States F:", "q4")
        delta_in = st.text_area("Transitions:", "q0,0:q1\nq0,1:q3\nq1,0:q2\nq1,1:q4\nq2,0:q1\nq2,1:q4\nq3,0:q2\nq3,1:q4\nq4,0:q4\nq4,1:q4")
        test_word = st.text_input("Input String to Process:", "01001")
        
        if st.button("Initialize Simulator", type="primary"):
            delta = parse_transitions(delta_in)
            curr_state = q0_in.strip()
            trace_log = [{"char": "START", "state": curr_state}]
            
            for char in test_word:
                curr_state = delta.get((curr_state, char), "REJECT/TRAP")
                trace_log.append({"char": char, "state": curr_state})
                
            st.session_state.sim_trace = trace_log
            st.session_state.sim_step = 0
            st.session_state.sim_dfa = {
                "q": q_in.split(","), "d": delta, 
                "q0": q0_in.strip(), "f": [i.strip() for i in f_in.split(",")]
            }
            st.rerun()

    with right_col:
        st.header("2. Step-by-Step Visualization")
        if not st.session_state.sim_trace:
            st.warning("Please configure the DFA and click 'Initialize Simulator'.")
        else:
            trace = st.session_state.sim_trace
            step_idx = st.session_state.sim_step
            dfa_context = st.session_state.sim_dfa
            
            c1, c2, c3 = st.columns([1,1,2])
            with c1:
                if st.button("Step Back") and step_idx > 0:
                    st.session_state.sim_step -= 1; st.rerun()
            with c2:
                if st.button("Step Forward") and step_idx < len(trace)-1:
                    st.session_state.sim_step += 1; st.rerun()
            
            current_log = trace[step_idx]
            st.write(f"**Read Symbol:** `{current_log['char']}` | **Current State:** `{current_log['state']}`")
            
            if step_idx == len(trace) - 1:
                if current_log['state'] in dfa_context['f']:
                    st.success("Result: STRING ACCEPTED")
                else: 
                    st.error("Result: STRING REJECTED")
            
            fig = render_graph(dfa_context['q'], dfa_context['d'], dfa_context['q0'], dfa_context['f'], current_log['state'])
            st.graphviz_chart(fig)