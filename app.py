import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Tilt Table Test Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 5px solid #1f77b4;
        border-radius: 0 5px 5px 0;
    }
    .checklist-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-left: 3px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #dc3545;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #28a745;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #17a2b8;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'checklist_progress' not in st.session_state:
    st.session_state.checklist_progress = {}
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'test_results' not in st.session_state:
    st.session_state.test_results = {}
if 'test_phase' not in st.session_state:
    st.session_state.test_phase = 'passive'

# Helper functions
def update_progress(category, item, value):
    if category not in st.session_state.checklist_progress:
        st.session_state.checklist_progress[category] = {}
    st.session_state.checklist_progress[category][item] = value

def get_progress_percentage(category, total_items):
    if category not in st.session_state.checklist_progress:
        return 0
    completed = sum(1 for v in st.session_state.checklist_progress[category].values() if v)
    return int((completed / total_items) * 100)

def generate_report():
    report = f"""
    TILT TABLE TEST REPORT
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    PATIENT INFORMATION:
    - Patient ID: {st.session_state.patient_data.get('patient_id', 'N/A')}
    - Age: {st.session_state.patient_data.get('age', 'N/A')}
    - Gender: {st.session_state.patient_data.get('gender', 'N/A')}
    - Weight: {st.session_state.patient_data.get('weight', 'N/A')} kg
    - Indication: {st.session_state.patient_data.get('indication', 'N/A')}
    
    TEST PARAMETERS:
    - Tilt Angle: {st.session_state.test_results.get('tilt_angle', 'N/A')} degrees
    - Test Duration: {st.session_state.test_results.get('duration', 'N/A')} minutes
    - Drug Provocation: {st.session_state.test_results.get('drug_used', 'None')}
    
    BASELINE VITALS:
    - Baseline HR: {st.session_state.test_results.get('baseline_hr', 'N/A')} bpm
    - Baseline SBP: {st.session_state.test_results.get('baseline_sbp', 'N/A')} mmHg
    - Baseline DBP: {st.session_state.test_results.get('baseline_dbp', 'N/A')} mmHg
    
    RESULTS:
    - Test Result: {st.session_state.test_results.get('result', 'N/A')}
    - Minimum HR: {st.session_state.test_results.get('min_hr', 'N/A')} bpm
    - Minimum SBP: {st.session_state.test_results.get('min_sbp', 'N/A')} mmHg
    - Symptoms: {st.session_state.test_results.get('symptoms', 'N/A')}
    - Time to Symptoms: {st.session_state.test_results.get('time_to_symptoms', 'N/A')} min
    
    INTERPRETATION:
    {st.session_state.test_results.get('interpretation', 'N/A')}
    
    RECOMMENDATIONS:
    {st.session_state.test_results.get('recommendations', 'N/A')}
    """
    return report

def get_download_link(text, filename):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background-color:#1f77b4;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">Download Report</button></a>'

# Sidebar navigation
st.sidebar.title("📋 Navigation")
steps = [
    "🏠 Home",
    "✅ Pre-Test Preparation", 
    "⚠️ Safety & Contraindications",
    "🩺 Patient Setup",
    "📊 Performing Test",
    "🔍 Analysis & Report"
]

for i, step in enumerate(steps):
    if st.sidebar.button(step, key=f"nav_{i}", use_container_width=True):
        st.session_state.current_step = i

st.sidebar.markdown("---")
st.sidebar.info("Tilt Table Test Assistant v1.0\n\nBased on ESC 2018 Guidelines & ACC/AHA/HRS 2017 Guidelines")

# Main content based on current step
current = st.session_state.current_step

