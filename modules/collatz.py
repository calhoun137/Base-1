import streamlit as st
import plotly.graph_objects as go
import numpy as np
from scipy import stats
import time  # <--- Required for the animation speed

from .base import DashboardModule
from core.collatz_lab import CollatzLab
from core.science_mode import U
from core.polynomial import Polynomial

class CollatzModule(DashboardModule):
    @property
    def id(self) -> str: return "collatz_lab"

    @property
    def display_name(self) -> str: return "Collatz Resonance Lab"

    def render_sidebar(self):
        # --- 1. INJECTION DECK (Setup) ---
        st.sidebar.markdown("### 1. Matter Injection")
        
        tab1, tab2 = st.sidebar.tabs(["Standard", "Mersenne"])
        
        with tab1:
            start_n = st.number_input("Integer N", min_value=1, value=27, step=1)
            if st.button("Inject Integer", type="primary", use_container_width=True):
                self._inject_matter(CollatzLab.inject(start_n), mode="standard")
                
        with tab2:
            p_val = st.number_input("Exponent P (2^P - 1)", min_value=3, value=127, step=1)
            st.caption(f"Magnitude: ~10^{int(p_val * 0.301)}")
            
            if st.button("Inject Mersenne", type="primary", use_container_width=True):
                coeffs = [U(1) for _ in range(p_val)]
                self._inject_matter(Polynomial(coeffs), mode="mersenne")

        st.sidebar.markdown("---")

        # --- 2. FLIGHT CONTROL DECK (Playback) ---
        st.sidebar.markdown("### 2. Flight Control")
        
        # State Check
        is_running = self.get_state('is_running', False)
        
        # Play/Pause Toggle
        # We use columns to center the big play button
        col_play, col_stop = st.sidebar.columns(2)
        with col_play:
            if not is_running:
                if st.button("▶️ RUN", type="primary", use_container_width=True):
                    self.set_state('is_running', True)
                    st.rerun()
            else:
                if st.button("⏸ PAUSE", use_container_width=True):
                    self.set_state('is_running', False)
                    st.rerun()
        
        # Manual Overrides (Only active if paused)
        with col_stop:
             if st.button("Step >", disabled=is_running, use_container_width=True):
                 self.run_step()

        # Speed Control
        delay = st.sidebar.slider("Time Dilation (Delay)", 0.0, 0.5, 0.05, format="%.2fs")
        
        # Special Actions
        with st.sidebar.expander("Advanced Operations"):
            if st.button("Burst (10 Steps)", use_container_width=True):
                for _ in range(10): 
                    if not self.run_step(): break
            
            if st.button("Run to Meltdown", use_container_width=True):
                 with st.spinner("Accelerating..."):
                     for _ in range(2000):
                         if not self.run_step(): break
                         if self.get_state('history_solid_height')[-1] == 0: break
                 st.rerun()

        # --- 3. PHYSICS LOOP (The Engine) ---
        # This runs BEFORE the main render to update state for the current frame
        if is_running:
            # Physics Tick
            still_active = self.run_step()
            
            # Auto-Stop condition
            if not still_active:
                self.set_state('is_running', False)
                st.success("Trajectory Converged.")
            
            # Pacing
            time.sleep(delay)

    def _inject_matter(self, poly: Polynomial, mode="standard"):
        """Reset the lab with new matter."""
        self.set_state('poly', poly)
        self.set_state('step', 0)
        self.set_state('history_entropy', [])
        self.set_state('history_avalanche', [])
        self.set_state('history_val', [])
        self.set_state('spectrogram_data', [])
        self.set_state('history_solid_height', [])
        self.set_state('mode', mode)
        self.set_state('status', 'Ready')
        self.set_state('is_running', False) # Always pause on new inject
        st.rerun()

    def run_step(self):
        poly = self.get_state('poly')
        if poly is None: return False
        
        # Physics & Measurement
        entropy = CollatzLab.measure_entropy(poly)
        val = poly.evaluate(U(2)).mass
        relaxed_poly, energy = CollatzLab.normalize_and_measure(poly)
        
        # Structure Analysis
        raw_coeffs = [c.mass if hasattr(c, 'mass') else int(c) for c in relaxed_poly.coeffs]
        solid_h = 0
        for c in raw_coeffs:
            if c == 1: solid_h += 1
            else: break
        
        # Record Telemetry
        self.get_state('history_entropy').append(entropy)
        self.get_state('history_avalanche').append(energy)
        self.get_state('history_val').append(val)
        self.get_state('history_solid_height').append(solid_h)
        self.get_state('spectrogram_data').append(raw_coeffs)

        # Convergence Check
        if val <= 1:
            self.set_state('status', 'Converged')
            return False

        # Dynamics (Map)
        lsb = raw_coeffs[0]
        if lsb % 2 == 0:
            next_coeffs = relaxed_poly.coeffs[1:]
            if not next_coeffs: next_coeffs = [U(0)]
            next_poly = Polynomial(next_coeffs)
        else:
            x_plus_1 = Polynomial([U(1), U(1)]) 
            next_poly = (relaxed_poly * x_plus_1) + Polynomial([U(1)])
            
        self.set_state('poly', next_poly)
        self.set_state('step', self.get_state('step') + 1)
        return True

    def render_main(self):
        poly = self.get_state('poly')
        if poly is None:
            st.info("System Standby. Inject Matter to Initialize.")
            return

        # --- A. Telemetry Deck ---
        step = self.get_state('step')
        solid_h = self.get_state('history_solid_height')[-1] if self.get_state('history_solid_height') else 0
        
        # Calculate Slope
        burn_rate_text = "N/A"
        burn_color = "#9ca3af"
        hist_h = self.get_state('history_solid_height')
        if len(hist_h) > 10 and self.get_state('mode') == 'mersenne':
            x = np.arange(len(hist_h))
            y = np.array(hist_h)
            slope, intercept, _, _, _ = stats.linregress(x, y)
            burn_rate_text = f"{slope:.4f} bits/step"
            burn_color = "#ef4444" if slope < -0.2 else "#10b981"

        # Telemetry UI
        st.markdown(f"""
        <div style="display: flex; gap: 30px; margin-bottom: 20px; align-items: center;">
            <div>
                <div class="telemetry-label">Step Count</div>
                <div class="telemetry-value">{step}</div>
            </div>
            <div>
                <div class="telemetry-label">Solid Core Height</div>
                <div class="telemetry-value">{solid_h}</div>
            </div>
            <div>
                <div class="telemetry-label">Burn Velocity</div>
                <div class="telemetry-value" style="color: {burn_color}">{burn_rate_text}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- B. Visualization Crucible ---
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="telemetry-label">Resonance Spectrogram</div>', unsafe_allow_html=True)
            spec_data = self.get_state('spectrogram_data')
            if spec_data:
                # Transpose for visual layout (X=Time)
                max_len = max(len(row) for row in spec_data)
                padded = [row + [None]*(max_len - len(row)) for row in spec_data]
                z_data = list(map(list, zip(*padded)))
                
                fig = go.Figure(go.Heatmap(z=z_data, colorscale='Viridis', showscale=False))
                fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0), 
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="telemetry-label">Core Stability</div>', unsafe_allow_html=True)
            if hist_h:
                fig_decay = go.Figure()
                fig_decay.add_trace(go.Scatter(y=hist_h, mode='lines', line=dict(color='#06b6d4', width=2)))
                # Add Trendline if Mersenne
                if len(hist_h) > 10 and self.get_state('mode') == 'mersenne':
                     fig_decay.add_trace(go.Scatter(x=x, y=intercept + slope * x, mode='lines', line=dict(color='#ef4444', dash='dash')))
                
                fig_decay.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0), 
                                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.05)')
                st.plotly_chart(fig_decay, use_container_width=True)
                
            st.markdown('<div class="telemetry-label" style="margin-top: 20px;">Avalanche Seismograph</div>', unsafe_allow_html=True)
            hist_aval = self.get_state('history_avalanche')
            if hist_aval:
                fig_av = go.Figure(go.Scatter(y=hist_aval[-100:], mode='lines', fill='tozeroy', line=dict(color='#ef4444')))
                fig_av.update_layout(height=150, margin=dict(t=0, b=0, l=0, r=0), 
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.05)')
                st.plotly_chart(fig_av, use_container_width=True)

        # --- 4. ANIMATION TRIGGER ---
        # If we are running, we must tell Streamlit to restart the script 
        # immediately to render the NEXT frame.
        if self.get_state('is_running', False):
            st.rerun()