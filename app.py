# import control as ct
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import streamlit as st

# # --- PAGE CONFIG ---
# st.set_page_config(
#     page_title="DC Motor Classical Controllers Study", layout="wide"
# )

# st.title("⚡ DC Motor Control & State Variable Analysis")
# st.write(
#     "Simulation and performance study of classical controllers (P, PD, PI, PID)"
#     " with customizable motor parameters and selective controller viewing."
# )

# # --- SIDEBAR: MOTOR PARAMETERS & CONFIGURATION ---
# st.sidebar.header("1. DC Motor Parameters")
# J = st.sidebar.number_input(
#     "Moment of Inertia (J)", value=0.01, format="%.4f"
# )
# B = st.sidebar.number_input(
#     "Viscous Friction (B)", value=0.10, format="%.4f"
# )
# Kt = st.sidebar.number_input("Torque Constant (Kt)", value=0.01, format="%.4f")
# Kb = st.sidebar.number_input("Back EMF Constant (Kb)", value=0.01, format="%.4f")
# Ra = st.sidebar.number_input(
#     "Armature Resistance (Ra)", value=1.00, format="%.2f"
# )
# La = st.sidebar.slider(
#     "Armature Inductance (La)", min_value=0.01, max_value=2.0, value=0.5, step=0.01
# )

# st.sidebar.header("2. Controller Selection")
# available_controllers = ["P", "PD", "PI", "PID"]
# selected_controllers = st.sidebar.multiselect(
#     "Select Controllers to Display:",
#     available_controllers,
#     default=["P", "PI", "PID"],
# )

# st.sidebar.header("3. Controller Tuning Gains")
# kp = st.sidebar.slider("Proportional Gain (Kp)", 0.0, 200.0, 100.0, 1.0)
# ki = st.sidebar.slider("Integral Gain (Ki)", 0.0, 50.0, 10.0, 0.5)
# kd = st.sidebar.slider("Derivative Gain (Kd)", 0.0, 5.0, 1.0, 0.1)
# sim_time = st.sidebar.slider("Simulation Time (s)", 1.0, 10.0, 5.0, 0.5)


# # --- BACKEND SIMULATION LOGIC ---
# @st.cache_data
# def run_motor_simulations(J, B, Kt, Kb, Ra, La, kp, ki, kd, sim_time):
#   # Open-loop Motor Transfer Function G(s) for Speed
#   num = [Kt]
#   den = [La * J, La * B + Ra * J, Ra * B + Kt * Kb]
#   G = ct.tf(num, den)

#   time = np.linspace(0, sim_time, 1000)
#   results = {}

#   # Controllers definition in transfer function form
#   controllers_map = {
#       "P": ct.tf([kp], [1]),
#       "PD": ct.tf([kd, kp], [1]),
#       "PI": ct.tf([kp, ki], [1, 0]),
#       "PID": ct.tf([kd, kp, ki], [1, 0]),
#   }

#   for name, C_tf in controllers_map.items():
#     # Standard feedback interconnection
#     T_sys = ct.feedback(C_tf * G, 1)

#     # Simulate step response for speed output
#     t, speed_response = ct.step_response(T_sys, T=time)

#     # Calculate performance metrics
#     info = ct.step_info(T_sys)
#     final_val = ct.dcgain(T_sys)
#     ess = abs(1.0 - final_val)

#     metrics = {
#         "Rise Time (s)": round(info.get("RiseTime", 0.0), 4),
#         "Settling Time (s)": round(info.get("SettlingTime", 0.0), 4),
#         "Overshoot (%)": round(info.get("Overshoot", 0.0), 2),
#         "Steady-State Error": round(ess, 4),
#         "Poles": [str(p) for p in ct.poles(T_sys)],
#     }

#     # Numerical tracking of state trajectories (Current, Speed, Position)
#     dt = time[1] - time[0]
#     ia_arr, omega_arr, theta_arr = [], [], []

#     ia, omega, theta = 0.0, 0.0, 0.0
#     int_err, prev_err = 0.0, 0.0

#     for step_t in time:
#       ref = 1.0 if step_t >= 0 else 0.0
#       err = ref - omega

