import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==========================================
# PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Mission Karmayogi Dashboard", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    /* Main app background */[data-testid="stAppViewContainer"] { background-color: #f8fafc !important; }
    
    /* Premium KPI Cards */
    [data-testid="stMetric"] {
        background-color: #ffffff !important; border: 1px solid #e2e8f0 !important;
        padding: 15px 20px !important; border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        border-top: 4px solid #2563eb !important; 
    }
    [data-testid="stMetricLabel"] * { color: #475569 !important; font-size: 1.05rem !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] * { color: #000000 !important; font-size: 2.2rem !important; font-weight: 800 !important; }

    /* =========================================
       SIDEBAR & ADMIN PANEL (Modern Dark Navy)
       ========================================= */
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    
    /* FORCE Sidebar Text to be white! */[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,[data-testid="stSidebar"] label, [data-testid="stSidebar"] span { 
        color: #ffffff !important; 
    }
    
    /* Input Box Styling */
    [data-testid="stSidebar"] .stTextInput input { 
        background-color: #1e293b !important; color: #ffffff !important; 
        border: 1px solid #334155 !important; border-radius: 8px !important; padding: 12px !important;
    }[data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Login Button Styling */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important; color: white !important;
        border: none !important; border-radius: 8px !important; padding: 10px !important;
        font-weight: 600 !important; width: 100% !important; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.3s ease !important;
    }[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* Logo / Avatar */
    [data-testid="stSidebar"] img {
        background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 50%;
        backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 10px;
    }

    /* =========================================
       MODERN BEAUTIFUL TABLES
       ========================================= */
    [data-testid="stTable"] {
        background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.05);
        overflow: hidden; border: 1px solid #e2e8f0; margin-bottom: 20px;
    }
    table { width: 100%; border-collapse: collapse; background-color: #ffffff !important; }
    
    th {
        background-color: #f8fafc !important; color: #64748b !important; font-weight: 700 !important; 
        padding: 16px !important; border-bottom: 2px solid #e2e8f0 !important; text-align: left;
        font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;
        white-space: nowrap !important;
    }
    
    td { 
        background-color: #ffffff !important; color: #1e293b !important; padding: 16px !important; 
        border-bottom: 1px solid #f1f5f9 !important; font-weight: 500 !important; font-size: 0.95rem;
    }
    tbody tr { transition: background-color 0.2s ease; }
    tbody tr:hover td { background-color: #f1f5f9 !important; cursor: pointer; }

    /* EVERY HEADER IN THE MAIN DASHBOARD */
    [data-testid="stMainBlock"] h1, [data-testid="stMainBlock"] h2, 
    [data-testid="stMainBlock"] h3,[data-testid="stMainBlock"] h4,
    [data-testid="stMainBlock"] h5,[data-testid="stMainBlock"] h6,
    [data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,[data-testid="stMarkdownContainer"] h4 { 
        color: #0f172a !important; font-weight: 700 !important;
    }
    [data-testid="stMainBlock"] p { color: #334155 !important; }

    /* RADIO BUTTONS & LEGENDS FIX */
    div[role="radiogroup"] label * { color: #0f172a !important; font-weight: 600 !important; }
    .stRadio label { color: #0f172a !important; font-weight: bold !important; }

    /* INFO BUTTONS & POPOVERS */
    div[data-testid="stPopover"] > button { background-color: #f1f5f9 !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; }
    div[data-testid="stPopoverBody"], div[data-testid="stPopoverBody"] div, 
    div[data-testid="stPopoverBody"] span, div[data-testid="stPopoverBody"] p,
    div[data-testid="stPopoverBody"] ul, div[data-testid="stPopoverBody"] li {
        background-color: #ffffff !important; color: #0f172a !important;
    }
    div[data-testid="stPopoverBody"] { border: 2px solid #2563eb !important; box-shadow: 0px 10px 15px rgba(0,0,0,0.1) !important; }

    /* Custom Subtitle 'Box Box' Layout */
    .header-flex { display: flex; flex-wrap: wrap; gap: 15px; margin-top: 5px; margin-bottom: 25px; }
    .feature-box {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px;
        padding: 8px 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); font-weight: 600;
        color: #1e293b !important; font-size: 0.95rem; display: flex; align-items: center; gap: 8px;
    }

    /* =========================================
       TABS FIX 
       ========================================= */
    .stTabs[data-baseweb="tab-list"] { gap: 15px; }
    .stTabs[data-baseweb="tab"] {
        height: 50px; border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px; background-color: #ffffff; border: 1px solid #e2e8f0;
        border-bottom: none; 
    }
    .stTabs [data-baseweb="tab"] p { 
        color: #64748b !important; font-weight: 600 !important; white-space: nowrap !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #eff6ff !important; border-top: 3px solid #2563eb !important; 
    }
    .stTabs[aria-selected="true"] p { color: #2563eb !important; }
    
    /* Force Fullscreen overlays to be white */
    [data-testid="stFullScreenFrame"] { background-color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

ADMIN_PASSWORD = "admin"  
MASTER_FILE = "master_data.csv"

st.title("🎓 Mission Karmayogi Learning Dashboard - Assam")

st.markdown("""
<div class="header-flex">
    <div class="feature-box">👥 Platform Adoption</div>
    <div class="feature-box">📈 User Engagement</div>
    <div class="feature-box">🎯 Learning Effectiveness</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS & INDIAN NUMBER FORMATTER
# ==========================================
def safe_div(a, b):
    return (a / b) if b != 0 else 0

def format_indian(num):
    if pd.isna(num): return "0"
    num = int(float(num))
    s = str(abs(num))
    if len(s) <= 3: res = s
    else:
        res = s[-3:]
        s = s[:-3]
        while len(s) > 0:
            res = s[-2:] + "," + res
            s = s[:-2]
    if num < 0: res = "-" + res
    return res

def flag(x):
    if x < 40: return "🔴 Poor"
    elif x < 70: return "🟡 Moderate"
    else: return "🟢 Good"

@st.cache_data
def load_master_data():
    if not os.path.exists(MASTER_FILE): return None
    df = pd.read_csv(MASTER_FILE)
    df.columns = df.columns.str.strip()
    text_cols =['Ministry', 'Department', 'Mdo Name']
    for col in df.columns:
        if col not in text_cols:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def apply_chart_styling(fig, is_pie=False):
    fig.update_layout(
        template="plotly_white", plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", 
        margin=dict(t=40, b=40, l=10, r=10), 
        font=dict(color="#0f172a", size=13), 
        legend=dict(font=dict(color="#0f172a", size=13)) 
    )
    if not is_pie:
        fig.update_xaxes(showgrid=False, tickfont=dict(color='#0f172a', size=13), title_font=dict(color='#0f172a', size=15, weight='bold'))
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', tickfont=dict(color='#0f172a', size=13), title_font=dict(color='#0f172a', size=15, weight='bold'))
    return fig

# ==========================================
# ADMIN PANEL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
    st.header("🔒 Admin Panel")
    st.markdown("Update the master dataset.")
    pwd_input = st.text_input("Enter Admin Password", type="password")
    
    if pwd_input == ADMIN_PASSWORD:
        st.success("Access Granted!")
        uploaded_file = st.file_uploader("Upload New Data", type=["csv", "xlsx", "xls"])
        if uploaded_file is not None:
            if st.button("💾 Save & Update Dashboard", use_container_width=True):
                if uploaded_file.name.endswith('.csv'): new_df = pd.read_csv(uploaded_file)
                else: new_df = pd.read_excel(uploaded_file)
                new_df.to_csv(MASTER_FILE, index=False)
                st.cache_data.clear()
                st.rerun()

# ==========================================
# MAIN DASHBOARD 
# ==========================================
df = load_master_data()

if df is not None:
    df_dept = df.groupby('Department').sum(numeric_only=True).reset_index()

    # 1. EXECUTIVE SUMMARY (TOP LEVEL KPIs)
    tot_onboarded = df['Onboarded'].sum()
    tot_active = df['Active'].sum()
    tot_enrol = df['Total Enrolments'].sum()
    tot_comp = df['Total Completions'].sum()
    tot_hours = df['Total Learning Hours'].sum()
    tot_attempt = df['Course Assessments Attempted'].sum()
    tot_pass = df['Course Assessments Passed'].sum()

    activation_rate = safe_div(tot_active, tot_onboarded) * 100
    overall_comp_rate = safe_div(tot_comp, tot_enrol) * 100
    pass_rate = safe_div(tot_pass, tot_attempt) * 100
    avg_hours_per_active = safe_div(tot_hours, tot_active)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Onboarded", format_indian(tot_onboarded))
    col2.metric("🟢 Total Active", format_indian(tot_active))
    col3.metric("📚 Total Enrolments", format_indian(tot_enrol))
    col4.metric("🏆 Total Completions", format_indian(tot_comp))
    
    st.markdown("<br>", unsafe_allow_html=True) 

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("⚡ Activation Rate", f"{activation_rate:.1f}%")
    col6.metric("✅ Overall Completion Rate", f"{overall_comp_rate:.1f}%")
    col7.metric("🎯 Assessment Pass Rate", f"{pass_rate:.1f}%")
    col8.metric("⏱️ Avg Hours / Active User", f"{avg_hours_per_active:.1f} hrs")

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # TABS CREATION
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Adoption & Activity", "📉 Learning Funnel & Engagement", 
        "🎯 Performance Quality", "🏢 MDO Deep Dive"
    ])

    # ==========================================
    # TAB 1: ADOPTION & ACTIVITY
    # ==========================================
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        colA, colB = st.columns([2, 1], gap="large")
        
        with colA:
            st.markdown("#### 🏢 Department Adoption")
            with st.popover("ℹ️ Info"): st.markdown("**What this shows:** The absolute number of users onboarded vs. those who have actively used the platform.")
            
            view_mode = st.radio("Select View:",["Top 10 Departments", "Bottom 10 Departments"], horizontal=True, label_visibility="collapsed")
            valid_depts = df_dept[df_dept['Onboarded'] > 0]
            
            if view_mode == "Top 10 Departments": chart_data = valid_depts.nlargest(10, 'Onboarded')
            else: chart_data = valid_depts.nsmallest(10, 'Onboarded')
                
            chart_data_melted = chart_data.melt(id_vars='Department', value_vars=['Onboarded', 'Active'], var_name='Status', value_name='Users')
            chart_data_melted['Users_Formatted'] = chart_data_melted['Users'].apply(format_indian)
            
            fig_adopt = px.bar(
                chart_data_melted, x='Department', y='Users', color='Status', barmode='group',
                color_discrete_map={'Onboarded': '#94a3b8', 'Active': '#2563eb'}, text='Users_Formatted'
            )
            fig_adopt = apply_chart_styling(fig_adopt)
            fig_adopt.update_traces(textfont=dict(color='#0f172a', weight='bold'), hovertemplate='<b>%{x}</b><br>Status: %{color}<br>Users: %{text}<extra></extra>')
            fig_adopt.update_layout(xaxis_title="", yaxis_title="Number of Users", legend_title="", legend=dict(yanchor="top", y=1.1, xanchor="right", x=1, orientation="h"))
            st.plotly_chart(fig_adopt, use_container_width=True, theme=None)
            
        with colB:
            st.markdown("#### 📊 Activity Distribution")
            with st.popover("ℹ️ Info"): st.markdown("**What this shows:** Categorizes departments into three health tiers based on Activation Rate `(Active ÷ Onboarded)`:\n- 🟢 **High**: > 75%\n- 🟡 **Medium**: 40% - 75%\n- 🔴 **Low**: < 40%")
            
            df_dept['Activity Rate'] = (df_dept['Active'] / df_dept['Onboarded']) * 100
            conditions =[(df_dept['Activity Rate'] >= 75), (df_dept['Activity Rate'] >= 40) & (df_dept['Activity Rate'] < 75), (df_dept['Activity Rate'] < 40)]
            choices =['High (>75%)', 'Medium (40-75%)', 'Low (<40%)']
            df_dept['Activity Tier'] = np.select(conditions, choices, default='Unknown')
            
            tier_counts = df_dept['Activity Tier'].value_counts().reset_index()
            tier_counts.columns =['Tier', 'Count']
            
            fig_donut = px.pie(
                tier_counts, names='Tier', values='Count', hole=0.6,
                color='Tier', color_discrete_map={'High (>75%)': '#10b981', 'Medium (40-75%)': '#fbbf24', 'Low (<40%)': '#ef4444'}
            )
            fig_donut = apply_chart_styling(fig_donut, is_pie=True)
            fig_donut.update_traces(textposition='inside', textinfo='percent', insidetextfont=dict(color='white', weight='bold'))
            fig_donut.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
            st.plotly_chart(fig_donut, use_container_width=True, theme=None)

    # ==========================================
    # TAB 2: LEARNING FUNNEL & ENGAGEMENT
    # ==========================================
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        colA, colB = st.columns([1, 2], gap="large")
        
        with colA:
            st.markdown("#### 🌪️ Platform Funnel")
            with st.popover("ℹ️ Info"): st.markdown("**What this shows:** The user journey across the entire platform. Identifies where drop-offs occur.")
            
            funnel_stages =['Enrolments', 'Completions', 'Assessed', 'Passed']
            funnel_values =[tot_enrol, tot_comp, tot_attempt, tot_pass]
            
            funnel_text =[]
            for i, val in enumerate(funnel_values):
                pct = (val / funnel_values[0]) * 100 if funnel_values[0] > 0 else 0
                if i == 0: funnel_text.append(f"{format_indian(val)}")
                else: funnel_text.append(f"{format_indian(val)} ({pct:.1f}%)")

            fig_funnel = go.Figure(go.Funnel(
                y = funnel_stages, x = funnel_values,
                textinfo = "text", text = funnel_text,
                marker = {"color":["#1e3a8a", "#2563eb", "#60a5fa", "#bae6fd"]}
            ))
            fig_funnel = apply_chart_styling(fig_funnel, is_pie=True)
            fig_funnel.update_yaxes(tickfont=dict(color='#0f172a', size=14, weight='bold'))
            fig_funnel.update_layout(showlegend=False)
            st.plotly_chart(fig_funnel, use_container_width=True, theme=None)
            
        with colB:
            st.markdown("#### 📉 Enrolments vs Completions")
            with st.popover("ℹ️ Info"): st.markdown("**What this shows:** Compares total course enrolments against actual completions for the Top 15 departments.")
            
            top_eng = df_dept.nlargest(15, 'Total Enrolments')
            eng_melted = top_eng.melt(id_vars='Department', value_vars=['Total Enrolments', 'Total Completions'], var_name='Metric', value_name='Count')
            eng_melted['Count_Formatted'] = eng_melted['Count'].apply(format_indian)
            
            fig_eng = px.bar(
                eng_melted, x='Department', y='Count', color='Metric', barmode='group',
                color_discrete_map={'Total Enrolments': '#cbd5e1', 'Total Completions': '#0ea5e9'}, text='Count_Formatted'
            )
            fig_eng = apply_chart_styling(fig_eng)
            fig_eng.update_traces(textfont=dict(color='#0f172a', weight='bold'), hovertemplate='<b>%{x}</b><br>Metric: %{color}<br>Count: %{text}<extra></extra>')
            fig_eng.update_layout(xaxis_title="", yaxis_title="Courses", legend_title="", legend=dict(yanchor="top", y=1.1, xanchor="right", x=1, orientation="h"))
            st.plotly_chart(fig_eng, use_container_width=True, theme=None)

        st.markdown("---")
        st.markdown("#### 🔄 Stage-by-Stage Conversion Rates")
        with st.popover("ℹ️ Info"): st.markdown("**What this shows:** The specific success percentages between each funnel stage for the entire state.")
        
        conversion_table = pd.DataFrame({
            'Stage Transition':['Enrolment → Completion', 'Completion → Attempt', 'Attempt → Pass', 'Overall (Enrolment → Pass)'],
            'Conversion %':[safe_div(tot_comp, tot_enrol) * 100, safe_div(tot_attempt, tot_comp) * 100, safe_div(tot_pass, tot_attempt) * 100, safe_div(tot_pass, tot_enrol) * 100]
        })

        conversion_table['Performance'] = conversion_table['Conversion %'].apply(flag)
        display_table = conversion_table.copy()
        display_table['Conversion %'] = display_table['Conversion %'].round(2).astype(str) + "%"
        
        st.table(display_table.style.hide(axis="index"))

        # UPDATED: Multi-colored Vertical Bar Chart
        fig_conv = px.bar(
            conversion_table, x='Stage Transition', y='Conversion %', 
            color='Stage Transition', # Map color to categories
            color_discrete_sequence=['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'], # Blue, Purple, Orange, Teal
            text=conversion_table['Conversion %'].apply(lambda x: f"{x:.2f}%")
        )
        fig_conv = apply_chart_styling(fig_conv)
        fig_conv.update_traces(textposition='outside', marker_line_width=0, textfont=dict(color='#0f172a', size=14, weight='bold'))
        # Hide legend to keep it clean
        fig_conv.update_layout(height=400, xaxis_title="", yaxis_title="Conversion %", showlegend=False) 
        st.plotly_chart(fig_conv, use_container_width=True, theme=None)

    # ==========================================
    # TAB 3: PERFORMANCE QUALITY
    # ==========================================
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        colA, colB = st.columns(2, gap="large")
        
        df_dept['Pass %'] = df_dept.apply(lambda x: safe_div(x['Course Assessments Passed'], x['Course Assessments Attempted']) * 100, axis=1)
        valid_assessments = df_dept[df_dept['Course Assessments Attempted'] >= 10].copy()
        
        with colA:
            st.markdown("#### ✅ Assessment Effectiveness")
            with st.popover("ℹ️ Info"): st.markdown("**What this shows:** Top 15 Departments by Pass % (Minimum 10 attempts to exclude outliers).")
            
            top_pass = valid_assessments.nlargest(15, 'Pass %').sort_values('Pass %', ascending=True)
            
            # UPDATED: 15 Beautiful distinct modern colors for the horizontal bars
            distinct_colors =['#f43f5e', '#ec4899', '#d946ef', '#a855f7', '#8b5cf6', 
                               '#6366f1', '#3b82f6', '#0ea5e9', '#06b6d4', '#14b8a6', 
                               '#10b981', '#22c55e', '#84cc16', '#eab308', '#f97316']

            fig_pass = px.bar(
                top_pass, x='Pass %', y='Department', orientation='h', 
                color='Department', # Map color to the distinct department
                color_discrete_sequence=distinct_colors, # Use the modern color list
                text=top_pass['Pass %'].apply(lambda x: f"{x:.1f}%")
            )
            fig_pass = apply_chart_styling(fig_pass)
            fig_pass.update_traces(textposition='outside', textfont=dict(color='#0f172a', weight='bold'))
            fig_pass.update_layout(showlegend=False, yaxis_title="", height=550) # Hide redundant legend
            st.plotly_chart(fig_pass, use_container_width=True, theme=None)
            
        with colB:
            st.markdown("#### 🧠 The Struggle Matrix")
            with st.popover("ℹ️ Info"): st.markdown("**What this shows:** Quadrant analysis of Effort (Hours) vs Results (Pass %).")
            
            valid_assessments['Avg Hours/Active'] = valid_assessments.apply(lambda x: safe_div(x['Total Learning Hours'], x['Active']), axis=1)
            q95 = valid_assessments['Avg Hours/Active'].quantile(0.95)
            matrix_data = valid_assessments[valid_assessments['Avg Hours/Active'] <= q95]
            
            fig_scatter = px.scatter(matrix_data, x='Avg Hours/Active', y='Pass %', hover_name='Department', size='Active', color='Pass %', color_continuous_scale='RdYlGn', size_max=40)
            fig_scatter = apply_chart_styling(fig_scatter)
            
            med_x = matrix_data['Avg Hours/Active'].median()
            med_y = matrix_data['Pass %'].median()
            fig_scatter.add_vline(x=med_x, line_dash="dash", line_color="#94a3b8")
            fig_scatter.add_hline(y=med_y, line_dash="dash", line_color="#94a3b8")
            
            fig_scatter.add_annotation(x=med_x*0.5, y=med_y + (100-med_y)*0.5, text="High Efficiency", showarrow=False, font=dict(color="#10b981", size=13, weight="bold"), opacity=1)
            fig_scatter.add_annotation(x=med_x*1.5, y=med_y + (100-med_y)*0.5, text="Hard Workers", showarrow=False, font=dict(color="#3b82f6", size=13, weight="bold"), opacity=1)
            fig_scatter.add_annotation(x=med_x*1.5, y=med_y*0.5, text="Struggling", showarrow=False, font=dict(color="#ef4444", size=13, weight="bold"), opacity=1)
            fig_scatter.add_annotation(x=med_x*0.5, y=med_y*0.5, text="Low Engagement", showarrow=False, font=dict(color="#f59e0b", size=13, weight="bold"), opacity=1)

            fig_scatter.update_layout(coloraxis_showscale=False, height=550)
            st.plotly_chart(fig_scatter, use_container_width=True, theme=None)

    # ==========================================
    # TAB 4: MDO DEEP DIVE
    # ==========================================
    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🔬 MDO Deep Dive Explorer")
        with st.popover("ℹ️ Info"): st.markdown("**What this shows:** Select a Department, and then drill down into a specific Sub-department (MDO) to see their exact conversion rates.")
            
        all_depts = sorted(df['Department'].dropna().unique().tolist())
        selected_dept = st.selectbox("1. Select a Department:", all_depts)
        
        mdo_df = df[df['Department'] == selected_dept].copy()
        mdo_df['Activation Rate %'] = mdo_df.apply(lambda x: safe_div(x['Active'], x['Onboarded']) * 100, axis=1)
        mdo_df['Pass Rate %'] = mdo_df.apply(lambda x: safe_div(x['Course Assessments Passed'], x['Course Assessments Attempted']) * 100, axis=1)
        
        display_cols =['Mdo Name', 'Onboarded', 'Active', 'Activation Rate %', 'Total Enrolments', 'Total Completions', 'Total Learning Hours', 'Pass Rate %']
        
        try:
            styled_df = mdo_df[display_cols].style.hide(axis="index").background_gradient(
                cmap='Blues', subset=['Activation Rate %', 'Pass Rate %']
            ).format({
                'Onboarded': format_indian, 
                'Active': format_indian, 
                'Total Enrolments': format_indian, 
                'Total Completions': format_indian, 
                'Total Learning Hours': format_indian,
                'Activation Rate %': "{:.1f}%",
                'Pass Rate %': "{:.1f}%"
            })
            st.table(styled_df)
        except Exception:
            st.table(mdo_df[display_cols].style.hide(axis="index"))

        # --- THE NEW MDO DROPDOWN ---
        st.divider()
        st.markdown(f"#### 🎯 Funnel Analysis Drill-down")
        
        mdo_list =["All Sub-departments (Aggregate)"] + sorted(mdo_df['Mdo Name'].dropna().unique().tolist())
        selected_mdo = st.selectbox(f"2. Select a specific Sub-department (MDO) within {selected_dept}:", mdo_list)
        
        if selected_mdo == "All Sub-departments (Aggregate)":
            target_df = mdo_df
            target_name = selected_dept
        else:
            target_df = mdo_df[mdo_df['Mdo Name'] == selected_mdo]
            target_name = selected_mdo
            
        # Calculate specific totals for target
        target_enrol = target_df['Total Enrolments'].sum()
        target_comp = target_df['Total Completions'].sum()
        target_attempt = target_df['Course Assessments Attempted'].sum()
        target_pass = target_df['Course Assessments Passed'].sum()

        target_conv_table = pd.DataFrame({
            'Stage Transition':['Enrolment → Completion', 'Completion → Attempt', 'Attempt → Pass', 'Overall (Enrolment → Pass)'],
            'Conversion %':[
                safe_div(target_comp, target_enrol) * 100, 
                safe_div(target_attempt, target_comp) * 100, 
                safe_div(target_pass, target_attempt) * 100, 
                safe_div(target_pass, target_enrol) * 100
            ]
        })

        target_conv_table['Performance'] = target_conv_table['Conversion %'].apply(flag)
        target_display = target_conv_table.copy()
        target_display['Conversion %'] = target_display['Conversion %'].round(2).astype(str) + "%"
        
        st.markdown(f"**Conversion Rates for: {target_name}**")
        st.table(target_display.style.hide(axis="index"))

        # UPDATED: Multi-colored Vertical Bar Chart for the Drill Down
        fig_target_conv = px.bar(
            target_conv_table, x='Stage Transition', y='Conversion %', 
            color='Stage Transition',
            color_discrete_sequence=['#0ea5e9', '#6366f1', '#ec4899', '#14b8a6'], # Sky Blue, Indigo, Pink, Teal
            text=target_conv_table['Conversion %'].apply(lambda x: f"{x:.2f}%")
        )
        fig_target_conv = apply_chart_styling(fig_target_conv)
        fig_target_conv.update_traces(textposition='outside', marker_line_width=0, textfont=dict(color='#0f172a', size=14, weight='bold'))
        fig_target_conv.update_layout(height=400, xaxis_title="", yaxis_title="Conversion %", showlegend=False)
        st.plotly_chart(fig_target_conv, use_container_width=True, theme=None)

else:
    st.info("👋 Welcome! The dashboard is currently empty. Please open the Sidebar on the left, log in, and upload the master data file.")