if current == 0:  # Home
    st.markdown('<div class="main-header">🏥 Tilt Table Test Assistant</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to the Comprehensive Tilt Table Test Management System
        
        This application guides healthcare professionals through the complete tilt table testing process:
        
        **📋 Features:**
        - **Step-by-step preparation checklists** (Equipment, Medications, Emergency)
        - **Safety screening** with contraindication detection
        - **Patient parameter input** with real-time monitoring
        - **Automated result analysis** based on international guidelines
        - **Comprehensive report generation**
        
        **🎯 Clinical Applications:**
        - Evaluation of vasovagal syncope
        - Orthostatic hypotension assessment
        - Postural Tachycardia Syndrome (POTS) screening
        - Convulsive syncope vs. epilepsy differentiation
        - Pseudosyncope detection
        
        **⚠️ Important:** This tool is for clinical decision support only. 
        Final clinical decisions should always be made by qualified healthcare providers.
        """)
        
        if st.button("Start Preparation →", type="primary", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>📊 Test Statistics</h4>
            <p><strong>Passive Phase Sensitivity:</strong> 13-75%</p>
            <p><strong>Passive Phase Specificity:</strong> >90%</p>
            <p><strong>Drug Phase Sensitivity:</strong> 42-87%</p>
            <p><strong>Standard Tilt Angle:</strong> 60-70°</p>
            <p><strong>Passive Duration:</strong> 20-45 min</p>
        </div>
        """, unsafe_allow_html=True)

