import streamlit as st
import pandas as pd

st.set_page_config(page_title="5-Way Cricket Matchup Engine", layout="wide")

@st.cache_data
def load_data():
    # Load ONLY the columns needed for matchup analytics to prevent Out of Memory (OOM)
    required_cols = [
        'format', 'start_date', 'innings', 'ball', 
        'batter', 'bowler', 'runs_off_bat', 'is_wicket', 'wicket_type'
    ]
    
    # Read parquet with specific columns
    df = pd.read_parquet('cricket_data.parquet', columns=required_cols)
    
    # Optimize memory: Convert heavy string columns to Categorical types
    categorical_cols = ['format', 'batter', 'bowler', 'wicket_type']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    # Downcast numerical columns to save up to 80% RAM
    df['runs_off_bat'] = df['runs_off_bat'].astype('int8')
    df['is_wicket'] = df['is_wicket'].astype('int8')
    df['innings'] = df['innings'].astype('int8')
    df['ball'] = df['ball'].astype('float32')
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading parquet data: {e}")
    st.stop()

st.title("🏏 5-Way Cricket Player Matchup Engine")
st.write("Query data across individual formats (**IPL, T20I, ODI, Test**) or choose **All** to aggregate whole-career records.")

st.sidebar.header("⚙️ Select Parameters")
selected_format = st.sidebar.selectbox("1. Select Matchup Mode", ["All", "IPL", "T20I", "ODI", "Test"])

# 1. Filter dataset by the selected format first
if selected_format == "All":
    format_df = df
else:
    format_df = df[df['format'] == selected_format]

# 2. Get available batters for this specific format
available_batters = sorted(format_df['batter'].dropna().unique().astype(str).tolist())

default_bat_idx = available_batters.index("Virat Kohli") if "Virat Kohli" in available_batters else 0
selected_batter = st.sidebar.selectbox("2. Select Batter", available_batters, index=default_bat_idx)

# 3. DYNAMIC FILTERING: Get ONLY the bowlers faced by this selected batter in this format
matchup_subset = format_df[format_df['batter'] == selected_batter]
available_bowlers = sorted(matchup_subset['bowler'].dropna().unique().astype(str).tolist())

default_bowl_idx = available_bowlers.index("Jasprit Bumrah") if "Jasprit Bumrah" in available_bowlers else 0
selected_bowler = st.sidebar.selectbox("3. Select Bowler (Only Faced Bowlers Shown)", available_bowlers, index=default_bowl_idx)

if st.sidebar.button("⚡ Run Deep Matchup", type="primary"):
    # Filter the already filtered batter data for the selected bowler
    matchup_df = matchup_subset[matchup_subset['bowler'] == selected_bowler]
    
    if matchup_df.empty:
        st.warning(f"⚠️ **{selected_batter}** has never faced **{selected_bowler}** in format: **{selected_format}**.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            total_balls = len(matchup_df)
            total_runs = int(matchup_df['runs_off_bat'].sum())
            total_wickets = int(matchup_df['is_wicket'].sum())
            
            strike_rate = (total_runs / total_balls) * 100 if total_balls > 0 else 0.0
            wicket_prob = (total_wickets / total_balls) * 100 if total_balls > 0 else 0.0
            dot_balls = len(matchup_df[matchup_df['runs_off_bat'] == 0])
            dot_ball_pct = (dot_balls / total_balls) * 100 if total_balls > 0 else 0.0
            
            st.markdown(f"### 📊 Matchup Stats")
            stats_data = {
                "Metric": [
                    "🎯 Total Deliveries Faced",
                    "📈 Runs Scored off Bowler",
                    "☝️ Times Dismissed (Wickets)",
                    "⚡ Head-to-Head Strike Rate",
                    "🔴 Dot Ball Percentage",
                    "☠️ Wicket Probability (Per Ball)"
                ],
                "Value": [
                    f"{total_balls} balls",
                    f"{total_runs} runs",
                    f"{total_wickets}",
                    f"{strike_rate:.2f}",
                    f"{dot_ball_pct:.2f}%",
                    f"{wicket_prob:.2f}%"
                ]
            }
            st.table(pd.DataFrame(stats_data))
            
        with col2:
            st.markdown("### 📋 Historical Ball-by-Ball Timeline")
            sample_logs = matchup_df[['format', 'start_date', 'innings', 'ball', 'runs_off_bat', 'wicket_type']].head(20)
            st.dataframe(sample_logs, use_container_width=True)
