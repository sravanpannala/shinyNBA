import os
import sys
import json
import requests
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine.ggplot import ggplot
from plotnine import (
    aes,
    labs,
    theme,
    theme_xkcd,
    guides,
    element_text,
    element_blank,
    element_rect,
    scale_y_continuous,
    geom_point,
    geom_smooth,
    scale_color_manual,
    geom_hline,
    scale_x_datetime,
    scale_y_datetime,
    # annotate,
    guide_legend,
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

if sys.platform == "win32":
# Testing
    data_DIR = "C:\\Users\\pansr\\Documents\\shinyNBA\\data\\"
else:
# Deployment
    data_DIR = "/var/data/shiny/"

df = pd.read_parquet(data_DIR + "lineup_data.parquet")
df["pid"] = df["pid"].astype(str)
teams_list = list(df["team"].unique())
team_init = "Cleveland Cavaliers"
dff = df.query(f'team == "{team_init}"')
dff_t = dff[["pid","player"]]
dff_t = dff_t.set_index("pid")
player_dict = dff_t.to_dict('dict')['player']
init_players = ['1628378', '1628386', '1629731', '1629636', '1630596']

dfl = pd.read_parquet(data_DIR + "lineup_list_data.parquet")

basic_a = [
    'PlusMinus',
    'TsPct',
    'EfgPct',
    'Minutes',
    'Poss',
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
        "Season": "2024-25", # To get for multiple seasons, separate seasons by comma
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
                **By**: [Sravan](https://twitter.com/sradjoker/) | **Idea**: [Shamit Dua](https://twitter.com/FearTheBrown) | **App views**: {0}
            """.format(ui.output_text("views",inline=True))
            ))
        )
    ),
    ui.card(
        ui.markdown(""" 
            Plots Lineup stats for 2024-25 Regular Season. Powered by [PBP Stats API](https://api.pbpstats.com/docs).  
            Trendline is calculated using Locally Weighted Scatterplot Smoothing. More information [here](https://ggplot2.tidyverse.org/reference/geom_smooth.html).  
            Please use the provided table (team lineups sorted by minutes played) to find possible lineup combinations if needed. 
            """
        ), 
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.row(
                ui.column(12,ui.input_selectize("team","Team",teams_list,selected=team_init)),
            ),
            ui.row(
                ui.column(12,ui.input_selectize("players","Lineup (Select Exactly 5 players)",player_dict, selected=init_players,multiple=True, width="70%")),
            ),
            ui.row(
                ui.column(12,ui.input_selectize("stat","Stat",stats,multiple=False)),
            ),
            ui.row(
                ui.column(12,ui.input_selectize("stype","Stat Type",["Totals","Per 100 Possessions"],selected="Totals",multiple=False)),
            ),
            ui.row(
                ui.column(12,ui.input_action_button("go", "Go!", class_="btn-success",width="70%"),)
            ),
            width="300px",
        ),
        ui.card(
            ui.output_data_frame("output_table"), height=""
        ),
        ui.card(
            ui.output_plot("plot",  width="900px", height="700px"),
        ),    
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
        # print(lineup_in)
        if len(lineup_in)!=5:
            raise Exception("Error: Please select exactly 5 players")
        # lineup_names = [player_dict[ll] for ll in lineup_in]
        lineup_in.sort()
        s = ""
        for ll in lineup_in:
            s += ll
            s += "-"
        lineup = s[:-1]
        # print(lineup)
        lineup_data, totals = get_game_logs(lineup)
        # print(len(lineup_data))
        if len(lineup_data)<2:
            raise Exception("Error: This Lineup hasn't played any minutes\nthis season, choose another lineup")
        lineup_data["Date"] = pd.to_datetime(lineup_data["Date"], format="%Y-%m-%d")
        lineup_data["Minutes"] = pd.to_datetime(lineup_data["Minutes"], format="%M:%S")
        lineup_data["Poss"] = lineup_data["OffPoss"]
        totals["Poss"] = totals["OffPoss"]
        return lineup_data, totals
    

    @render.plot(alt="Stat Trends")
    @reactive.event(input.go, ignore_none=False)
    def plot():
        try:
            df1,totals = get_lineup_data()
            df1["TrendLine"] = "Trend Line"
            df1["AvgLine"] = "Season Avg"
            var = input.stat()
            var1 = var + "1"
            stype = input.stype()
            if stype == "Per 100 Possessions":
                no_mod = ['PerPoss','Frequency','Accuracy','Pct','ShotQualityAvg','Pace']
                if any(c in var for c in no_mod):
                    df1[var1] = df1[var]
                    y_int = totals[var]
                elif "Minutes" in var:
                    df1[var1] = df1[var]
                    tot_secs = round(totals[var]*60/len(df1[var]))
                    td = dt.timedelta(seconds=tot_secs)
                    y_int = pd.to_datetime(td, format="%H:%M:%S") # type: ignore
                else:
                    df1[var1] = df1[var]/df1["Poss"]*100
                    y_int = totals[var]/totals["Poss"]*100
            else:
                df1[var1] = df1[var]
                y_int = totals[var]/len(df1[var])
                no_mod = ['PerPoss','Frequency','Accuracy','Pct','ShotQualityAvg','Pace']
                if any(c in var for c in no_mod):
                    y_int = totals[var]
                elif "Minutes" in var:
                    tot_secs = round(totals[var]*60/len(df1[var]))
                    td = dt.timedelta(seconds=tot_secs)
                    y_int = pd.to_datetime(td, format="%H:%M:%S") # type: ignore
            scale_y = []
            if "Pct" in var or "Accuracy" in var or "Frequency" in var:
                scale_y = scale_y_continuous(labels=percent_format()) # type: ignore
            elif "Minutes" in var:
                scale_y = scale_y_datetime(date_labels = "%M:%S")
            kwargs_legend = {"alpha":0.0}
            fig = (
                ggplot(df1,aes(x="Date",y=var1, color="TrendLine"))  
                + geom_smooth(size=1.5, se=False, method="lowess", span=0.3)
                + geom_point(fill="white",stroke=1.2)
                + geom_hline(aes(color="AvgLine",yintercept = y_int), linetype='dashed', show_legend=True)
                + scale_x_datetime(date_labels="%b-%d", date_breaks="2 week")
                + scale_color_manual(name="Trendline", values=["orangered","black"])
                + scale_y
                + labs(
                    x="Date",
                    y=var + " " + f"({stype})",
                    title=f"Lineup Stat Trends: {var}",
                    subtitle= (
                        totals['Name'] + "\n"
                        + stype + " | " 
                        + "Total Possessions Played: " + str(totals["Poss"]) + " | " 
                        + "Total Minutes Played: " + str(totals["Minutes"]) 
                    ),
                    caption="@sradjoker | @FearTheBrown | Powered by api.pbpstats.com\nshiny.sradjoker.cc/NBA-Lineups-Trends",
                )
                + theme_xkcd(base_size=16)
                + theme(
                    text=element_text(family=["Comic Sans MS"]),
                    plot_title=element_text(face="bold", size=20),
                    plot_subtitle=element_text(size=12),
                    plot_caption=element_text(ha="left"),
                    plot_margin=0.025,
                    figure_size=[9,7]
                )
                + theme(
                    legend_title=element_blank(),
                    # legend_position = [0.78,0.80],
                    legend_position="bottom",
                    legend_box_margin=0,
                    legend_background=element_rect(color="grey", size=0.001,**kwargs_legend), # type: ignore
                    legend_box_background = element_blank(),
                    legend_text=element_text(size=11),
                )
                + guides(color=guide_legend(ncol=2))
            )
        except Exception as error:
            print(error)
            fig, ax = plt.subplots(1,1,figsize=(9,7))  
            ax.text(0.1, 0.95,str(error),horizontalalignment='left',verticalalignment='center',transform = ax.transAxes, fontsize=18)
            ax.axis('off')

        return fig  
    
    @render.data_frame
    def output_table():
        team = input.team()
        display_df = dfl.query(f"team == '{team}'")
        # display_df.style.background_gradient(axis=0, cmap="PiYG")  
        return render.DataGrid(display_df, filters=True)
    # @render.ui
    # def my_plot():
    #     try:
    #         return ui.output_plot("plot",  width="900px", height="700px")
    #     except:
    #         return ui.h3("Error: Please select exactly 5 players")
    
app = App(app_ui, server)
