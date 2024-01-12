import os
import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine.ggplot import ggplot
from plotnine import (
    aes,
    labs,
    geom_density,
    theme,
    theme_xkcd,
    # theme_538,
    guide_legend,
    guides,
    element_text,
    element_blank,
    element_rect,
    scale_fill_manual,
    scale_x_continuous,
    # scale_x_discrete,
    scale_y_continuous,
    geom_point,
    geom_smooth,
    scale_color_manual,
    geom_line,
    geom_hline,
    scale_x_datetime,
    # facet_wrap,
)
from mizani.formatters import percent_format

pd.options.mode.chained_assignment =  None

from shiny import App, ui, render, reactive


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

# Testing
# connections = "100"
# data_DIR = "C:\\Users\\pansr\\Documents\\shinyNBA\\data\\"

# Deployment
connections = str(get_viewcount())
data_DIR = "/var/data/shiny/"

df = pd.read_parquet(data_DIR + "lineup_data.parquet")
teams_list = list(df["team"].unique())

dff = df.query(f'team == "ATL"')
dff_t = dff[["pid","player"]]
dff_t = dff_t.set_index("pid")
player_dict = dff_t.to_dict('dict')['player']


basic_a = [
    'PlusMinus',
    'TsPct',
    'EfgPct',
    'Minutes',
    'TotalPoss',
    'ShotQualityAvg',
    'Points',
    'Pace',
    'Rebounds',
    'Assists',
    'Steals',
    'Blocks',
    'FG2A',
    'FG2M',
    'Fg2Pct',
    'FG3A',
    'FG3M',
    'Fg3Pct',
    'Turnovers',
    'Fouls',
    'DefRebounds',
    'OffRebounds',
    'FTA',
    'FtPoints',
]

shooting_a = [
    'AtRimFGA',
    'AtRimFGM',
    'AtRimAccuracy',
    'AtRimFrequency',
    'ShortMidRangeFGA',
    'ShortMidRangeFGM',
    'ShortMidRangeAccuracy',
    'ShortMidRangeFrequency',
    'LongMidRangeFGA',
    'LongMidRangeFGM',
    'LongMidRangeAccuracy',
    'LongMidRangeFrequency',
    'Corner3FGA',
    'Corner3FGM',
    'Corner3Accuracy',
    'Corner3Frequency',
    'Arc3FGA',
    'Arc3FGM',
    'Arc3Accuracy',
    'Arc3Frequency',
]

misc_a = [
    'AssistPoints',
    'AtRimAssists',
    'Corner3Assists',
    'FoulsDrawn',
    'SecondsPerPossDef',
    'SecondsPerPossOff',
]

basic = {key: key for key in basic_a}
shooting = {key: key for key in shooting_a}
misc = {key: key for key in misc_a}

stats = {"Basic":basic,"Shooting":shooting,"Misc":misc}

# deflections

def get_game_logs(lineup):
    url = "https://api.pbpstats.com/get-game-logs/nba"
    params = {
        "Season": "2023-24", # To get for multiple seasons, separate seasons by comma
        "SeasonType": "Regular Season",
        "EntityId": lineup,
        "EntityType": "Lineup" # Use LineupOpponent to get opponent stats
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    totals = response_json['single_row_table_data']
    game_logs = response_json['multi_row_table_data']
    df_gl = pd.DataFrame(game_logs)
    return df_gl, totals

app_ui = ui.page_fluid(
    # ui.head_content(ui.include_js("gtag.js",method="inline")),
    ui.card(
        ui.panel_title(ui.h1("NBA Lineups Trends")),
        ui.card_footer(ui.h6(ui.markdown("""
                **By**: [SravanNBA](https://twitter.com/SravanNBA/) | **Idea**: [Shamit Dua](https://twitter.com/FearTheBrown) | **App views**: {0}
            """.format(ui.output_text("views",inline=True))
            ))
        )
    ),
    ui.card(
        ui.markdown(""" 
            Plots Lineup stats for 2023-24 Regular Season  
            """
        ), 
    ),
    ui.row(
        ui.column(3,ui.input_selectize("team","Team",teams_list,selected="ATL")),
        ui.column(9,ui.input_selectize("players","Lineup (Select Exactly 5 players)",player_dict,multiple=True, width="70%")),
    ),
    ui.row(
        ui.column(3,ui.input_selectize("stat","Stat",stats,multiple=False)),
        ui.column(3,ui.input_selectize("stype","Stat Type",["Totals","Per 100 Possessions"],selected="Totals",multiple=False)),
    ),
    ui.card(
        ui.output_plot("plot",  width="800px", height="600px"),
    ),
)

def server(input, output, session):
    @reactive.Calc
    def get_player_dict() -> dict:   
        team = input.team()
        dff = df.query(f'team == "{team}"')
        dff_t = dff[["pid","player"]]
        dff_t = dff_t.set_index("pid")
        player_dict = dff_t.to_dict('dict')['player']
        return player_dict
    
    @reactive.Effect()
    def _():
        player_dict = get_player_dict()
        ui.update_selectize(
            "players",
            choices=player_dict,
        )
        
    @reactive.Calc
    def get_lineup_data() -> tuple[pd.DataFrame, dict]:   
        player_dict = get_player_dict()
        lineup_in = list(input.players())
        # lineup_names = [player_dict[ll] for ll in lineup_in]
        lineup_in.sort()
        s = ""
        for ll in lineup_in:
            s += ll
            s += "-"
        lineup = s[:-1]
        lineup_data, totals = get_game_logs(lineup)
        lineup_data["Date"] = pd.to_datetime(lineup_data["Date"], format="%Y-%m-%d")
        return lineup_data, totals
    

    @render.plot(alt="Stat Trends")
    def plot():
        try:
            df1,totals = get_lineup_data()
            var = input.stat()
            stype = input.stype()
            if stype == "Per 100 Possessions":
                no_mod = ['PerPoss','Frequency','Accuracy','Pct','TotalPoss','ShotQualityAvg','Pace',]
                if any(c in var for c in no_mod):
                    df1[var] = df1[var]
                else:
                    df1[var] = df1[var]/df1["TotalPoss"]*100
            else:
                df1[var] = df1[var]
            scale_y = []
            if "Pct" in var or "Accuracy" in var or "Frequency" in var:
                scale_y = scale_y_continuous(labels=percent_format())
            plot = (
                ggplot(df1,aes(x="Date",y=var))  
                + geom_point(alpha=0.8)
                + geom_smooth(size=1.5, se=False, method="lowess", span=0.5, alpha=0.5)
                # + geom_hline(yintercept = totals[var])
                + scale_x_datetime(date_labels="%b-%d", date_breaks="2 week")
                # + geom_smooth(size=1.5, se=False, method="mavg", method_args={"window":5, "min_periods":0})
                # + geom_line()
                + scale_y
                + labs(
                    x="Date",
                    y=var,
                    title=f"Lineup Stat Trends:  {var}",
                    subtitle=totals['Name'],
                    caption="@SravanNBA",
                )
                + theme_xkcd(base_size=16)
                + theme(
                    plot_title=element_text(face="bold", size=20),
                    plot_subtitle=element_text(size=12),
                    plot_margin=0.025,
                    figure_size=[8,6]
                )
            )
        except:
            plot, ax = plt.subplots(1,1,figsize=(8,6))  
            ax.text(0.1, 0.85,'Error: Please select exactly 5 players',horizontalalignment='left',verticalalignment='center',transform = ax.transAxes, fontsize=20)
        return plot  
    
app = App(app_ui, server)
