import streamlit as st
import plotly.graph_objects as go
from .base import DashboardModule

from core.polynomial import Polynomial
from core.science_mode import U
from core.collatz_lab import CollatzLab
from core.galois import GaloisField

class ComparatorModule(DashboardModule):
    @property
    def id(self) -> str: return "galois_comparator"

    @property
    def display_name(self) -> str: return "Galois vs. Collatz Comparator"

    def render_sidebar(self):
        st.sidebar.markdown("### Dual-Engine Parameters")
        
        # We stick to P=127 for the perfect demo, or allow adjustment
        p_val = st.sidebar.number_input("Field Exponent (P)", value=127, min_value=3)
        
        st.sidebar.caption(f"Comparing Z[x] vs GF(2^{p_val})")
        st.sidebar.caption("Modulus: x^P + x + 1")

        if st.sidebar.button("Inject Dual Stream", type="primary"):
            self._initialize(p_val)
            
        st.sidebar.markdown("---")
        if st.sidebar.button("Run Comparison (50 Steps)"):
            self._run_batch(50)

    def _initialize(self, p):
        # 1. Create the Ideal Universe (Galois Field)
        # Modulus P(x) = x^p + x + 1
        mod_coeffs = [U(0)] * (p + 1)
        mod_coeffs[p] = U(1) # x^p
        mod_coeffs[1] = U(1) # x
        mod_coeffs[0] = U(1) # 1
        
        # Initialize Field Engine
        # Note: We use p=2 (Binary)
        GF = GaloisField(p=U(2), n=p, mod_poly_coeffs=mod_coeffs)
        
        # Initial State: Mersenne Number (All 1s)
        initial_coeffs = [U(1)] * p
        
        # State A: Collatz (Infinite Z)
        poly_collatz = Polynomial(initial_coeffs)
        
        # State B: Galois (Finite GF(2^p))
        # Use the factory to create the element
        poly_galois = GF(initial_coeffs)
        
        # Save to State
        self.set_state('p', p)
        self.set_state('gf_engine', GF)
        self.set_state('collatz_poly', poly_collatz)
        self.set_state('galois_poly', poly_galois)
        self.set_state('history_collatz', [])
        self.set_state('history_galois', [])
        self.set_state('history_diff', [])
        self.set_state('step', 0)
        st.rerun()

    def _run_batch(self, steps):
        c_poly = self.get_state('collatz_poly')
        g_poly = self.get_state('galois_poly')
        gf = self.get_state('gf_engine')
        
        if c_poly is None: return

        # Pre-compute the operator (x+1) for Galois
        # In GF(2), x+1 is just coefficients [1, 1]
        op_poly = gf([U(1), U(1)])
        one_poly = gf([U(1)])

        for _ in range(steps):
            # --- 1. Record State ---
            # Get raw bits (0 or 1)
            c_bits = [c.mass % 2 for c in c_poly.coeffs] # View as bits for comparison
            g_bits = [c.mass for c in g_poly.coeffs]     # Already bits in GF(2)
            
            # Align lengths for difference map
            max_len = max(len(c_bits), len(g_bits))
            c_padded = c_bits + [0]*(max_len - len(c_bits))
            g_padded = g_bits + [0]*(max_len - len(g_bits))
            
            # Compute XOR Difference (Hamming Error)
            diff = [c ^ g for c, g in zip(c_padded, g_padded)]
            
            self.get_state('history_collatz').append(c_padded)
            self.get_state('history_galois').append(g_padded)
            self.get_state('history_diff').append(diff)
            
            # --- 2. Step Collatz (The Physics) ---
            # We use the raw "Ascent" map here to compare apples-to-apples with LFSR
            # Map: P -> (x+1)P + 1
            # Note: We must Normalize to get the "bits" correctly for the next step 
            # or the comparison diverges due to coefficients > 1.
            # For this experiment, we run the FULL Collatz Step (Normalize -> Map)
            
            # Normalize first to resolve pressure
            relaxed_c, _ = CollatzLab.normalize_and_measure(c_poly)
            
            # Apply Map (x+1)*P + 1
            # We enforce "Ascent" logic to test the growth. 
            # (If we let it descend, it just shifts, which is boring).
            # We want to see the "Friction" of growth.
            x_plus_1 = Polynomial([U(1), U(1)])
            c_poly = (relaxed_c * x_plus_1) + Polynomial([U(1)])

            # --- 3. Step Galois (The Ideal) ---
            # Map: G -> G * (x+1) + 1
            # galois.py handles the modulus automatically
            g_poly = (g_poly * op_poly) + one_poly
            
        self.set_state('collatz_poly', c_poly)
        self.set_state('galois_poly', g_poly)
        self.set_state('step', self.get_state('step') + steps)

    def render_main(self):
        if not self.get_state('history_collatz'):
            st.info("Inject Dual Stream to Begin.")
            return

        def plot_spectrogram(data, title, color_scale='Viridis'):
            z_data = list(map(list, zip(*data))) # Transpose
            fig = go.Figure(data=go.Heatmap(z=z_data, colorscale=color_scale, showscale=False))
            fig.update_layout(
                title=title, height=250, margin=dict(l=0, r=0, t=30, b=0),
                paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)

        # 1. Collatz (Real)
        plot_spectrogram(self.get_state('history_collatz'), "A. Physical Universe (Collatz Dynamics)")
        
        # 2. Galois (Ideal)
        plot_spectrogram(self.get_state('history_galois'), "B. Ideal Universe (Galois LFSR)", color_scale='Blues')
        
        # 3. Difference (The Ghost)
        st.markdown("### C. The Error Map (A XOR B)")
        st.caption("This visualizes the 'Leakage' of arithmetic energy.")
        plot_spectrogram(self.get_state('history_diff'), "", color_scale='Hot')