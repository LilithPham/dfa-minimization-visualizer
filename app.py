import streamlit as st
import graphviz
import pandas as pd
import numpy as np
import random
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
if 'sim_history' not in st.session_state: st.session_state.sim_history = [] # NEW: Test History
if 'rand_word' not in st.session_state: st.session_state.rand_word = "01001" # NEW: Random String State

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
            dot.node(s, shape=shape, style='filled', fillcolor='#7FFF00', color='red', penwidth='3')
        else:
            dot.node(s, shape=shape)
            
    if active_node and active_node not in states:
        dot.node(active_node, shape='octagon', style='filled', fillcolor='#FFB6C1', color='red', penwidth='3')
            
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
# HEADER & BRANDING (NEW)
# -----------------------------------------------------------------------------
st.title("🕹️ Interactive DFA Visualizer Suite")
st.markdown("""
    <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <strong>Student:</strong> Pham Minh Thu &nbsp;&nbsp; | &nbsp;&nbsp; 
        <strong>Institution:</strong> Vietnamese-German University (VGU) &nbsp;&nbsp; | &nbsp;&nbsp;
        <strong>Course:</strong> Automata Theory & Formal Languages
    </div>
    <br>
    """, unsafe_allow_html=True)

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
    st.header("DFA Minimization (Table-Filling Algorithm)")
    
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.subheader("1. Input Specification")
        q_in = st.text_input("States Q:", "q0, q1, q2, q3, q4")
        sigma_in = st.text_input("Alphabet Σ:", "0, 1")
        q0_in = st.text_input("Start State q0:", "q0")
        f_in = st.text_input("Final States F:", "q4")
        delta_in = st.text_area("Transitions (src,sym:dst):", 
"q0,0:q1\nq0,1:q3\nq1,0:q2\nq1,1:q4\nq2,0:q1\nq2,1:q4\nq3,0:q2\nq3,1:q4\nq4,0:q4\nq4,1:q4", height=200)
        
        if st.button("🚀 Run Minimization Algorithm", type="primary", use_container_width=True):
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
        st.subheader("2. Execution Visualizer")
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
                if st.button("⬅️ Previous Step", use_container_width=True) and idx > 0:
                    st.session_state.min_step -= 1; st.rerun()
            with btn2:
                if st.button("Next Step ➡️", use_container_width=True) and idx < len(history)-1:
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
                    fig_orig = render_graph(orig['q'], orig['delta'], orig['q0'], orig['f'])
                    st.graphviz_chart(fig_orig)
                    # NEW: Export Button
                    st.download_button("📥 Download Original Graph", data=graphviz.Source(fig_orig.source).pipe(format='png'), file_name="original_dfa.png", mime="image/png")
            
            # Phase 2 & 3: Distinguishability Grid (Slide-style)
            if 'marked_pairs' in current_step:
                st.write("**Distinguishability Table (Marking Process):**")
                
                reachable = current_step.get('reachable', orig['q']) 
                if 'reachable' not in current_step:
                    reachable = history[0]['reachable'] 
                    
                all_pairs = get_all_pairs(reachable)
                marked_set = set(tuple(p) for p in current_step['marked_pairs'])
                
                display_pairs = []
                for p, q in all_pairs:
                    if (p, q) in marked_set or (q, p) in marked_set:
                        display_pairs.append(f"({p}, {q}) ✅")
                    else:
                        display_pairs.append(f"({p}, {q})")
                
                cols_count = 4
                while len(display_pairs) % cols_count != 0:
                    display_pairs.append("") 
                grid = np.array(display_pairs).reshape(-1, cols_count)
                
                empty_cols = [" " * i for i in range(1, cols_count + 1)]
                df_grid = pd.DataFrame(grid, columns=empty_cols)
                st.table(df_grid)
            
            # Phase 4: Final Reduced DFA
            if 'reduced_dfa' in current_step:
                r = current_step['reduced_dfa']
                
                st.write("**Equivalent State Partitions (Equivalence Classes):**")
                partition_cols = st.columns(len(r['states']))
                for i, combined_state in enumerate(r['states']):
                    pretty_name = "{" + combined_state.replace('_', ', ') + "}"
                    partition_cols[i].success(f"**Partition {i+1}**\n\n{pretty_name}")
                
                st.markdown("---")
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.write("**Minimized Transition Table:**")
                    st.table(render_transition_table(r['states'], orig['sigma'], r['transitions'], r['final_states']))
                with c2:
                    st.write("**Minimized DFA Graph:**")
                    fig_min = render_graph(r['states'], r['transitions'], r['start_state'], r['final_states'])
                    st.graphviz_chart(fig_min)
                    # NEW: Export Button
                    st.download_button("📥 Download Minimized Graph", data=graphviz.Source(fig_min.source).pipe(format='png'), file_name="minimized_dfa.png", mime="image/png")

