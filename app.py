# dashboard/app.py
import streamlit as st
import os

# 1. Page Configuration (MUST be the first Streamlit command)
st.set_page_config(
    page_title="Base-1 Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Load CSS Style
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Path to style.css (assuming it's in the same folder as app.py)
css_path = os.path.join(os.path.dirname(__file__), 'style.css')
if os.path.exists(css_path):
    load_css(css_path)

from modules.collatz import CollatzModule
from modules.comparator import ComparatorModule
from modules.mixing import MixingLab
from modules.zeta import ZetaModule  # <--- NEW IMPORT

AVAILABLE_MODULES = [
    CollatzModule(),
    ComparatorModule(),
    MixingLab(),
    ZetaModule()  # <--- NEW CARTRIDGE
]

# 4. The Sidebar (The Rack)
st.sidebar.title("BASE-1 // CONSOLE")
st.sidebar.markdown("---")

if not AVAILABLE_MODULES:
    st.sidebar.warning("No Cartridges Found.")
    st.sidebar.info("Please implement a module in 'dashboard/modules/'")
    selected_module = None
else:
    # distinct names for the dropdown
    module_names = [m.display_name for m in AVAILABLE_MODULES]
    choice = st.sidebar.selectbox("Select Module", module_names)
    
    # Find the selected module object
    selected_module = next(m for m in AVAILABLE_MODULES if m.display_name == choice)

# 5. The Main Loop
if selected_module:
    # A. Render Module Controls
    st.sidebar.markdown(f"### // {selected_module.display_name}")
    selected_module.render_sidebar()
    
    # B. Render Main Stage
    selected_module.render_main()
else:
    # Zero State (Welcome Screen)
    st.title("System Standby")
    st.markdown("""
    ### Welcome to the Base-1 Mathematical Console.
    
    The system is currently in **Idle Mode**.
    
    **Status:**
    * Physics Engine: `Ready`
    * Visualization Core: `Online`
    * Modules Loaded: `4`
    
    *Inject a cartridge to begin experimentation.*
    """)