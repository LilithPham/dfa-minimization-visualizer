# 🕹️ Interactive DFA Visualizer Suite

**Automata Theory & Formal Languages - Midterm Project** **Institution:** Vietnamese-German University (VGU)  
**Student:** Pham Minh Thu  

---

## 📖 Project Overview
This project is an interactive web application designed to visualize and simulate Deterministic Finite Automata (DFA). Built with Python and Streamlit, it serves as an educational tool to demonstrate the step-by-step execution of the **Table-Filling (Marking) Algorithm** for DFA Minimization, as well as providing a real-time **String Execution Simulator**.

## ✨ Core Features

### 1. Minimization Engine (Table-Filling Algorithm)
* **Reachability Analysis:** Automatically detects and removes inaccessible states using Breadth-First Search (BFS).
* **Step-by-Step Visualization:** Breaks down the marking process into logical phases, allowing users to navigate forward and backward.
* **Distinguishability Grid:** Displays the marking table exactly as taught in academic lectures, clearly distinguishing between marked and equivalent pairs.
* **Equivalence Class Partitioning:** Groups indistinguishable states and outputs the final mathematical partitions.
* **Dynamic Graph Rendering:** Generates and displays both the Original DFA and the final Minimal DFA side-by-side for easy comparison using Graphviz.

### 2. Step-by-Step String Simulator
* **Real-time Tracing:** Simulates the execution of a given string through the defined DFA.
* **Visual Highlighting:** Dynamically highlights the active state node in green on the Graphviz graph as each character is processed.
* **Acceptance Evaluation:** Determines and clearly outputs whether the final state is an accepting state or a rejecting state.

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

### Local Execution
1. Clone this repository:
   ```bash
   git clone [https://github.com/LilithPham/dfa-minimization-visualizer.git](https://github.com/LilithPham/dfa-minimization-visualizer.git)
   cd dfa-minimization-visualizer
2. Create and activate a virtual environment:
   ```bash
python -m venv venv
 //On Windows:
.\venv\Scripts\activate
 //On Mac/Linux:
source venv/bin/activate
3. Install required Python packages:
    ```bash
pip install streamlit graphviz pandas numpy
4.Launch the application:
    ```bash
streamlit run app.py
### 📁 Project Structure
app.py: The main Streamlit frontend application handling UI, state management, and graph rendering.

dfa_logic.py: The backend logic containing the DFAMinimizer class that executes the discrete mathematics algorithms.

README.md: Project documentation.

.gitignore: Git configuration to ignore virtual environments and cache files.

Developed for the CS Midterm Project - 2026