# -----------------------------------------------------------------------------
# MODULE 2: DFA STRING SIMULATOR
# -----------------------------------------------------------------------------
elif module == "DFA String Simulator":
    st.header("DFA Execution Trace Simulator")
    
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.subheader("1. Simulator Configuration")
        q_in = st.text_input("States Q:", "q0, q1, q2, q3, q4")
        sigma_in = st.text_input("Alphabet Σ:", "0, 1")
        q0_in = st.text_input("Start State q0:", "q0")
        f_in = st.text_input("Final States F:", "q4")
        delta_in = st.text_area("Transitions:", "q0,0:q1\nq0,1:q3\nq1,0:q2\nq1,1:q4\nq2,0:q1\nq2,1:q4\nq3,0:q2\nq3,1:q4\nq4,0:q4\nq4,1:q4")
        
        # NEW: Random String Generator
        c_input, c_btn = st.columns([2, 1])
        with c_input:
            test_word = st.text_input("Input String to Process:", st.session_state.rand_word)
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎲 Random", use_container_width=True):
                alph_list = [a.strip() for a in sigma_in.split(",")]
                if not alph_list or alph_list == [""]: alph_list = ["0", "1"]
                st.session_state.rand_word = "".join(random.choices(alph_list, k=random.randint(3, 7)))
                st.rerun()
        
        if st.button("🏁 Initialize Simulator", type="primary", use_container_width=True):
            delta = parse_transitions(delta_in)
            curr_state = q0_in.strip()
            trace_log = [{"char": "START", "state": curr_state}]
            
            for char in test_word:
                curr_state = delta.get((curr_state, char), "REJECT/TRAP")
                trace_log.append({"char": char, "state": curr_state})
                
            st.session_state.sim_trace = trace_log
            st.session_state.sim_step = 0
            
            finals_list = [i.strip() for i in f_in.split(",")]
            st.session_state.sim_dfa = {
                "q": [s.strip() for s in q_in.split(",")], "d": delta, 
                "q0": q0_in.strip(), "f": finals_list
            }
            
            # NEW: Save to Test History
            final_res = "ACCEPTED ✅" if curr_state in finals_list else "REJECTED ❌"
            st.session_state.sim_history.insert(0, {"Input String": test_word, "Final State": curr_state, "Result": final_res})
            st.rerun()

    with right_col:
        st.subheader("2. Step-by-Step Visualization")
        if not st.session_state.sim_trace:
            st.warning("Please configure the DFA and click 'Initialize Simulator'.")
        else:
            trace = st.session_state.sim_trace
            step_idx = st.session_state.sim_step
            dfa_context = st.session_state.sim_dfa
            
            c1, c2, c3 = st.columns([1,1,2])
            with c1:
                if st.button("⬅️ Step Back", use_container_width=True) and step_idx > 0:
                    st.session_state.sim_step -= 1; st.rerun()
            with c2:
                if st.button("Step Forward ➡️", use_container_width=True) and step_idx < len(trace)-1:
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
            
            # NEW: Display Test History
            if st.session_state.sim_history:
                st.markdown("---")
                st.write("📜 **Recent Test History**")
                st.dataframe(pd.DataFrame(st.session_state.sim_history).head(5), use_container_width=True)