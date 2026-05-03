import streamlit as st
import graphviz
import pandas as pd
import numpy as np
import random
from dfa_logic import DFAMinimizer, NFAToDFAConverter

# -----------------------------------------------------------------------------
# GLOBAL CONFIGURATION & SESSION PERSISTENCE
# -----------------------------------------------------------------------------
st.set_page_config(page_title="DFA Visualizer Suite - VGU", layout="wide")

# Session States for Data Grids
for key in ['dfa_table', 'sim_table', 'nfa_table']:
    if key not in st.session_state: st.session_state[key] = None

if 'min_step' not in st.session_state: st.session_state.min_step = 0
if 'min_history' not in st.session_state: st.session_state.min_history = []
if 'original_dfa' not in st.session_state: st.session_state.original_dfa = None

if 'sim_step' not in st.session_state: st.session_state.sim_step = 0
if 'sim_trace' not in st.session_state: st.session_state.sim_trace = []
if 'sim_dfa' not in st.session_state: st.session_state.sim_dfa = None
if 'sim_history' not in st.session_state: st.session_state.sim_history = [] 
if 'rand_word' not in st.session_state: st.session_state.rand_word = "01001" 

if 'nfa_history' not in st.session_state: st.session_state.nfa_history = []
if 'nfa_step' not in st.session_state: st.session_state.nfa_step = 0
if 'original_nfa' not in st.session_state: st.session_state.original_nfa = None

# -----------------------------------------------------------------------------
# UTILITY & RENDERING FUNCTIONS
# -----------------------------------------------------------------------------
def init_table(alphabet, default_states):
    """Khởi tạo bảng dữ liệu với các cột tương ứng theo Alphabet"""
    df = pd.DataFrame(index=range(len(default_states)), columns=["State"] + alphabet)
    df["State"] = default_states
    return df.fillna("")

def render_graph(states, transitions, start, finals, active_node=None):
    """Generates a DOT graph representation of the DFA/NFA."""
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
        # Xử lý chung cho cả DFA (chuỗi) và NFA (list)
        dst_list = dst if isinstance(dst, list) else [dst]
        for d in dst_list:
            key = (src, d)
            if key not in edge_dict: edge_dict[key] = []
            edge_dict[key].append(symbol)
        
    for (src, dst), symbols in edge_dict.items():
        dot.edge(src, dst, label=', '.join(symbols))
        
    return dot

def render_transition_table(states, alphabet, delta, finals):
    df = pd.DataFrame(index=states, columns=alphabet)
    for s in states:
        for a in alphabet:
            df.at[s, a] = delta.get((s, a), "-")
    df.index = [f"*{s} (Final)" if s in finals else s for s in states]
    return df

def get_all_pairs(states):
    pairs = []
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            pairs.append((states[i], states[j]))
    return pairs

# -----------------------------------------------------------------------------
# HEADER & BRANDING
# -----------------------------------------------------------------------------
st.title("🕹️ Interactive Automata Visualizer Suite")
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
module = st.sidebar.radio("Navigation Menu:", ["DFA Minimizer", "DFA String Simulator", "NFA to DFA Converter"])
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 CS Midterm Project")

# -----------------------------------------------------------------------------
# CORE LOGIC: UNIFIED UI FOR ALL MODULES
# -----------------------------------------------------------------------------
if module == "DFA Minimizer":
    st_key, m_type = "dfa_table", "DFA"
    title = "DFA Minimization (Table-Filling Algorithm)"
elif module == "DFA String Simulator":
    st_key, m_type = "sim_table", "DFA"
    title = "DFA Execution Trace Simulator"
else:
    st_key, m_type = "nfa_table", "NFA"
    title = "NFA to DFA (Subset Construction)"

