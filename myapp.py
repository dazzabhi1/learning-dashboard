import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==========================================
# PAGE CONFIGURATION & SECRETS
# ==========================================
st.set_page_config(page_title="Learning Analytics Dashboard", page_icon="📊", layout="wide")

ADMIN_PASSWORD = "admin"  # Changed to 'admin' for easier testing
MASTER_FILE = "master_data.csv"

st.title("📊 Enterprise Learning Dashboard")

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def safe_div(a, b):
    return (a / b) if b != 0 else 0

@st.cache_data
def load_master_data():
    if not os.path.exists(MASTER_FILE):
        return None
    
    df = pd.read_csv(MASTER_FILE)
    
    # Strip whitespace from columns
    df.columns = df.columns.str.strip()
    text_cols = ['Ministry', 'Department', 'Mdo Name']
    
    for col in df.columns:
        if col not in text_cols:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

# ==========================================
# ADMIN PANEL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("🔒 Admin Panel")
    st.markdown("Update the dashboard data here.")
    
    pwd_input = st.text_input("Enter Admin Password", type="password")
    
    if pwd_input == ADMIN_PASSWORD:
        st.success("Access Granted!")
        uploaded_file = st.file_uploader("Upload New Data (CSV or Excel)", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            # ADDED A BUTTON HERE TO PREVENT INFINITE REFRESH LOOPS
            if st.button("💾 Save & Update Dashboard"):
                if uploaded_file.name.endswith('.csv'):
                    new_df = pd.read_csv(uploaded_file)
                else:
                    new_df = pd.read_excel(uploaded_file)
                    
                # Save it permanently
                new_df.to_csv(MASTER_FILE, index=False)
                
                # Clear cache and refresh
                st.cache_data.clear()
                st.rerun()

# ==========================================
# MAIN DASHBOARD (VISIBLE TO EVERYONE)
# ==========================================
df = load_master_data()

if df is not None:
    # Pre-aggregate department level data for charts
    df_dept = df.groupby('Department').sum(numeric_only=True).reset_index()

    # ==========================================
    # 1. EXECUTIVE SUMMARY (TOP LEVEL KPIs)
    # ==========================================
    st.markdown("### 📈 Executive Summary")
    
    # Raw Totals
    tot_onboarded = df['Onboarded'].sum()
    tot_active = df['Active'].sum()
    tot_user_comp = df['User Completions'].sum()
    tot_enrol = df['Total Enrolments'].sum()
    tot_comp = df['Total Completions'].sum()
    tot_hours = df['Total Learning Hours'].sum()
    tot_attempt = df['Course Assessments Attempted'].sum()
    tot_pass = df['Course Assessments Passed'].sum()

    # Derived KPIs
    activation_rate = safe_div(tot_active, tot_onboarded) * 100
    overall_comp_rate = safe_div(tot_comp, tot_enrol) * 100
    pass_rate = safe_div(tot_pass, tot_attempt) * 100
    avg_hours_per_active = safe_div(tot_hours, tot_active)

    # Display Metrics in 2 rows
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Onboarded", f"{tot_onboarded:,.0f}")
    col2.metric("🟢 Total Active", f"{tot_active:,.0f}")
    col3.metric("📚 Total Enrolments", f"{tot_enrol:,.0f}")
    col4.metric("🏆 Total Completions", f"{tot_comp:,.0f}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("⚡ Activation Rate", f"{activation_rate:.1f}%")
    col6.metric("✅ Overall Completion Rate", f"{overall_comp_rate:.1f}%")
    col7.metric("🎯 Assessment Pass Rate", f"{pass_rate:.1f}%")
    col8.metric("⏱️ Avg Hours / Active User", f"{avg_hours_per_active:.1f} hrs")

    st.divider()

    # ==========================================
    # TABS CREATION
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Adoption & Activity", 
        "📉 Learning Funnel & Engagement", 
        "🎯 Performance Quality", 
        "🏢 MDO Deep Dive"
    ])

    # ==========================================
    # TAB 1: ADOPTION & ACTIVITY
    # ==========================================
    with tab1:
        st.markdown("#### Department Adoption")
        
        colA, colB = st.columns([2, 1])
        
        with colA:
            # Toggle for Top 10 vs Bottom 10
            view_mode = st.radio("Select View:", ["Top 10 Departments", "Bottom 10 Departments"], horizontal=True)
            
            valid_depts = df_dept[df_dept['Onboarded'] > 0]
            
            if view_mode == "Top 10 Departments":
                chart_data = valid_depts.nlargest(10, 'Onboarded')
            else:
                chart_data = valid_depts.nsmallest(10, 'Onboarded')
                
            chart_data_melted = chart_data.melt(
                id_vars='Department', value_vars=['Onboarded', 'Active'], 
                var_name='Status', value_name='Users'
            )
            
            fig_adopt = px.bar(
                chart_data_melted, x='Department', y='Users', color='Status', barmode='group',
                color_discrete_map={'Onboarded': '#94a3b8', 'Active': '#2563eb'},
                title=f"{view_mode}: Onboarded vs Active", text_auto='.2s'
            )
            st.plotly_chart(fig_adopt, use_container_width=True)
            
        with colB:
            st.markdown("#### User Activity Distribution")
            
            st.info("💡 **How this is calculated:**\nIt measures the **Activation Rate** `(Active ÷ Onboarded)` for every single department, and groups them into 3 health tiers (High, Medium, Poor).")
            
            df_dept['Activity Rate'] = (df_dept['Active'] / df_dept['Onboarded']) * 100
            
            conditions = [
                (df_dept['Activity Rate'] >= 75),
                (df_dept['Activity Rate'] >= 40) & (df_dept['Activity Rate'] < 75),
                (df_dept['Activity Rate'] < 40)
            ]
            choices = ['High (>75%)', 'Medium (40-75%)', 'Low (<40%)']
            df_dept['Activity Tier'] = np.select(conditions, choices, default='Unknown')
            
            tier_counts = df_dept['Activity Tier'].value_counts().reset_index()
            tier_counts.columns = ['Tier', 'Count']
            
            fig_donut = px.pie(
                tier_counts, names='Tier', values='Count', hole=0.5,
                color='Tier', color_discrete_map={'High (>75%)': '#10b981', 'Medium (40-75%)': '#fbbf24', 'Low (<40%)': '#ef4444'}
            )
            fig_donut.update_layout(margin=dict(t=10, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)

    # ==========================================
    # TAB 2: LEARNING FUNNEL & ENGAGEMENT
    # ==========================================
    with tab2:
        colA, colB = st.columns([1, 2])
        
        with colA:
            st.markdown("#### Learning Funnel")
            funnel_stages = ['Enrolments', 'Completions', 'Assessments Attempted', 'Assessments Passed']
            funnel_values = [tot_enrol, tot_comp, tot_attempt, tot_pass]
            
            fig_funnel = go.Figure(go.Funnel(
                y = funnel_stages, x = funnel_values,
                textinfo = "value+percent initial",
                marker = {"color": ["#3b82f6", "#6366f1", "#8b5cf6", "#a855f7"]}
            ))
            fig_funnel.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_funnel, use_container_width=True)
            
        with colB:
            st.markdown("#### Engagement: Enrolments vs Completions")
            top_eng = df_dept.nlargest(15, 'Total Enrolments')
            eng_melted = top_eng.melt(
                id_vars='Department', value_vars=['Total Enrolments', 'Total Completions'], 
                var_name='Metric', value_name='Count'
            )
            
            fig_eng = px.bar(
                eng_melted, x='Department', y='Count', color='Metric', barmode='group',
                color_discrete_map={'Total Enrolments': '#cbd5e1', 'Total Completions': '#0ea5e9'},
                text_auto='.2s'
            )
            fig_eng.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_eng, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Conversion Rates Across Learning Funnel")
        
        conversion_table = pd.DataFrame({
            'Stage Transition': [
                'Enrolment → Completion', 
                'Completion → Attempt', 
                'Attempt → Pass', 
                'Overall (Enrolment → Pass)'
            ],
            'Conversion %': [
                safe_div(tot_comp, tot_enrol) * 100,
                safe_div(tot_attempt, tot_comp) * 100,
                safe_div(tot_pass, tot_attempt) * 100,
                safe_div(tot_pass, tot_enrol) * 100
            ]
        })

        def flag(x):
            if x < 40:
                return "🔴 Poor"
            elif x < 70:
                return "🟡 Moderate"
            else:
                return "🟢 Good"

        conversion_table['Performance'] = conversion_table['Conversion %'].apply(flag)
        
        display_table = conversion_table.copy()
        display_table['Conversion %'] = display_table['Conversion %'].round(2).astype(str) + "%"
        st.dataframe(display_table, use_container_width=True, hide_index=True)

        fig_conv = px.bar(
            conversion_table, 
            x='Stage Transition', 
            y='Conversion %',
            color='Conversion %', 
            color_continuous_scale='Teal',
            text=conversion_table['Conversion %'].apply(lambda x: f"{x:.2f}%")
        )
        fig_conv.update_traces(textposition='outside')
        fig_conv.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=450)
        st.plotly_chart(fig_conv, use_container_width=True)

    # ==========================================
    # TAB 3: PERFORMANCE QUALITY
    # ==========================================
    with tab3:
        colA, colB = st.columns(2)
        
        df_dept['Pass %'] = df_dept.apply(lambda x: safe_div(x['Course Assessments Passed'], x['Course Assessments Attempted']) * 100, axis=1)
        valid_assessments = df_dept[df_dept['Course Assessments Attempted'] >= 10].copy()
        
        with colA:
            st.markdown("#### Assessment Effectiveness")
            st.caption("Top 15 Departments by Pass % (Min. 10 attempts)")
            
            top_pass = valid_assessments.nlargest(15, 'Pass %').sort_values('Pass %', ascending=True)
            
            fig_pass = px.bar(
                top_pass, x='Pass %', y='Department', orientation='h',
                color='Pass %', color_continuous_scale='Teal',
                text=top_pass['Pass %'].apply(lambda x: f"{x:.1f}%")
            )
            fig_pass.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_pass, use_container_width=True)
            
        with colB:
            st.markdown("#### The Struggle Matrix")
            st.caption("Are users spending a lot of time but failing? (Avg Hours vs Pass %)")
            
            valid_assessments['Avg Hours/Active'] = valid_assessments.apply(lambda x: safe_div(x['Total Learning Hours'], x['Active']), axis=1)
            
            q95 = valid_assessments['Avg Hours/Active'].quantile(0.95)
            matrix_data = valid_assessments[valid_assessments['Avg Hours/Active'] <= q95]
            
            fig_scatter = px.scatter(
                matrix_data, x='Avg Hours/Active', y='Pass %', 
                hover_name='Department', size='Active', color='Pass %',
                color_continuous_scale='RdYlGn', size_max=40
            )
            
            med_x = matrix_data['Avg Hours/Active'].median()
            med_y = matrix_data['Pass %'].median()
            fig_scatter.add_vline(x=med_x, line_dash="dash", line_color="gray", opacity=0.5)
            fig_scatter.add_hline(y=med_y, line_dash="dash", line_color="gray", opacity=0.5)
            
            st.plotly_chart(fig_scatter, use_container_width=True)

    # ==========================================
    # TAB 4: MDO DEEP DIVE
    # ==========================================
    with tab4:
        st.markdown("#### Drill-down: Department to MDO Level")
        st.caption("Select a Department to see the breakdown of individual MDOs (Sub-departments)")
        
        all_depts = sorted(df['Department'].dropna().unique().tolist())
        selected_dept = st.selectbox("Select Department:", all_depts)
        
        mdo_df = df[df['Department'] == selected_dept].copy()
        
        mdo_df['Activation Rate %'] = mdo_df.apply(lambda x: safe_div(x['Active'], x['Onboarded']) * 100, axis=1).round(1)
        mdo_df['Pass Rate %'] = mdo_df.apply(lambda x: safe_div(x['Course Assessments Passed'], x['Course Assessments Attempted']) * 100, axis=1).round(1)
        
        display_cols = [
            'Mdo Name', 'Onboarded', 'Active', 'Activation Rate %', 
            'Total Enrolments', 'Total Completions', 'Total Learning Hours', 'Pass Rate %'
        ]
        
        st.dataframe(
            mdo_df[display_cols],
            use_container_width=True,
            hide_index=True
        )

else:
    st.info("👋 Welcome! The dashboard is currently empty. If you are the Administrator, please log in on the left and upload the data file.")
