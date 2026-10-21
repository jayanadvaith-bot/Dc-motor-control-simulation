# ⚡ DC Motor Classical Controllers Study & State Variable Analysis

An interactive Streamlit-based web application for simulating, tuning, and comparing classical controllers (**P, PD, PI, PID**) applied to a separately excited DC motor. This project is built to study dynamic speed tracking, transient characteristics, armature current, rotor position, and closed-loop pole locations.

---

## 🚀 Features
- **Customizable Motor Parameters:** Adjust moment of inertia ($J$), viscous friction ($B$), torque constant ($K_t$), back-EMF constant ($K_b$), armature resistance ($R_a$), and armature inductance ($L_a$).
- **Reference Speed Tracking:** Input any target reference speed ($\text{rad/s}$) and analyze how effectively each controller tracks the setpoint.
- **Interactive Controller Tuning:** Dynamically adjust Proportional ($K_p$), Integral ($K_i$), and Derivative ($K_d$) gains via the sidebar.
- **Multi-Tab Dashboard:**
  - 📊 **Speed Responses:** Compares closed-loop speed output against the target reference line.
  - 📈 **State Variables:** Multi-axis dynamic viewer for Angular Speed ($\omega(t)$), Armature Current ($i_a(t)$), and Angular Position ($\theta(t)$).
  - 📋 **Performance Metrics:** Generates comparison tables for rise time, settling time, overshoot, and steady-state error.
  - 🗺️ **Pole Map:** Inspects closed-loop poles for stability analysis.

---

## 🛠️ Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/your-username/dc-motor-classical-controllers.git](https://github.com/your-username/dc-motor-classical-controllers.git)
   cd dc-motor-classical-controllers