#       if name == "P":
#         va = kp * err
#       elif name == "PD":
#         der = (err - prev_err) / dt if dt > 0 else 0.0
#         va = (kp * err) + (kd * der)
#       elif name == "PI":
#         int_err += err * dt
#         va = (kp * err) + (ki * int_err)
#       elif name == "PID":
#         int_err += err * dt
#         der = (err - prev_err) / dt if dt > 0 else 0.0
#         va = (kp * err) + (ki * int_err) + (kd * der)
#       else:
#         va = 0.0

#       prev_err = err

#       # Motor state-space derivatives
#       dia_dt = (va - Ra * ia - Kb * omega) / La
#       domega_dt = (Kt * ia - B * omega) / J
#       dtheta_dt = omega

#       ia += dia_dt * dt
#       omega += domega_dt * dt
#       theta += dtheta_dt * dt

#       ia_arr.append(ia)
#       omega_arr.append(omega)
#       theta_arr.append(theta)

#     results[name] = {
#         "time": t,
#         "speed": np.array(omega_arr),
#         "current": np.array(ia_arr),
#         "position": np.array(theta_arr),
#         "metrics": metrics,
#     }

#   return results


# # Run simulations
# results = run_motor_simulations(J, B, Kt, Kb, Ra, La, kp, ki, kd, sim_time)

# # --- FRONTEND TABS ---
# tab1, tab2, tab3, tab4 = st.tabs([
#     "📊 Speed Responses",
#     "📈 State Variables (Current, Speed, Position)",
#     "📋 Performance Metrics",
#     "🗺️ Pole Map",
# ])

# with tab1:
#   st.subheader("Closed-Loop Speed Response (Selected Controllers)")
#   if not selected_controllers:
#     st.warning(
#         "Please select at least one controller from the sidebar to display the"
#         " graph."
#     )
#   else:
#     fig, ax = plt.subplots(figsize=(10, 5))
#     for name in selected_controllers:
#       if name in results:
#         data = results[name]
#         ax.plot(data["time"], data["speed"], label=f"{name} Controller", linewidth=2)
#     ax.axhline(y=1.0, color="gray", linestyle=":", label="Unit Reference")
#     ax.set_xlabel("Time (s)")
#     ax.set_ylabel("Angular Speed (rad/s)")
#     ax.grid(True, linestyle=":", alpha=0.6)
#     ax.legend()
#     st.pyplot(fig)

# with tab2:
#   st.subheader("State Variables Dynamic Viewer")
#   if not selected_controllers:
#     st.warning("Please select at least one controller from the sidebar.")
#   else:
#     fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

#     for name in selected_controllers:
#       if name in results:
#         d = results[name]
#         # 1. Angular Speed
#         ax1.plot(d["time"], d["speed"], label=f"{name} Speed", linewidth=2)
#         # 2. Armature Current
#         ax2.plot(d["time"], d["current"], label=f"{name} Current", linewidth=2)
#         # 3. Angular Position
#         ax3.plot(d["time"], d["position"], label=f"{name} Position", linewidth=2)

#     ax1.set_ylabel("Speed (rad/s)")
#     ax1.grid(True, linestyle=":", alpha=0.6)
#     ax1.legend(loc="upper right")
#     ax1.set_title("Angular Speed $\\omega(t)$")

#     ax2.set_ylabel("Current (A)")
#     ax2.grid(True, linestyle=":", alpha=0.6)
#     ax2.legend(loc="upper right")
#     ax2.set_title("Armature Current $i_a(t)$")

#     ax3.set_ylabel("Position (rad)")
#     ax3.set_xlabel("Time (s)")
#     ax3.grid(True, linestyle=":", alpha=0.6)
#     ax3.legend(loc="upper right")
#     ax3.set_title("Angular Position $\\theta(t)$")

#     st.pyplot(fig)

# with tab3:
#   st.subheader("Performance Comparison Table")
#   if not selected_controllers:
#     st.info("Select controllers in the sidebar to view metrics.")
#   else:
#     metrics_data = {
#         name: {k: v for k, v in results[name]["metrics"].items() if k != "Poles"}
#         for name in selected_controllers
#         if name in results
#     }
#     df = pd.DataFrame(metrics_data).T
#     st.dataframe(df, use_container_width=True)

