import gradio as gr
import pandas as pd

# Load the dataset
df = pd.read_csv('cricket_data.csv')

# Pre-calculate unique lists for fast dropdown switching
player_cache = {
    "All": {
        "batters": sorted(df['batter'].dropna().unique().tolist()),
        "bowlers": sorted(df['bowler'].dropna().unique().tolist())
    }
}

for fmt in ['IPL', 'T20I', 'ODI', 'Test']:
    fmt_df = df[df['format'] == fmt]
    player_cache[fmt] = {
        "batters": sorted(fmt_df['batter'].dropna().unique().tolist()),
        "bowlers": sorted(fmt_df['bowler'].dropna().unique().tolist())
    }

def analyze_matchup(selected_format, selected_batter, selected_bowler):
    if selected_format == "All":
        matchup_df = df[(df['batter'] == selected_batter) & (df['bowler'] == selected_bowler)]
    else:
        matchup_df = df[
            (df['format'] == selected_format) & 
            (df['batter'] == selected_batter) & 
            (df['bowler'] == selected_bowler)
        ]
    
    if matchup_df.empty:
        error_md = f"""
        ### ⚠️ No Direct Head-to-Head Record Found
        **{selected_batter}** has never faced **{selected_bowler}** in the chosen format: **{selected_format}**.
        """
        return error_md, pd.DataFrame()

    total_balls = len(matchup_df)
    total_runs = int(matchup_df['runs_off_bat'].sum())
    total_wickets = int(matchup_df['is_wicket'].sum())
    
    strike_rate = (total_runs / total_balls) * 100 if total_balls > 0 else 0.0
    wicket_prob = (total_wickets / total_balls) * 100 if total_balls > 0 else 0.0
    dot_balls = len(matchup_df[matchup_df['runs_off_bat'] == 0])
    dot_ball_pct = (dot_balls / total_balls) * 100 if total_balls > 0 else 0.0

    metrics_md = f"""
    ## 🏏 Matchup Dashboard: {selected_batter} vs {selected_bowler}
    **Selected Perspective:** Format Analysis ➡️ `{selected_format}`
    
    | Analytics Metric | Performance Value |
    | :--- | :--- |
    | 🎯 **Total Deliveries Faced** | **{total_balls}** balls |
    | 📈 **Runs Scored off Bowler** | **{total_runs}** runs |
    | ☝️ **Times Dismissed (Wickets)** | **{total_wickets}** |
    | ⚡ **Head-to-Head Strike Rate** | **{strike_rate:.2f}** |
    | 🔴 **Dot Ball Percentage** | **{dot_ball_pct:.2f}%** |
    | ☠️ **Wicket Probability (Per Ball)** | **{wicket_prob:.2f}%** |
    """
    
    sample_logs = matchup_df[['format', 'start_date', 'innings', 'ball', 'runs_off_bat', 'wicket_type']].head(20)
    return metrics_md, sample_logs

def update_dropdowns(selected_format):
    available_batters = player_cache[selected_format]["batters"]
    available_bowlers = player_cache[selected_format]["bowlers"]
    default_bat = available_batters[0] if available_batters else None
    default_bowl = available_bowlers[0] if available_bowlers else None
    return gr.Dropdown(choices=available_batters, value=default_bat), gr.Dropdown(choices=available_bowlers, value=default_bowl)

with gr.Blocks(title="5-Way Cricket Matchup Engine") as demo:
    gr.Markdown("# 🏏 5-Way Cricket Player Matchup Engine")
    gr.Markdown("Query data across individual formats (**IPL, T20I, ODI, Test**) or choose **All** to aggregate whole-career records.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Select Parameters")
            format_dropdown = gr.Dropdown(
                choices=["All", "IPL", "T20I", "ODI", "Test"], 
                value="All", 
                label="1. Select Matchup Mode"
            )
            batter_dropdown = gr.Dropdown(choices=player_cache["All"]["batters"], value="Virat Kohli" if "Virat Kohli" in player_cache["All"]["batters"] else player_cache["All"]["batters"][0], label="2. Select Batter")
            bowler_dropdown = gr.Dropdown(choices=player_cache["All"]["bowlers"], value="Jasprit Bumrah" if "Jasprit Bumrah" in player_cache["All"]["bowlers"] else player_cache["All"]["bowlers"][0], label="3. Select Bowler")
            submit_btn = gr.Button("⚡ Run Deep Matchup", variant="primary")
            
        with gr.Column(scale=2):
            output_markdown = gr.Markdown("### 📋 Configure parameters and click Run to compute analytics.")
            output_df = gr.DataFrame(label="Historical Ball-by-Ball Timeline Samples (Max 20)")

    format_dropdown.change(fn=update_dropdowns, inputs=[format_dropdown], outputs=[batter_dropdown, bowler_dropdown])
    submit_btn.click(fn=analyze_matchup, inputs=[format_dropdown, batter_dropdown, bowler_dropdown], outputs=[output_markdown, output_df])

demo.launch(share=True)
