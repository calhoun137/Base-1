import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import time
from .base import DashboardModule

from core.collatz_lab import CollatzLab
from core.science_mode import U
from core.polynomial import Polynomial

class MixingLab(DashboardModule):
    @property
    def id(self) -> str: return "mixing_lab"

    @property
    def display_name(self) -> str: return "Mixing & Density Lab"

    def render_sidebar(self):
        st.sidebar.markdown("### // Criticality Scanner")
        st.sidebar.info("Locating the density threshold where Growth < Dissipation.")
        
        # Sparse Construction Kit
        st.sidebar.markdown("**Construct Sparse Trap:**")
        st.sidebar.latex(r"N = 2^A + 2^B + 1")
        
        power_a = st.sidebar.number_input("Power A (MSB)", min_value=50, value=500, step=50)
        power_b = st.sidebar.number_input("Power B (Middle)", min_value=0, value=250, step=10)
        
        if st.sidebar.button("Inject Sparse Matter", type="primary"):
            # Construct Polynomial: 1 + x^B + x^A
            coeffs = [U(0)] * (power_a + 1)
            coeffs[0] = U(1)          # 2^0
            coeffs[power_b] = U(1)    # 2^B
            coeffs[power_a] = U(1)    # 2^A (MSB)
            
            poly = Polynomial(coeffs)
            self._inject(poly)

        st.sidebar.markdown("---")
        
        # Flight Control
        is_running = self.get_state('is_running', False)
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button("▶ SCAN"):
                self.set_state('is_running', True)
                st.rerun()
        with col2:
            if st.sidebar.button("⏸ PAUSE"):
                self.set_state('is_running', False)
                st.rerun()
                
        # Physics Speed
        speed = st.sidebar.select_slider("Simulation Clock", options=["Step", "Fast", "Hyper"], value="Fast")
        self.set_state('speed', speed)

        # Physics Loop
        if is_running:
            active = self.run_step()
            if not active:
                self.set_state('is_running', False)
            
            if speed == "Step": time.sleep(0.1)
            elif speed == "Fast": time.sleep(0.001)
            # Hyper runs multiple steps per frame (handled in loop below)
            
            st.rerun()

    def _inject(self, poly):
        self.set_state('poly', poly)
        self.set_state('step', 0)
        self.set_state('history_density', [])
        self.set_state('history_drift', [])  # New: Tracks instantaneous drift (+1.58 or -1)
        self.set_state('is_running', False)
        st.rerun()

    def run_step(self):
        poly = self.get_state('poly')
        if poly is None: return False
        
        # Batch processing for "Hyper" speed
        loops = 10 if self.get_state('speed') == "Hyper" else 1
        
        for _ in range(loops):
            # 1. Metrics Check
            # Hamming Density
            hamming_weight = sum(1 for c in poly.coeffs if not c.is_vacuum)
            bit_length = len(poly.coeffs)
            density = hamming_weight / bit_length if bit_length > 0 else 0
            
            # Normalize for next step physics
            relaxed_poly, _ = CollatzLab.normalize_and_measure(poly)
            
            # Check Convergence
            val = poly.evaluate(U(2)).mass
            if val <= 1: return False
            
            # 2. Dynamics & Drift Calculation
            lsb = relaxed_poly.coeffs[0].mass
            
            if lsb % 2 == 0:
                # Descent: Divide by 2
                # Drift = -1 bit
                drift = -1.0
                
                next_coeffs = relaxed_poly.coeffs[1:]
                if not next_coeffs: next_coeffs = [U(0)]
                poly = Polynomial(next_coeffs)
            else:
                # Ascent: 3n + 1
                # Drift = log2(3) ≈ +1.585 bits
                drift = 1.585
                
                x_plus_1 = Polynomial([U(1), U(1)])
                poly = (relaxed_poly * x_plus_1) + Polynomial([U(1)])
                
            # Log Data
            self.get_state('history_density').append(density)
            self.get_state('history_drift').append(drift)
            self.set_state('step', self.get_state('step') + 1)
            
        self.set_state('poly', poly)
        return True

    def _calculate_critical_threshold(self, df):
        """
        Bins the history data by Density and calculates Average Drift.
        Finds the density where Average Drift crosses 0.
        """
        # Create bins (0.0 to 1.0)
        df['bin'] = pd.cut(df['density'], bins=np.linspace(0, 1, 21), labels=np.linspace(0.025, 0.975, 20))
        grouped = df.groupby('bin', observed=False)['drift'].mean().reset_index()
        
        # Interpolate to find zero crossing
        zero_crossing = None
        for i in range(len(grouped) - 1):
            y1 = grouped.iloc[i]['drift']
            y2 = grouped.iloc[i+1]['drift']
            x1 = grouped.iloc[i]['bin']
            x2 = grouped.iloc[i+1]['bin']
            
            # Check sign flip
            if not np.isnan(y1) and not np.isnan(y2) and (y1 > 0 and y2 < 0):
                # Linear interpolation: y = mx + c
                m = (y2 - y1) / (x2 - x1)
                # 0 = m(x - x1) + y1  =>  -y1 = m(x - x1)  =>  x = x1 - y1/m
                if m != 0:
                    zero_crossing = x1 - (y1 / m)
                break
                
        return grouped, zero_crossing

    def render_main(self):
        if not self.get_state('history_density'):
            st.title("System Standby")
            st.markdown("Inject sparse matter ($2^{500} + 2^{250} + 1$) to begin Criticality Scan.")
            return

        # Prepare Data
        densities = self.get_state('history_density')
        drifts = self.get_state('history_drift')
        steps = np.arange(len(densities))
        
        df = pd.DataFrame({'step': steps, 'density': densities, 'drift': drifts})
        
        # Analyze Threshold
        grouped_data, critical_threshold = self._calculate_critical_threshold(df)

        # --- HUD ---
        curr_density = densities[-1]
        
        # Dynamic Status
        if critical_threshold:
            status_text = f"CRITICALITY FOUND: ρ ≈ {critical_threshold:.3f}"
            status_color = "#10b981" # Green
        else:
            status_text = "SCANNING FOR CROSSOVER..."
            status_color = "#eab308" # Yellow

        st.markdown(f"""
        <div style="display:flex; gap: 40px; margin-bottom: 20px; align-items: center;">
            <div>
                <div class="telemetry-label">Current Density</div>
                <div class="telemetry-value">{curr_density:.4f}</div>
            </div>
             <div>
                <div class="telemetry-label">System Status</div>
                <div class="telemetry-value" style="color: {status_color}">{status_text}</div>
            </div>
            <div>
                <div class="telemetry-label">Sample Size</div>
                <div class="telemetry-value">{len(densities)} Steps</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- VISUALIZATION ---
        col1, col2 = st.columns([2, 1])

        # Graph 1: Buoyancy Analysis (The Zero Crossing)
        with col1:
            st.markdown("**1. Stability Analysis (Drift vs Density)**")
            fig_buoy = go.Figure()
            
            # Plot the binned average curve
            # Filter out NaNs for clean plotting
            clean_group = grouped_data.dropna()
            
            fig_buoy.add_trace(go.Scatter(
                x=clean_group['bin'], 
                y=clean_group['drift'],
                mode='lines+markers',
                name='Avg Drift',
                line=dict(color='#f472b6', width=3, shape='spline')
            ))
            
            # Zero Line (The Waterline)
            fig_buoy.add_hline(y=0, line_color="#ef4444", line_width=2, line_dash="solid", annotation_text="Stable (Net Zero)")
            
            # Growth Line
            fig_buoy.add_hline(y=1.585, line_color="#22d3ee", line_width=1, line_dash="dash", annotation_text="Pure Growth")
            
            # Plot the detected intersection
            if critical_threshold:
                 fig_buoy.add_vline(x=critical_threshold, line_color="#10b981", line_dash="dot", 
                                    annotation_text=f"Critical Threshold: {critical_threshold:.3f}")

            fig_buoy.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.05)',
                xaxis_title="Bit Density (ρ)", 
                yaxis_title="Net Drift (Bits/Step)",
                yaxis=dict(range=[-1.2, 1.8]),
                xaxis=dict(range=[0, 1])
            )
            st.plotly_chart(fig_buoy, use_container_width=True)

        # Graph 2: The Mixing Curve (Time Series)
        with col2:
            st.markdown("**2. Mixing Progress**")
            fig_mix = go.Figure()
            
            fig_mix.add_trace(go.Scatter(
                x=steps[-500:], # Show last 500 steps for clarity
                y=densities[-500:],
                mode='lines',
                line=dict(color='#22d3ee')
            ))
            
            fig_mix.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.05)',
                xaxis_title="Step (Recent)", yaxis_title="Density",
                yaxis=dict(range=[0, 1])
            )
            st.plotly_chart(fig_mix, use_container_width=True)