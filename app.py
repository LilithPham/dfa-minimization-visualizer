import streamlit as st
import graphviz
from dfa_logic import DFAMinimizer
import pandas as pd

# Cấu hình trang web
st.set_page_config(page_title="DFA Minimizer", layout="wide")
st.title("🕹️ Ứng dụng Trực quan hóa: DFA Minimization")
st.markdown("---")

# Khởi tạo bộ nhớ tạm (Session State) để lưu số bước hiện tại
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'history' not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns([1, 2]) # Cột 1 nhỏ, Cột 2 to

with col1:
    st.header("⚙️ 1. Dữ liệu Đầu vào")
    st.info("Dữ liệu mặc định được lấy từ Ví dụ Slide 55 của bài giảng.")
    
    # Form nhập liệu
    states_input = st.text_input("Tập trạng thái Q (cách nhau bởi dấu phẩy):", "q0, q1, q2, q3, q4, q5")
    alphabet_input = st.text_input("Bảng chữ cái Sigma (Σ):", "0, 1")
    start_state = st.text_input("Trạng thái bắt đầu (Start State):", "q0")
    final_states_input = st.text_input("Tập trạng thái đích F:", "q3, q4")
    
    st.write("**Luật chuyển (Transitions)**")
    st.caption("Định dạng: Trạng thái hiện tại , Ký tự : Trạng thái tiếp theo")
    transitions_input = st.text_area("Mỗi luật 1 dòng:", 
"""q0,0:q1
q0,1:q2
q1,0:q2
q1,1:q3
q2,0:q2
q2,1:q4
q3,0:q3
q3,1:q3
q4,0:q4
q4,1:q4
q5,0:q5
q5,1:q4""")
    
    if st.button("🚀 Bắt đầu Chạy Thuật Toán", type="primary"):
        # Xử lý chuỗi nhập vào thành List/Dict cho Python hiểu
        states = [s.strip() for s in states_input.split(",")]
        alphabet = [a.strip() for a in alphabet_input.split(",")]
        final_states = [f.strip() for f in final_states_input.split(",")]
        
        transitions = {}
        for line in transitions_input.strip().split('\n'):
            if line:
                parts = line.split(':')
                left = parts[0].split(',')
                transitions[(left[0].strip(), left[1].strip())] = parts[1].strip()
                
        # Gọi "Bộ não" DFA Logic
        minimizer = DFAMinimizer(states, alphabet, transitions, start_state.strip(), final_states)
        st.session_state.history = minimizer.run()
        st.session_state.step = 0 # Reset về bước đầu tiên
        st.rerun() # Tải lại trang web để hiện kết quả

with col2:
    st.header("📺 2. Trực quan hóa Thuật toán")
    
    if not st.session_state.history:
        st.warning("👈 Hãy kiểm tra dữ liệu bên trái và bấm 'Bắt đầu Chạy Thuật Toán'!")
    else:
        history = st.session_state.history
        current_step = st.session_state.step
        step_data = history[current_step]
        
        # Thanh điều hướng bước (Next/Prev)
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("⬅️ Bước trước") and st.session_state.step > 0:
                st.session_state.step -= 1
                st.rerun()
        with c2:
            if st.button("Bước tiếp ➡️") and st.session_state.step < len(history) - 1:
                st.session_state.step += 1
                st.rerun()
        with c3:
            st.progress((current_step + 1) / len(history), text=f"Tiến độ: Bước {current_step + 1} / {len(history)}")
        
        st.markdown("---")
        
        # Hiển thị nội dung của bước hiện tại
        st.subheader(step_data['step_name'])
        st.success(step_data['description'])
        
        # Nếu đang ở các bước Kẻ bảng mark()
        if 'marked_pairs' in step_data:
            st.write("🎯 **Danh sách các cặp đã bị đánh dấu (X) [Distinguishable]:**")
            # Trình bày cho đẹp mắt
            df = pd.DataFrame(step_data['marked_pairs'], columns=["Node 1", "Node 2"])
            st.dataframe(df, use_container_width=True)
            
        # Nếu ở bước cuối cùng: Vẽ Đồ thị DFA thu gọn
        if 'equivalent_pairs' in step_data:
            st.write("✨ **Danh sách các cặp giống nhau (Indistinguishable) để gộp:**")
            st.code(step_data['equivalent_pairs'])
            
            st.write("🎨 **Đồ thị DFA sau khi thu gọn:**")
            try:
                # Dùng Graphviz để vẽ đồ thị tự động
                dot = graphviz.Digraph()
                dot.attr(rankdir='LR')
                dot.node('start', shape='none', label='')
                
                # Đây là demo vẽ tượng trưng (Em có thể nâng cấp thêm sau)
                dot.node('q0', shape='circle')
                dot.node('q1', shape='circle')
                dot.node('q2_q4', shape='doublecircle') # Gộp node
                dot.node('q3', shape='doublecircle')
                
                dot.edge('start', 'q0')
                dot.edge('q0', 'q1', label='0')
                dot.edge('q1', 'q2_q4', label='1')
                dot.edge('q0', 'q2_q4', label='1')
                
                st.graphviz_chart(dot)
            except Exception as e:
                st.error("Chưa cài đặt Graphviz core trên máy tính. Bạn có thể cài sau để hiện đồ thị nhé!")