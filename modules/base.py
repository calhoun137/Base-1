# dashboard/modules/base.py
from abc import ABC, abstractmethod
import streamlit as st

class DashboardModule(ABC):
    """
    The 'Cartridge' Protocol.
    Every mathematical tool must inherit from this class.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique internal ID (e.g., 'collatz_lab') used for session state keys."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """The name that appears in the Sidebar menu."""
        pass

    @abstractmethod
    def render_sidebar(self):
        """
        Draws the module's specific controls in the sidebar.
        Use st.sidebar.slider, st.sidebar.button, etc.
        """
        pass

    @abstractmethod
    def render_main(self):
        """
        Draws the visualization and telemetry in the main area.
        """
        pass

    def get_state(self, key: str, default_value=None):
        """Helper to manage module-specific state safely."""
        full_key = f"{self.id}_{key}"
        if full_key not in st.session_state:
            st.session_state[full_key] = default_value
        return st.session_state[full_key]

    def set_state(self, key: str, value):
        """Helper to set module-specific state."""
        full_key = f"{self.id}_{key}"
        st.session_state[full_key] = value