st.header(title)
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("1. Configuration Table")
    st.info("💡 Edit cells directly. Click ➕ below the table to add new states.")
    
    # 1. Alphabet Input
    default_alpha = "0, 1" if m_type == "DFA" else "a, b, e"
    sigma_in = st.text_input("Alphabet Σ (comma separated, use 'e' for epsilon):", default_alpha)
    alphabet = [x.strip() for x in sigma_in.split(",") if x.strip()]
    
    # 2. Init Table if empty or alphabet changed
    if st.session_state[st_key] is None or list(st.session_state[st_key].columns[1:]) != alphabet:
        st.session_state[st_key] = init_table(alphabet, ["q0", "q1", "q2", "q3", "q4"])

    # 3. Interactive Data Grid
    edited_df = st.data_editor(
        st.session_state[st_key], 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True, 
        key=f"editor_{st_key}"
    )
    
    # 4. Start & Final States
    c1, c2 = st.columns(2)
    with c1: 
        q0_in = st.text_input("Start State:", "q0")
    with c2: 
        f_in = st.text_input("Final States F:", "q4" if m_type == "DFA" else "q2")
    
    # 5. Extra feature for Simulator
    test_word = ""
    if module == "DFA String Simulator":
        c_input, c_btn = st.columns([2, 1])
        with c_input:
            test_word = st.text_input("Input String to Process:", st.session_state.rand_word)
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎲 Random", use_container_width=True):
                alph_list = alphabet if alphabet else ["0", "1"]
                st.session_state.rand_word = "".join(random.choices(alph_list, k=random.randint(3, 7)))
                st.rerun()

    # 6. Execute Button
    btn_label = "🚀 Run Algorithm" if module == "DFA Minimizer" else "🏁 Initialize Simulator" if module == "DFA String Simulator" else "⚙️ Convert to DFA"
    if st.button(btn_label, type="primary", use_container_width=True):
        # Data Parsing Logic
        delta = {}
        states = []
        for _, row in edited_df.iterrows():
            src = str(row["State"]).strip()
            if not src or src == "nan": continue
            states.append(src)
            for sym in alphabet:
                val = str(row.get(sym, "")).strip()
                if val and val != "nan":
                    if m_type == "NFA":
                        delta[(src, sym)] = [d.strip() for d in val.split(",") if d.strip()]
                    else:
                        delta[(src, sym)] = val.split(",")[0].strip() # Đảm bảo DFA chỉ có 1 đích đến
        
        start = q0_in.strip()
        finals = [i.strip() for i in f_in.split(",")]

        # Module Execution
        if module == "DFA Minimizer":
            st.session_state.original_dfa = {"q": states, "sigma": alphabet, "delta": delta, "q0": start, "f": finals}
            engine = DFAMinimizer(states, alphabet, delta, start, finals)
            st.session_state.min_history = engine.run()
            st.session_state.min_step = 0
            
        elif module == "DFA String Simulator":
            curr = start
            trace = [{"char": "START", "state": curr}]
            for char in test_word:
                curr = delta.get((curr, char), "REJECT/TRAP")
                trace.append({"char": char, "state": curr})
                
            st.session_state.sim_trace = trace
            st.session_state.sim_step = 0
            st.session_state.sim_dfa = {"q": states, "d": delta, "q0": start, "f": finals}
            
            final_res = "ACCEPTED ✅" if curr in finals else "REJECTED ❌"
            st.session_state.sim_history.insert(0, {"Input String": test_word, "Final State": curr, "Result": final_res})
            
        elif module == "NFA to DFA Converter":
            converter = NFAToDFAConverter(states, alphabet, delta, start, finals)
            st.session_state.nfa_history = converter.run()
            st.session_state.nfa_step = 0
            
        st.rerun()

