from pathlib import Path
import os, sys
import numpy as np
import pandas as pd

from shiny import App, ui, render, reactive

from modules import player_box_ui, player_box_server, player_season_ui, player_season_server

logs_DIR = "/var/log/shiny-server/"

def get_viewcount():
    app_name = os.path.basename(os.getcwd())
    logs = [s for s in  os.listdir(logs_DIR) if app_name in s]
    connections = 0
    for log in logs:
        with open(logs_DIR + log,"r") as f:
            log_text = f.read()
        connections += log_text.count("open")
    return connections

if sys.platform == "win32":
# Testing
    data_DIR = "C:\\Users\\pansr\\Documents\\shinyNBA\\data\\"
else:
# Deployment
    data_DIR = "/var/data/shiny/"

dfb_p = pd.read_parquet(data_DIR + "NBA_Box_P_Base_All.parquet")
dfb_p.columns = map(str.lower, dfb_p.columns) # type: ignore
dfb_p = dfb_p.sort_values("game_date",ascending=False).reset_index(drop=True)
dfb_p['game_date'] = dfb_p['game_date'].dt.strftime('%Y-%m-%d')
dfb_p["fg_pct"] = dfb_p["fg_pct"]*100
dfb_p["fg3_pct"] = dfb_p["fg3_pct"]*100
dfb_p["ft_pct"] = dfb_p["ft_pct"]*100
colsb_p = ['player_name', 'season', 'game_date',
       'team_name', 'wl', 'pts',
       'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 
       'plus_minus', 'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 
       'fg3_pct', 'ftm', 'fta', 'ft_pct', 'matchup',]
dfb_p = dfb_p[colsb_p]

dfs_p = pd.read_parquet(data_DIR + "NBA_Box_P_Lead_Base_All.parquet")
dfs_p.columns = map(str.lower, dfs_p.columns) # type: ignore
dfs_p = dfs_p.sort_values("season",ascending=False).reset_index(drop=True)
dfs_p["fg_pct"] = dfs_p["fg_pct"]*100
dfs_p["fg3_pct"] = dfs_p["fg3_pct"]*100
dfs_p["ft_pct"] = dfs_p["ft_pct"]*100
colss_p = ['player', 'season', 'team', 'gp', 'pts',
       'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov',
       'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 
       'fg3_pct', 'ftm', 'fta', 'ft_pct']
dfs_p = dfs_p[colss_p]

stats_b_p = ['pts', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 
       'plus_minus', 'season', 'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 
       'fg3_pct', 'ftm', 'fta', 'ft_pct']
stats_str_b_p = stats_b_p[0]
for i in range(len(stats_b_p)-1):
    stats_str_b_p = stats_str_b_p + ", "+ stats_b_p[i+1] 

stats_s_p = ['gp', 'pts',
       'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov',
       'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 
       'fg3_pct', 'ftm', 'fta', 'ft_pct']
stats_str_s_p = stats_s_p[0]
for i in range(len(stats_s_p)-1):
    stats_str_s_p = stats_str_s_p + ", "+ stats_s_p[i+1] 

operators = [">", ">=", "==", "<", "<=", "!="]
ops_str = operators[0]
for i in range(len(operators)-1):
    ops_str = ops_str + ", "+ operators[i+1] 

app_ui = ui.page_fluid(
    ui.card(
        ui.panel_title(ui.h1("NBA Stat Query")),
        ui.card_footer(ui.h6(ui.markdown("""
                **By**: [SravanNBA](https://twitter.com/SravanNBA/) | **App views**: {0}
            """.format(ui.output_text("views",inline=True))
            ))
        )
    ),
    ui.card(
        ui.markdown(""" 
            Simple NBA Stat Query Tool. Searches Box Scores and Seasons.  
            Includes **Regular Season** | Data available from **1946-47** onwards and **updated daily**  
            """
        ), 
    ),
    ui.navset_tab(
        player_box_ui("Player_Box_Score",stats_str_b_p,ops_str),
        player_season_ui("Player_Season",stats_str_s_p,ops_str),
    )
)


def server(input, output, session):

    @render.text
    def views():
        try:
            txt = str(get_viewcount())
        except:
            txt = ""
        return txt

    player_box_server(id="Player_Box_Score",df=dfb_p)  # type: ignore
    player_season_server(id="Player_Season",df=dfs_p) # type: ignore


app = App(app_ui, server)