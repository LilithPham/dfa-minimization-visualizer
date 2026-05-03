# 🕹️ Interactive DFA Visualizer Suite

**Automata Theory & Formal Languages - Midterm Project** **Institution:** Vietnamese-German University (VGU)  
**Student:** Pham Minh Thu  

---

## 📖 Project Overview
This project is an interactive web application designed to visualize and simulate Deterministic Finite Automata (DFA). Built with Python and Streamlit, it serves as an educational tool to demonstrate the step-by-step execution of the **Table-Filling (Marking) Algorithm** for DFA Minimization, as well as providing a real-time **String Execution Simulator**.

## ✨ Core Features

### 1. DFA Minimizer (Table-Filling Algorithm)
* **Reachability Analysis:** Automatically filters out unreachable states.
* **Distinguishability Grid:** Dynamically generates the marking table exactly as taught in lectures, identifying distinguishable vs. equivalent state pairs.
* **Equivalence Class Partitioning:** Mathematically groups indistinguishable states into final partitions.
* **Minimal DFA Output:** Renders the optimized DFA side-by-side with its new transition table.

### 2. DFA String Execution Simulator
* **Interactive Traversal:** Simulates the execution of strings step-by-step.
* **Visual Tracing:** Dynamically highlights the active state node in **neon green**. Transitions falling outside the alphabet or state definitions are visually caught in a **red octagon trap state**.
* **Random Testing:** Built-in random string generator based on the defined alphabet $\Sigma$.
* **QA Test History:** Automatically logs recent execution results (Accepted/Rejected) into a test history board.

### 3. NFA to DFA Converter (Subset Construction)
* **$\lambda$-Transition Support:** Fully handles NFA with lambda (epsilon) transitions using precise $\lambda$-closure algorithms.
* **Non-Deterministic Inputs:** Allows inputting multiple destination states per symbol via comma-separated values in an interactive data grid.
* **Step-by-Step Visualization:** Traces the Powerset/Subset construction method phase-by-phase.
* **Graph Generation:** Automatically renders the mathematically equivalent DFA transition table and node graph.
## 🛠️ Technology Stack
* **Language:** Python 3.9+
* **Framework:** [Streamlit](https://streamlit.io/) (for interactive web UI)
* **Data Handling:** Pandas, NumPy
* **Graph Visualization:** [Graphviz](https://graphviz.org/)

## ⚙️ Installation & Setup

### Prerequisites
1. **Python:** Ensure Python is installed on your system.
2. **Graphviz Core:** You must install the Graphviz executable for your operating system to render graphs.
   * **Windows:** Download from the [official Graphviz site](https://graphviz.org/download/) or use `winget install graphviz`. Ensure it is added to your system PATH.
   * **macOS:** `brew install graphviz`
   * **Linux:** `sudo apt-get install graphviz`

## 📁 Project Structure
* **app.py**: The main Streamlit frontend application handling UI, state management, and graph rendering.

* **dfa_logic.py**: The backend logic containing the DFAMinimizer class that executes the discrete mathematics algorithms.

* **README.md**: Project documentation.

* **.gitignore**: Git configuration to ignore virtual environments and cache files.


### Local Execution
1. Clone this repository:
   ```bash
   git clone [https://github.com/LilithPham/dfa-minimization-visualizer.git](https://github.com/LilithPham/dfa-minimization-visualizer.git)
   cd dfa-minimization-visualizer

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv 
   .\venv\Scripts\activate

3. Install required Python packages:
   ```bash
   pip install streamlit graphviz pandas numpy

4.Launch the application:
   ```bash
  streamlit run app.py

### ☁️ Cloud Deployment
This application is fully compatible with Streamlit Community Cloud. It utilizes requirements.txt for Python dependencies and packages.txt for the underlying Linux Graphviz core, ensuring seamless zero-config deployment.

Developed for the CS Midterm Project - 2026