# -----------------------------------------------------------------------------
# RIGHT COLUMN VISUALIZATION
# -----------------------------------------------------------------------------
with right_col:
    st.subheader("2. Visualization")

    # ----- RENDER MODULE 1: MINIMIZER -----
    if module == "DFA Minimizer":
        if not st.session_state.min_history:
            st.warning("Awaiting DFA configuration. Please run the algorithm on the left.")
        else:
            history = st.session_state.min_history
            idx = st.session_state.min_step
            current_step = history[idx]
            orig = st.session_state.original_dfa
            
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

            if idx == 0:
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.write("**Transition Table:**")
                    st.table(render_transition_table(orig['q'], orig['sigma'], orig['delta'], orig['f']))
                with c2:
                    st.write("**State Transition Graph:**")
                    fig_orig = render_graph(orig['q'], orig['delta'], orig['q0'], orig['f'])
                    st.graphviz_chart(fig_orig)
                    st.download_button("📥 Download Original Graph", data=graphviz.Source(fig_orig.source).pipe(format='png'), file_name="original_dfa.png", mime="image/png")
            
            if 'marked_pairs' in current_step:
                st.write("**Distinguishability Table (Marking Process):**")
                reachable = current_step.get('reachable', orig['q']) 
                if 'reachable' not in current_step: reachable = history[0]['reachable'] 
                all_pairs = get_all_pairs(reachable)
                marked_set = set(tuple(p) for p in current_step['marked_pairs'])
                
                display_pairs = []
                for p, q in all_pairs:
                    if (p, q) in marked_set or (q, p) in marked_set:
                        display_pairs.append(f"({p}, {q}) ✅")
                    else:
                        display_pairs.append(f"({p}, {q})")
                
                cols_count = 4
                while len(display_pairs) % cols_count != 0: display_pairs.append("") 
                grid = np.array(display_pairs).reshape(-1, cols_count)
                empty_cols = [" " * i for i in range(1, cols_count + 1)]
                st.table(pd.DataFrame(grid, columns=empty_cols))
            
            if 'reduced_dfa' in current_step:
                r = current_step['reduced_dfa']
                st.write("**Equivalent State Partitions:**")
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
                    st.download_button("📥 Download Minimized Graph", data=graphviz.Source(fig_min.source).pipe(format='png'), file_name="minimized_dfa.png", mime="image/png")

    # ----- RENDER MODULE 2: SIMULATOR -----
    elif module == "DFA String Simulator":
        if not st.session_state.sim_trace:
            st.warning("Awaiting DFA configuration and execution...")
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
            
            if st.session_state.sim_history:
                st.markdown("---")
                st.write("📜 **Recent Test History**")
                st.dataframe(pd.DataFrame(st.session_state.sim_history).head(5), use_container_width=True)

    # ----- RENDER MODULE 3: NFA CONVERTER -----
    elif module == "NFA to DFA Converter":
        if not st.session_state.nfa_history:
            st.warning("Awaiting NFA configuration and execution...")
        else:
            history = st.session_state.nfa_history
            idx = st.session_state.nfa_step
            current_step = history[idx]
            
            btn1, btn2, progress_col = st.columns([1,1,2])
            with btn1:
                if st.button("⬅️ Previous Step", use_container_width=True) and idx > 0:
                    st.session_state.nfa_step -= 1; st.rerun()
            with btn2:
                if st.button("Next Step ➡️", use_container_width=True) and idx < len(history)-1:
                    st.session_state.nfa_step += 1; st.rerun()
            with progress_col:
                st.progress((idx + 1) / len(history), f"Phase {idx+1} of {len(history)}")

            st.markdown("---")
            st.subheader(current_step['step_name'])
            st.success(current_step['description'])

            if 'converted_dfa' in current_step:
                dfa = current_step['converted_dfa']
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.write("**Converted DFA Transition Table:**")
                    st.table(render_transition_table(dfa['q'], dfa['sigma'], dfa['delta'], dfa['f']))
                with c2:
                    st.write("**Converted DFA Graph:**")
                    fig_dfa = render_graph(dfa['q'], dfa['delta'], dfa['q0'], dfa['f'])
                    st.graphviz_chart(fig_dfa)
                    st.download_button("📥 Download Result DFA", data=graphviz.Source(fig_dfa.source).pipe(format='png'), file_name="subset_dfa.png", mime="image/png")