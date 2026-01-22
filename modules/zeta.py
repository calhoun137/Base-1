import streamlit as st
import pandas as pd
import altair as alt
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base import DashboardModule
from core.science_mode import U
from core.algorithms import Euclid
from core.stream import Stream
from core.continued_fraction import ContinuedFraction
from core.riemann_siegel import stirling_theta
from core.gosper import GosperProbe

class ZetaModule(DashboardModule):
    @property
    def id(self) -> str: return "zeta_lab"

    @property
    def display_name(self) -> str: return "Riemann Zeta Laboratory"

    def render_sidebar(self):
        st.sidebar.markdown("### // Riemann-Siegel Scanner")
        
        mode = st.sidebar.radio("Operation Mode", ["Critical Line Scan", "Single Point Analysis"])
        self.set_state('mode', mode)

        if mode == "Critical Line Scan":
            t_start = st.sidebar.number_input("Start t", value=14.0, step=0.1)
            t_end = st.sidebar.number_input("End t", value=15.0, step=0.1)
            steps = st.sidebar.slider("Resolution (Steps)", min_value=10, max_value=1000, value=100)
            
            if st.sidebar.button("▶ START SCAN", type="primary"):
                self._run_scan(t_start, t_end, steps)
                
        else:
            t_target = st.sidebar.number_input("Target t", value=14.1347, format="%.5f")
            depth = st.sidebar.slider("Stream Depth (Precision)", 10, 100, 30)
            
            if st.sidebar.button("▶ ANALYZE POINT", type="primary"):
                self._analyze_point(t_target, depth)

    def render_main(self):
        mode = self.get_state('mode')

        # --- MODE 1: SCAN ---
        if mode == "Critical Line Scan":
            results = self.get_state('scan_results')
            if not results:
                st.info("System Ready. Configure Scan Parameters in Sidebar.")
                return

            # Visualization
            df = pd.DataFrame(results)
            
            # Chart 1: The Zeta Function
            base = alt.Chart(df).encode(x='t')
            line = base.mark_line(color='#3b82f6', size=3).encode(
                y=alt.Y('Z(t)', title='Riemann-Siegel Z(t)'),
                tooltip=['t', 'Z(t)', 'Theta (rad)']
            )
            zero_rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='#ef4444', strokeDash=[5,5]).encode(y='y')
            
            st.markdown("### 1. The Critical Line (Zeta Value)")
            st.altair_chart((line + zero_rule).interactive(), use_container_width=True)
            
            # Chart 2: Entropy Heat Map
            st.markdown("### 2. Computational Entropy (Thermodynamics)")
            
            entropy_chart = base.mark_area(color='#f59e0b', opacity=0.6).encode(
                y=alt.Y('Max Entropy', title='Peak Shannon Entropy (bits)'),
                tooltip=['t', 'Max Entropy', 'Total Ops']
            )
            st.altair_chart(entropy_chart.interactive(), use_container_width=True)
            
            # Chart 3: Fano Resonance (Spectral Analysis)
            # [NEW] We visualize the breakdown of the entropy into R/G/B channels
            if 'peak_fano_r' in df.columns:
                st.markdown("### 3. Fano Resonance (Algebraic Spectrum)")
                st.caption("Shows the dominant algebraic sector (R/G/B) at the moment of peak computational stress.")
                
                # We need to melt the dataframe to stack the colors
                df_fano = df.melt('t', value_vars=['peak_fano_r', 'peak_fano_g', 'peak_fano_b'], 
                                  var_name='channel', value_name='intensity')
                
                # Map names to clean labels if needed
                color_scale = alt.Scale(domain=['peak_fano_r', 'peak_fano_g', 'peak_fano_b'], 
                                        range=['#ef4444', '#22c55e', '#3b82f6'])
                
                fano_scan_chart = alt.Chart(df_fano).mark_area(opacity=0.8).encode(
                    x='t',
                    y=alt.Y('intensity', stack='normalize', title='Relative Fano Mass'),
                    color=alt.Color('channel', scale=color_scale, legend=alt.Legend(title="Fano Axis")),
                    tooltip=['t', 'channel', 'intensity']
                ).properties(height=250)
                
                st.altair_chart(fano_scan_chart.interactive(), use_container_width=True)
            
            with st.expander("View Raw Data"):
                st.dataframe(df)

        # --- MODE 2: SINGLE POINT (DEEP DIVE) ---
        elif mode == "Single Point Analysis":
            single_res = self.get_state('single_result')
            if not single_res:
                st.info("System Ready. Enter Target t.")
                return

            st.markdown(f"### Deep Dive: t = {single_res['t']}")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Z(t)", f"{single_res['Z(t)']:.5f}")
            col2.metric("Theta (rad)", f"{single_res['Theta (rad)']:.5f}")
            col3.metric("Peak Entropy", f"{single_res['Max Entropy']:.2f} bits")
            
            st.markdown(f"**Theta Stream:** `{single_res['Theta Terms']}`")
            
            # Retrieve Log Data SAFELY
            log_data = single_res.get('Entropy Log', [])
            
            # --- Chart 3: The Entropy Seismograph ---
            st.markdown("### 3. Entropy Seismograph (Live Probe)")
            st.caption("Visualizing the internal state of the 8-coefficient tensor.")
            
            if log_data:
                df_log = pd.DataFrame(log_data).reset_index()
                
                seismo = alt.Chart(df_log).mark_line(size=1).encode(
                    x=alt.X('index', title='Computation Step'),
                    y=alt.Y('entropy', title='Shannon Entropy (bits)'),
                    color=alt.Color('depth', title='Pipeline Depth', scale=alt.Scale(scheme='magma')),
                    tooltip=['index', 'entropy', 'depth']
                ).properties(height=300)
                st.altair_chart(seismo.interactive(), use_container_width=True)

                # --- Chart 4: Fano Spectrograph (RGB) ---
                st.markdown("### 4. Fano Resonance (Algebraic Stress)")
                st.caption("Visualizing the Projective State in P^7 projected to RGB.")

                if 'fano_r' in df_log.columns:
                    df_long = df_log.melt('index', value_vars=['fano_r', 'fano_g', 'fano_b'], 
                                           var_name='channel', value_name='intensity')
                    
                    color_scale = alt.Scale(domain=['fano_r', 'fano_g', 'fano_b'], range=['#ef4444', '#22c55e', '#3b82f6'])
                    
                    fano_chart = alt.Chart(df_long).mark_area(opacity=0.6).encode(
                        x=alt.X('index', title='Computation Step'),
                        y=alt.Y('intensity', stack='normalize', title='Relative Mass (Fano Projection)'),
                        color=alt.Color('channel', scale=color_scale, legend=alt.Legend(title="Fano Axis")),
                        tooltip=['index', 'channel', 'intensity']
                    ).properties(height=300)
                    
                    st.altair_chart(fano_chart.interactive(), use_container_width=True)
            else:
                st.warning("No entropy log data available.")

    # --- Logic Helpers ---

    def _evaluate_stream_captured(self, cf_obj, depth=30):
        terms = []
        iterator = iter(cf_obj)
        for _ in range(depth):
            try:
                terms.append(int(next(iterator)))
            except StopIteration:
                break
        
        if not terms: return 0.0, []
        val = 0.0
        for t in reversed(terms):
            if val == 0: val = float(t)
            else: val = float(t) + (1.0 / val)
        return val, terms

    def _run_simulation_step(self, t_float, depth=20):
        # Convert float t to Rational (High Precision)
        den = 100
        num = int(t_float * den)
        
        # 1. Materialize 't'
        t_proc = Euclid(U(num), U(den))
        t_cf = ContinuedFraction(Stream(t_proc))
        
        # 2. Run Engine with Probe
        entropy_log = []
        
        with GosperProbe() as probe:
            theta_cf = stirling_theta(t_cf)
            theta_val, theta_terms = self._evaluate_stream_captured(theta_cf, depth=depth)
            entropy_log = list(probe.log)
            
        # 3. Compute Z(t) ~ 2 * cos(theta)
        z_val = 2 * math.cos(theta_val)
        
        # [NEW] Extract Peak Fano Resonance
        # We find the moment of maximum entropy and capture the Fano Color
        peak_entropy = 0
        peak_fano = {'r': 0.33, 'g': 0.33, 'b': 0.33} # Default gray
        
        if entropy_log:
            # Find the record with max entropy
            peak_record = max(entropy_log, key=lambda x: x['entropy'])
            peak_entropy = peak_record['entropy']
            
            # Check if Fano data exists (it should with updated gosper.py)
            if 'fano_r' in peak_record:
                peak_fano = {
                    'r': peak_record['fano_r'],
                    'g': peak_record['fano_g'],
                    'b': peak_record['fano_b']
                }
        
        return {
            "t": t_float,
            "Z(t)": z_val,
            "Theta (rad)": theta_val,
            "Theta Terms": str(theta_terms[:5]) + "...",
            "Max Entropy": peak_entropy,
            "Total Ops": len(entropy_log),
            "peak_fano_r": peak_fano['r'],
            "peak_fano_g": peak_fano['g'],
            "peak_fano_b": peak_fano['b'],
            # We still keep the log if needed, but Scan mode ignores it to save RAM usually.
            # "Entropy Log": entropy_log 
        }

    def _run_scan(self, start, end, steps):
        results = []
        step_size = (end - start) / steps
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(steps + 1):
            t_current = start + (i * step_size)
            status_text.text(f"Computing t = {t_current:.4f}...")
            
            data = self._run_simulation_step(t_current)
            results.append(data)
            
            progress_bar.progress((i + 1) / (steps + 1))
            
        progress_bar.empty()
        status_text.empty()
        self.set_state('scan_results', results)

    def _analyze_point(self, t, depth):
        with st.spinner("Spinning up Gosper Tensor..."):
            # Deep dive needs the full log
            data = self._run_simulation_step(t, depth)
            
            # Re-attach the log if we optimized it out in run_simulation_step?
            # Actually, let's make sure run_simulation_step returns the log for Single Point
            # We can modify _run_simulation_step to optionally drop log, or just keep it.
            # For simplicity, let's ensure the log is passed.
            
            # Re-running the probe logic to guarantee log presence:
            den = 100
            num = int(t * den)
            t_proc = Euclid(U(num), U(den))
            t_cf = ContinuedFraction(Stream(t_proc))
            with GosperProbe() as probe:
                theta_cf = stirling_theta(t_cf)
                theta_val, theta_terms = self._evaluate_stream_captured(theta_cf, depth=depth)
                data['Entropy Log'] = list(probe.log)
                
        self.set_state('single_result', data)