# with tab4:
#   st.subheader("Closed-Loop Poles Overview")
#   if not selected_controllers:
#     st.info("Select controllers in the sidebar.")
#   else:
#     selected_pole_ctrl = st.selectbox(
#         "Select Controller to view Poles:", selected_controllers
#     )
#     if selected_pole_ctrl in results:
#       poles = results[selected_pole_ctrl]["metrics"]["Poles"]
#       st.write(f"**Poles for {selected_pole_ctrl} Controller:**")
#       for p in poles:
#         st.code(p)


import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DC Motor Classical Controllers Study", layout="wide"
)

st.title("⚡ DC Motor Control & State Variable Analysis")
st.write(
    "Simulation and performance study of classical controllers (P, PD, PI, PID)"
    " with customizable motor parameters, reference setpoint tracking, and controller comparison."
)

# --- SIDEBAR: MOTOR PARAMETERS & CONFIGURATION ---
st.sidebar.header("1. Reference Input")
ref_speed = st.sidebar.number_input(
    "Target Reference Speed (rad/s)", value=100.0, step=10.0, format="%.2f"
)

st.sidebar.header("2. DC Motor Parameters")
J = st.sidebar.number_input(
    "Moment of Inertia (J)", value=0.01, format="%.4f"
)
B = st.sidebar.number_input(
    "Viscous Friction (B)", value=0.10, format="%.4f"
)
Kt = st.sidebar.number_input("Torque Constant (Kt)", value=0.01, format="%.4f")
Kb = st.sidebar.number_input("Back EMF Constant (Kb)", value=0.01, format="%.4f")
Ra = st.sidebar.number_input(
    "Armature Resistance (Ra)", value=1.00, format="%.2f"
)
La = st.sidebar.slider(
    "Armature Inductance (La)", min_value=0.01, max_value=2.0, value=0.5, step=0.01
)

st.sidebar.header("3. Controller Selection")
available_controllers = ["P", "PD", "PI", "PID"]
selected_controllers = st.sidebar.multiselect(
    "Select Controllers to Display:",
    available_controllers,
    default=["P", "PI", "PID"],
)

st.sidebar.header("4. Controller Tuning Gains")
kp = st.sidebar.slider("Proportional Gain (Kp)", 0.0, 500.0, 100.0, 1.0)
ki = st.sidebar.slider("Integral Gain (Ki)", 0.0, 200.0, 20.0, 0.5)
kd = st.sidebar.slider("Derivative Gain (Kd)", 0.0, 20.0, 1.0, 0.1)
sim_time = st.sidebar.slider("Simulation Time (s)", 1.0, 10.0, 5.0, 0.5)


# --- BACKEND SIMULATION LOGIC ---
@st.cache_data
def run_motor_simulations(J, B, Kt, Kb, Ra, La, kp, ki, kd, sim_time, ref_speed):
    # Open-loop Motor Transfer Function G(s) for Speed
    num = [Kt]
    den = [La * J, La * B + Ra * J, Ra * B + Kt * Kb]
    G = ct.tf(num, den)

    time = np.linspace(0, sim_time, 1000)
    results = {}

    # Controllers definition in transfer function form
    controllers_map = {
        "P": ct.tf([kp], [1]),
        "PD": ct.tf([kd, kp], [1]),
        "PI": ct.tf([kp, ki], [1, 0]),
        "PID": ct.tf([kd, kp, ki], [1, 0]),
    }

    for name, C_tf in controllers_map.items():
        # Closed-loop transfer function
        T_sys = ct.feedback(C_tf * G, 1)

        # Calculate metrics from unit step info
        info = ct.step_info(T_sys)
        dc_gain = ct.dcgain(T_sys)
        
        # Absolute steady-state error with respect to reference speed
        steady_state_speed = dc_gain * ref_speed
        ess = abs(ref_speed - steady_state_speed)

        metrics = {
            "Target Speed (rad/s)": round(ref_speed, 2),
            "Final Speed (rad/s)": round(float(steady_state_speed), 2),
            "Rise Time (s)": round(info.get("RiseTime", 0.0), 4),
            "Settling Time (s)": round(info.get("SettlingTime", 0.0), 4),
            "Overshoot (%)": round(info.get("Overshoot", 0.0), 2),
            "Steady-State Error": round(float(ess), 4),
            "Poles": [str(np.round(p, 4)) for p in ct.poles(T_sys)],
        }

        # Time domain step simulation for states
        dt = time[1] - time[0]
        ia_arr, omega_arr, theta_arr = [], [], []

        ia, omega, theta = 0.0, 0.0, 0.0
        int_err, prev_err = 0.0, 0.0

        for step_t in time:
            err = ref_speed - omega

            if name == "P":
                va = kp * err
            elif name == "PD":
                der = (err - prev_err) / dt if dt > 0 else 0.0
                va = (kp * err) + (kd * der)
            elif name == "PI":
                int_err += err * dt
                va = (kp * err) + (ki * int_err)
            elif name == "PID":
                int_err += err * dt
                der = (err - prev_err) / dt if dt > 0 else 0.0
                va = (kp * err) + (ki * int_err) + (kd * der)
            else:
                va = 0.0

            prev_err = err

            # Motor state-space differential equations
            dia_dt = (va - Ra * ia - Kb * omega) / La
            domega_dt = (Kt * ia - B * omega) / J
            dtheta_dt = omega

            # Euler integration
            ia += dia_dt * dt
            omega += domega_dt * dt
            theta += dtheta_dt * dt

            ia_arr.append(ia)
            omega_arr.append(omega)
            theta_arr.append(theta)

        results[name] = {
            "time": time,
            "speed": np.array(omega_arr),
            "current": np.array(ia_arr),
            "position": np.array(theta_arr),
            "metrics": metrics,
        }

    return results