elif current == 1:  # Pre-Test Preparation
    st.markdown('<div class="section-header">✅ Pre-Test Preparation Checklist</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🔧 Equipment", "💊 Medications", "🚨 Emergency", "📋 Patient Prep"])
    
    # Equipment Tab
    with tabs[0]:
        st.subheader("Equipment Readiness")
        
        equipment_items = {
            "Motorized tilt table (60-70° capability)": False,
            "Foot board and safety restraints": False,
            "ECG monitor (3 or 6 lead capability)": False,
            "Beat-to-beat BP monitor (finger plethysmography)": False,
            "IV access supplies": False,
            "Emergency crash cart available": False,
            "Defibrillator ready": False,
            "Atropine 1mg IV available": False,
            "Isoproterenol/nitroglycerin if needed": False,
            "Timer/stopwatch": False,
            "Emergency lowering capability (<10 sec)": False
        }
        
        progress = get_progress_percentage('equipment', len(equipment_items))
        st.progress(progress / 100, text=f"Equipment Readiness: {progress}%")
        
        for item in equipment_items.keys():
            checked = st.checkbox(item, key=f"eq_{item}", 
                                value=st.session_state.checklist_progress.get('equipment', {}).get(item, False))
            update_progress('equipment', item, checked)
        
        if progress == 100:
            st.success("✅ All equipment ready!")
        elif progress > 50:
            st.warning("⚠️ Equipment partially ready")
        else:
            st.error("❌ Equipment not ready")
    
    # Medications Tab
    with tabs[1]:
        st.subheader("Medication Readiness")
        
        st.markdown("""
        <div class="info-box">
        <strong>Drug Provocation Protocol:</strong><br>
        Use ONLY after nondiagnostic passive phase. Choose ONE:
        <ul>
            <li><strong>Isoproterenol:</strong> 1-3 mcg/min, target HR +20-25%</li>
            <li><strong>Nitroglycerin:</strong> 300-400 mcg SL (Italian protocol)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        med_items = {
            "Isoproterenol available (if using)": False,
            "Nitroglycerin available (if using)": False,
            "Atropine 1mg IV (emergency)": False,
            "Normal saline 500ml-1L (hydration)": False,
            "IV fluids administration set": False,
            "Emergency medications checked (not expired)": False,
            "Sildenafil/Vardenafil washout confirmed (>24h)": False,
            "Tadalafil washout confirmed (>48h)": False
        }
        
        progress = get_progress_percentage('medications', len(med_items))
        st.progress(progress / 100, text=f"Medication Readiness: {progress}%")
        
        for item in med_items.keys():
            checked = st.checkbox(item, key=f"med_{item}",
                                value=st.session_state.checklist_progress.get('medications', {}).get(item, False))
            update_progress('medications', item, checked)
        
        st.markdown("""
        <div class="warning-box">
        <strong>⚠️ Contraindications for Isoproterenol:</strong>
        <ul>
            <li>Severe coronary artery disease</li>
            <li>Uncontrolled hypertension</li>
            <li>LV outflow tract obstruction</li>
            <li>Significant aortic stenosis</li>
            <li>Known serious arrhythmias</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Emergency Tab
    with tabs[2]:
        st.subheader("Emergency Readiness")
        
        emergency_items = {
            "Crash cart immediately available": False,
            "Atropine drawn and labeled": False,
            "Defibrillator pads attached": False,
            "Oxygen supply ready": False,
            "Airway management equipment": False,
            "Emergency team contact confirmed": False,
            "IV access patent and functional": False,
            "Patient consented for procedure": False,
            "Emergency lowering procedure reviewed": False,
            "Continuous monitoring confirmed": False
        }
        
        progress = get_progress_percentage('emergency', len(emergency_items))
        st.progress(progress / 100, text=f"Emergency Readiness: {progress}%")
        
        for item in emergency_items.keys():
            checked = st.checkbox(item, key=f"em_{item}",
                                value=st.session_state.checklist_progress.get('emergency', {}).get(item, False))
            update_progress('emergency', item, checked)
        
        st.markdown("""
        <div class="danger-box">
        <strong>🚨 Emergency Protocols:</strong><br>
        If prolonged asystole or severe hypotension:
        <ol>
            <li>Return table to horizontal IMMEDIATELY (<10 seconds)</li>
            <li>Administer atropine 1mg IV if bradycardic</li>
            <li>IV fluids bolus</li>
            <li>CPR if no pulse</li>
            <li>Activate emergency response if needed</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Patient Preparation Tab
    with tabs[3]:
        st.subheader("Patient Preparation")
        
        st.markdown("""
        <div class="checklist-item">
        <strong>Fasting:</strong> 3-4 hours minimum (some recommend 8 hours overnight)
        </div>
        <div class="checklist-item">
        <strong>Medications:</strong> Hold or continue per clinical judgment
        </div>
        <div class="checklist-item">
        <strong>Environment:</strong> Quiet room, comfortable temperature, minimal distractions
        </div>
        <div class="checklist-item">
        <strong>IV Access:</strong> Place at least 30 minutes before test
        </div>
        <div class="checklist-item">
        <strong>Instructions:</strong> Patient should report ALL symptoms immediately
        </div>
        """, unsafe_allow_html=True)
        
        patient_prep = {
            "Patient fasting confirmed": False,
            "Medication status documented": False,
            "IV placed >30 min ago": False,
            "Room environment optimized": False,
            "Patient pre-test vitals stable": False,
            "Informed consent obtained": False
        }
        
        for item in patient_prep.keys():
            checked = st.checkbox(item, key=f"pp_{item}",
                                value=st.session_state.checklist_progress.get('patient_prep', {}).get(item, False))
            update_progress('patient_prep', item, checked)

elif current == 2:  # Safety & Contraindications
    st.markdown('<div class="section-header">⚠️ Safety Screening & Contraindications</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="danger-box">
    <strong>ABSOLUTE CONTRAINDICATIONS:</strong>
    <ul>
        <li>Severe coronary artery disease (hypotension may cause MI)</li>
        <li>Severe cerebrovascular disease (risk of cerebral ischemia)</li>
        <li>Pregnancy (hypotension harmful to fetus)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Screening Checklist")
        
        contraindications = {
            "Severe coronary artery disease": False,
            "Recent MI (<3 months)": False,
            "Severe aortic stenosis": False,
            "Severe cerebrovascular disease": False,
            "Pregnancy": False,
            "Uncontrolled hypertension": False,
            "LV outflow tract obstruction": False,
            "Severe anemia": False,
            "Acute illness/dehydration": False
        }
        
        risk_score = 0
        for condition, default in contraindications.items():
            checked = st.checkbox(f"⚠️ {condition}", key=f"contra_{condition}")
            if checked:
                risk_score += 1
        
        if risk_score > 0:
            st.error(f"🚨 {risk_score} contraindication(s) identified. Test should NOT proceed without cardiology clearance.")
        else:
            st.success("✅ No absolute contraindications identified")
    
    with col2:
        st.subheader("Drug-Specific Screening")
        
        st.markdown("If using **Isoproterenol**:")
        iso_contra = st.multiselect("Check all that apply:", 
            ["Coronary artery disease", "Uncontrolled HTN", "LVOT obstruction", 
             "Aortic stenosis", "History of VT/VF", "Recent MI"])
        
        st.markdown("If using **Nitroglycerin**:")
        nitro_contra = st.multiselect("Recent PDE5 inhibitor use:", 
            ["Sildenafil (<24h)", "Vardenafil (<24h)", "Tadalafil (<48h)"])
        
        if iso_contra:
            st.warning(f"⚠️ {len(iso_contra)} contraindication(s) for Isoproterenol")
        if nitro_contra:
            st.error(f"🚨 Nitroglycerin contraindicated! Wait appropriate washout period.")
    
    st.markdown("---")
    st.subheader("Risk Stratification")
    
    risk_level = st.radio("Patient Risk Category:", 
        ["Low Risk (No structural heart disease)", 
         "Intermediate Risk (Controlled comorbidities)",
         "High Risk (Structural heart disease present)"],
        horizontal=True)
    
    if risk_level == "High Risk (Structural heart disease present)":
        st.error("""
        🚨 HIGH RISK PATIENT - Additional precautions required:
        - Cardiology consultation recommended
        - Exclude cardiac causes before tilt testing
        - Consider alternative diagnostic methods
        - Have advanced life support immediately available
        """)

elif current == 3:  # Patient Setup
    st.markdown('<div class="section-header">🩺 Patient Setup & Baseline Parameters</div>', unsafe_allow_html=True)
    
    with st.form("patient_setup"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Demographics")
            patient_id = st.text_input("Patient ID", value=st.session_state.patient_data.get('patient_id', ''))
            age = st.number_input("Age (years)", 10, 100, value=st.session_state.patient_data.get('age', 30))
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                index=["Male", "Female", "Other"].index(st.session_state.patient_data.get('gender', 'Male')))
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 
                                   value=st.session_state.patient_data.get('weight', 70.0))
        
        with col2:
            st.subheader("Clinical Indication")
            indication = st.selectbox("Primary Indication", [
                "Recurrent unexplained syncope",
                "Single high-risk syncope episode",
                "Suspected vasovagal syncope",
                "Suspected orthostatic hypotension",
                "POTS evaluation",
                "Convulsive syncope vs epilepsy",
                "Pseudosyncope evaluation",
                "Autonomic dysfunction workup"
            ], index=["Recurrent unexplained syncope", "Single high-risk syncope episode", 
                     "Suspected vasovagal syncope", "Suspected orthostatic hypotension",
                     "POTS evaluation", "Convulsive syncope vs epilepsy",
                     "Pseudosyncope evaluation", "Autonomic dysfunction workup"
                     ].index(st.session_state.patient_data.get('indication', 'Recurrent unexplained syncope')) 
            if st.session_state.patient_data.get('indication') in 
            ["Recurrent unexplained syncope", "Single high-risk syncope episode", 
             "Suspected vasovagal syncope", "Suspected orthostatic hypotension",
             "POTS evaluation", "Convulsive syncope vs epilepsy",
             "Pseudosyncope evaluation", "Autonomic dysfunction workup"] else 0)
            
            history = st.text_area("Relevant History", 
                                 value=st.session_state.patient_data.get('history', ''),
                                 placeholder="Previous syncope episodes, injuries, occupation...")
            medications = st.text_area("Current Medications", 
                                     value=st.session_state.patient_data.get('medications', ''),
                                     placeholder="BP meds, diuretics, etc.")
        
        with col3:
            st.subheader("Test Protocol Selection")
            protocol = st.selectbox("Protocol Type", [
                "Standard Passive (20-45 min)",
                "Short Passive (15 min)",
                "Italian Protocol (Nitroglycerin)",
                "Isoproterenol Protocol",
                "Custom"
            ])
            
            tilt_angle = st.slider("Tilt Angle (degrees)", 60, 80, 70)
            max_duration = st.number_input("Max Duration (minutes)", 15, 60, 45)
            
            drug_provocation = st.checkbox("Plan Drug Provocation if Passive Negative")
            if drug_provocation:
                drug_choice = st.radio("Drug:", ["Isoproterenol", "Nitroglycerin"])
        
        st.markdown("---")
        st.subheader("Baseline Vitals")
        
        col_v1, col_v2, col_v3, col_v4 = st.columns(4)
        with col_v1:
            baseline_hr = st.number_input("Baseline HR (bpm)", 40, 150, 70)
        with col_v2:
            baseline_sbp = st.number_input("Baseline SBP (mmHg)", 80, 200, 120)
        with col_v3:
            baseline_dbp = st.number_input("Baseline DBP (mmHg)", 40, 120, 80)
        with col_v4:
            baseline_spo2 = st.number_input("Baseline SpO2 (%)", 90, 100, 98)
        
        submitted = st.form_submit_button("💾 Save Patient Setup", use_container_width=True)
        
        if submitted:
            st.session_state.patient_data = {
                'patient_id': patient_id,
                'age': age,
                'gender': gender,
                'weight': weight,
                'indication': indication,
                'history': history,
                'medications': medications,
                'protocol': protocol,
                'tilt_angle': tilt_angle,
                'max_duration': max_duration,
                'drug_provocation': drug_provocation,
                'drug_choice': drug_choice if drug_provocation else None,
                'baseline_hr': baseline_hr,
                'baseline_sbp': baseline_sbp,
                'baseline_dbp': baseline_dbp,
                'baseline_spo2': baseline_spo2
            }
            st.success("✅ Patient data saved successfully!")

elif current == 4:  # Performing Test
    st.markdown('<div class="section-header">📊 Performing the Tilt Table Test</div>', unsafe_allow_html=True)
    
    if not st.session_state.patient_data:
        st.warning("⚠️ Please complete Patient Setup first!")
        st.stop()
    
    # Test timeline
    st.subheader("Test Timeline")
    
    phase = st.radio("Current Phase:", 
        ["1. Supine Baseline (5-10 min)", 
         "2. Passive Tilt (15-45 min)",
         "3. Drug Provocation (if needed)",
         "4. Recovery"],
        horizontal=True,
        key="test_phase_selector")
    
    st.markdown("---")
    
    if "Supine" in phase:
        st.info("📋 **Supine Phase Instructions:**")
        st.markdown("""
        - Patient horizontal for 5-10 minutes
        - Record stable baseline HR and BP
        - Ensure IV patency
        - Confirm monitoring systems functional
        - Patient should report any symptoms
        """)
        
        with st.form("supine_vitals"):
            st.subheader("Record Baseline")
            hr = st.number_input("HR (bpm)", 40, 150, 
                               value=st.session_state.patient_data.get('baseline_hr', 70))
            sbp = st.number_input("SBP (mmHg)", 80, 200,
                                value=st.session_state.patient_data.get('baseline_sbp', 120))
            dbp = st.number_input("DBP (mmHg)", 40, 120,
                                value=st.session_state.patient_data.get('baseline_dbp', 80))
            
            if st.form_submit_button("Confirm Baseline & Proceed to Tilt"):
                st.session_state.test_results['baseline_hr'] = hr
                st.session_state.test_results['baseline_sbp'] = sbp
                st.session_state.test_results['baseline_dbp'] = dbp
                st.success("Baseline recorded. Ready to tilt.")
    
    elif "Passive" in phase:
        st.info("📋 **Passive Tilt Phase:**")
        st.markdown(f"""
        - Tilt to {st.session_state.patient_data.get('tilt_angle', 70)}°
        - Duration: Up to {st.session_state.patient_data.get('max_duration', 45)} minutes
        - Record vitals every 3-5 minutes
        - Continuous ECG monitoring
        - STOP immediately if syncope occurs
        """)
        
        # Real-time data entry simulation
        st.subheader("Vital Signs Recording")
        
        with st.form("tilt_vitals"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                time_point = st.number_input("Time at tilt (minutes)", 0.0, 60.0, 5.0, 0.5)
                current_hr = st.number_input("Current HR (bpm)", 30, 200, 75)
            
            with col2:
                current_sbp = st.number_input("Current SBP (mmHg)", 50, 250, 115)
                current_dbp = st.number_input("Current DBP (mmHg)", 30, 150, 75)
            
            with col3:
                symptoms = st.multiselect("Symptoms", [
                    "None", "Lightheadedness", "Nausea", "Sweating", 
                    "Blurred vision", "Palpitations", "Chest discomfort",
                    "Tremulousness", "Complete LOC"
                ])
            
            with col4:
                hr_change = ((current_hr - st.session_state.test_results.get('baseline_hr', 70)) / 
                           st.session_state.test_results.get('baseline_hr', 70) * 100)
                bp_change = ((current_sbp - st.session_state.test_results.get('baseline_sbp', 120)) / 
                           st.session_state.test_results.get('baseline_sbp', 120) * 100)
                
                st.metric("HR Change", f"{hr_change:+.1f}%")
                st.metric("SBP Change", f"{bp_change:+.1f}%")
            
            test_status = st.radio("Test Status:", 
                ["Continue", "Positive - Return to supine", "Negative - Proceed to drugs", "Abort"],
                horizontal=True)
            
            if st.form_submit_button("Record Data Point"):
                if 'data_points' not in st.session_state.test_results:
                    st.session_state.test_results['data_points'] = []
                
                st.session_state.test_results['data_points'].append({
                    'time': time_point,
                    'hr': current_hr,
                    'sbp': current_sbp,
                    'dbp': current_dbp,
                    'symptoms': symptoms
                })
                
                # Auto-analysis
                if "Complete LOC" in symptoms or current_sbp < 70 or current_hr < 40:
                    st.error("🚨 CRITICAL: Syncope/ Severe hypotension detected!")
                    st.session_state.test_results['result'] = "Positive - Vasovagal Syncope"
                    st.session_state.test_results['time_to_symptoms'] = time_point
                
                elif hr_change > 30 and current_sbp < 10:
                    st.warning("⚠️ POTS pattern detected")
                
                st.success(f"Data point at {time_point} min recorded")
    
    elif "Drug" in phase:
        st.info("💊 **Drug Provocation Phase**")
        
        drug = st.session_state.patient_data.get('drug_choice', 'Nitroglycerin')
        
        if drug == "Isoproterenol":
            st.markdown("""
            **Isoproterenol Protocol:**
            - Start 1 mcg/min, titrate to 3 mcg/min
            - Target: HR +20-25% above baseline
            - Tilt 60-70° for additional 15-20 min
            """)
            dose = st.number_input("Current dose (mcg/min)", 0.0, 5.0, 1.0, 0.5)
        else:
            st.markdown("""
            **Nitroglycerin Protocol (Italian):**
            - 300-400 mcg SL in 60-70° position
            - Continue tilt for 15-20 minutes
            """)
            dose = st.number_input("Dose administered (mcg)", 0, 800, 400, 100)
        
        with st.form("drug_phase"):
            st.subheader("Post-Drug Monitoring")
            time_drug = st.number_input("Time post-drug (minutes)", 0, 30, 5)
            hr_drug = st.number_input("HR (bpm)", 30, 200, 85)
            sbp_drug = st.number_input("SBP (mmHg)", 50, 250, 100)
            symptoms_drug = st.multiselect("Symptoms", 
                ["None", "Lightheadedness", "Nausea", "Headache", "Palpitations", "LOC"])
            
            if st.form_submit_button("Record Drug Phase Data"):
                st.session_state.test_results['drug_used'] = drug
                st.session_state.test_results['drug_dose'] = dose
                if "LOC" in symptoms_drug:
                    st.session_state.test_results['drug_response'] = "Positive"
                    st.success("Drug-induced positive response recorded")
                else:
                    st.session_state.test_results['drug_response'] = "Negative"
    
    else:  # Recovery
        st.success("✅ Test Complete - Recovery Phase")
        st.markdown("""
        - Return to supine immediately
        - Monitor until full recovery
        - Document total test duration
        - Record any delayed symptoms
        """)

elif current == 5:  # Analysis & Report
    st.markdown('<div class="section-header">🔍 Analysis & Report Generation</div>', unsafe_allow_html=True)
    
    if not st.session_state.test_results:
        st.warning("⚠️ No test data available. Please complete the test first.")
        st.stop()
    
    # Analysis Section
    st.subheader("Test Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Hemodynamic Patterns")
        
        baseline_hr = st.session_state.test_results.get('baseline_hr', 70)
        baseline_sbp = st.session_state.test_results.get('baseline_sbp', 120)
        
        # Get min values from data points if available
        if 'data_points' in st.session_state.test_results and st.session_state.test_results['data_points']:
            df = pd.DataFrame(st.session_state.test_results['data_points'])
            min_hr = df['hr'].min()
            min_sbp = df['sbp'].min()
            max_hr_drop = baseline_hr - min_hr
            max_bp_drop = baseline_sbp - min_sbp
            time_to_symptoms = df[df['symptoms'].apply(lambda x: 'Complete LOC' in x if isinstance(x, list) else False)]['time'].min() if any('Complete LOC' in str(s) for s in df['symptoms']) else None
        else:
            min_hr = st.number_input("Minimum HR recorded (bpm)", 30, 200, 50)
            min_sbp = st.number_input("Minimum SBP recorded (mmHg)", 40, 250, 80)
            max_hr_drop = baseline_hr - min_hr
            max_bp_drop = baseline_sbp - min_sbp
            time_to_symptoms = st.number_input("Time to symptoms (minutes)", 0.0, 60.0, 10.0)
        
        st.session_state.test_results['min_hr'] = min_hr
        st.session_state.test_results['min_sbp'] = min_sbp
        st.session_state.test_results['time_to_symptoms'] = time_to_symptoms
        
        # Pattern recognition
        st.markdown("### Pattern Analysis")
        
        if max_bp_drop >= 40 and max_hr_drop >= 60:
            pattern = "Mixed (Cardioinhibitory + Vasodepressor)"
            st.error("🚨 Mixed Response: Significant HR and BP drop")
        elif max_hr_drop >= 60 or min_hr < 40:
            pattern = "Cardioinhibitory (Predominant)"
            st.warning("⚠️ Cardioinhibitory Response: Significant bradycardia")
        elif max_bp_drop >= 40:
            pattern = "Vasodepressor (Predominant)"
            st.info("ℹ️ Vasodepressor Response: BP drop without severe bradycardia")
        elif (min_hr - baseline_hr) >= 30 and max_bp_drop < 10:
            pattern = "POTS Pattern"
            st.info("ℹ️ Postural Tachycardia Syndrome pattern")
        else:
            pattern = "Nonspecific/Negative"
            st.info("ℹ️ No clear vasovagal pattern")
        
        st.session_state.test_results['pattern'] = pattern
        
        # Age consideration
        age = st.session_state.patient_data.get('age', 50)
        if age > 60 and "Vasodepressor" in pattern:
            st.markdown("""
            <div class="info-box">
            <strong>Age Consideration:</strong> Older patients more likely to show 
            vasodepressor response rather than cardioinhibitory response.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Final Interpretation")
        
        result_type = st.selectbox("Test Result:", [
            "Positive - Vasovagal Syncope",
            "Positive - Orthostatic Hypotension", 
            "Positive - POTS",
            "Positive - Pseudosyncope",
            "Negative - No abnormality detected",
            "Indeterminate"
        ])
        
        st.session_state.test_results['result'] = result_type
        
        # Interpretation logic
        interpretations = {
            "Positive - Vasovagal Syncope": """
            Delayed accelerating fall in BP with HR changes consistent with 
            vasovagal mechanism. Patient reported symptoms similar to 
            spontaneous episodes.
            """,
            "Positive - Orthostatic Hypotension": """
            Immediate or early (within 3-5 min) sustained drop in SBP ≥20 mmHg 
            or DBP ≥10 mmHg without compensatory tachycardia.
            """,
            "Positive - POTS": """
            Sustained HR increase ≥30 bpm (≥40 bpm if <20 years) within 10 min 
            of tilt without significant BP drop.
            """,
            "Positive - Pseudosyncope": """
            Apparent LOC without significant hemodynamic changes. 
            Consider psychiatric evaluation.
            """,
            "Negative - No abnormality detected": """
            No significant hemodynamic changes during passive or drug phase.
            Consider alternative diagnoses or repeat testing.
            """,
            "Indeterminate": """
            Inconclusive results. Consider prolonged monitoring or alternative testing.
            """
        }
        
        interpretation = st.text_area("Detailed Interpretation", 
                                    value=interpretations.get(result_type, ""),
                                    height=150)
        st.session_state.test_results['interpretation'] = interpretation
        
        # Recommendations
        st.markdown("### Recommendations")
        
        if "Vasovagal" in result_type:
            if "Cardioinhibitory" in pattern:
                rec = """
                - Consider permanent pacemaker if recurrent severe bradycardia/asystole
                - Fluid and salt supplementation
                - Physical counterpressure maneuvers
                - Consider midodrine or fludrocortisone
                """
            else:
                rec = """
                - Fluid and salt supplementation
                - Physical counterpressure maneuvers
                - Consider midodrine, fludrocortisone, or beta-blockers
                - Pacemaker NOT indicated for pure vasodepressor response
                """
        elif "Orthostatic" in result_type:
            rec = """
            - Volume expansion (fluids, salt)
            - Compression stockings/abdominal binder
            - Head-up sleeping position
            - Consider midodrine, droxidopa, or fludrocortisone
            - Review medications (stop offending agents)
            """
        elif "POTS" in result_type:
            rec = """
            - Hydration (2-3L/day) and increased salt intake
            - Compression garments
            - Exercise training (recumbent initially)
            - Consider beta-blockers, ivabradine, or fludrocortisone
            - Evaluate for underlying causes
            """
        else:
            rec = "Further evaluation based on clinical suspicion."
        
        recommendations = st.text_area("Treatment Recommendations", value=rec, height=120)
        st.session_state.test_results['recommendations'] = recommendations
    
    # Report Generation
    st.markdown("---")
    st.subheader("📄 Final Report")
    
    if st.button("Generate Final Report", type="primary"):
        report = generate_report()
        st.text_area("Report Preview", report, height=400)
        
        # Download link
        st.markdown(get_download_link(report, f"Tilt_Test_Report_{st.session_state.patient_data.get('patient_id', 'Unknown')}.txt"), 
                   unsafe_allow_html=True)
        
        # Summary metrics
        st.markdown("### Test Summary")
        cols = st.columns(4)
        metrics = [
            ("Result", st.session_state.test_results.get('result', 'N/A')),
            ("Pattern", st.session_state.test_results.get('pattern', 'N/A')),
            ("Min HR", f"{st.session_state.test_results.get('min_hr', 'N/A')} bpm"),
            ("Min SBP", f"{st.session_state.test_results.get('min_sbp', 'N/A')} mmHg")
        ]
        for col, (label, value) in zip(cols, metrics):
            with col:
                st.metric(label, value)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.8rem;">
    <p>Tilt Table Test Assistant | Clinical Decision Support Tool</p>
    <p>Based on 2018 ESC Guidelines for Syncope & 2017 ACC/AHA/HRS Guideline</p>
    <p><strong>Disclaimer:</strong> This tool is for educational and clinical decision support purposes only. 
    Not a substitute for professional medical judgment.</p>
</div>
""", unsafe_allow_html=True)