# Run simulations
results = run_motor_simulations(J, B, Kt, Kb, Ra, La, kp, ki, kd, sim_time, ref_speed)

# --- FRONTEND TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Speed Responses",
    "📈 State Variables (Current, Speed, Position)",
    "📋 Performance Metrics",
    "🗺️ Pole Map",
])

with tab1:
    st.subheader(f"Closed-Loop Speed Response (Target: {ref_speed} rad/s)")
    if not selected_controllers:
        st.warning("Please select at least one controller from the sidebar to display the graph.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        for name in selected_controllers:
            if name in results:
                data = results[name]
                ax.plot(data["time"], data["speed"], label=f"{name} Controller", linewidth=2)
        ax.axhline(y=ref_speed, color="red", linestyle="--", label=f"Target Reference ({ref_speed} rad/s)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Angular Speed (rad/s)")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig)

with tab2:
    st.subheader("State Variables Dynamic Viewer")
    if not selected_controllers:
        st.warning("Please select at least one controller from the sidebar.")
    else:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

        for name in selected_controllers:
            if name in results:
                d = results[name]
                ax1.plot(d["time"], d["speed"], label=f"{name} Speed", linewidth=2)
                ax2.plot(d["time"], d["current"], label=f"{name} Current", linewidth=2)
                ax3.plot(d["time"], d["position"], label=f"{name} Position", linewidth=2)

        ax1.axhline(y=ref_speed, color="red", linestyle="--", alpha=0.7, label="Target Speed")
        ax1.set_ylabel("Speed (rad/s)")
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(loc="upper right")
        ax1.set_title(r"Angular Speed $\omega(t)$")

        ax2.set_ylabel("Current (A)")
        ax2.grid(True, linestyle=":", alpha=0.6)
        ax2.legend(loc="upper right")
        ax2.set_title(r"Armature Current $i_a(t)$")

        ax3.set_ylabel("Position (rad)")
        ax3.set_xlabel("Time (s)")
        ax3.grid(True, linestyle=":", alpha=0.6)
        ax3.legend(loc="upper right")
        ax3.set_title(r"Angular Position $\theta(t)$")

        st.pyplot(fig)

with tab3:
    st.subheader(f"Performance Comparison Table (Target Speed = {ref_speed} rad/s)")
    if not selected_controllers:
        st.info("Select controllers in the sidebar to view metrics.")
    else:
        metrics_data = {
            name: {k: v for k, v in results[name]["metrics"].items() if k != "Poles"}
            for name in selected_controllers
            if name in results
        }
        df = pd.DataFrame(metrics_data).T
        st.dataframe(df, use_container_width=True)

with tab4:
    st.subheader("Closed-Loop Poles Overview")
    if not selected_controllers:
        st.info("Select controllers in the sidebar.")
    else:
        selected_pole_ctrl = st.selectbox(
            "Select Controller to view Poles:", selected_controllers
        )
        if selected_pole_ctrl in results:
            poles = results[selected_pole_ctrl]["metrics"]["Poles"]
            st.write(f"**Poles for {selected_pole_ctrl} Controller:**")
            for p in poles:
                st.code(p)