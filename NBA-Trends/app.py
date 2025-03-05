from pathlib import Path
import os, sys
import numpy as np
import pandas as pd

from shiny import App, ui, render, reactive

from modules import player_dist_ui, player_dist_server, team_dist_ui, team_dist_server

if sys.platform == "win32":
# Testing
    data_DIR = "C:\\Users\\pansr\\Documents\\shinyNBA\\data\\"
else:
# Deployment
    data_DIR = "/var/data/shiny/"

dfp = pd.read_parquet(data_DIR + "NBA_Player_Distribution.parquet")
dft = pd.read_parquet(data_DIR + "NBA_Team_Distribution.parquet")

players = list(dfp["Player"].unique())
players.append("None")
seasons = (list(map(str,list(set(dfp["Season"])))))
seasons.reverse()

teams = list(dft["Team"].unique())
teams.append("None")
seasonst = (list(map(str,list(set(dft["Season"])))))
seasonst.reverse()

basic_a = [
    'Pts', 'Min', 'FGM', 'FGA', 'FG %', 'FG3M', 'FG3A',
    'FG3 %', 'FTM', 'FTA', 'FT %', 'OReb', 'DReb', 'Reb', 'Ast', 'Stl',
    'Blk', 'Tov', 'PF', 'Plus Minus',
]

advanced_a = [
    'ORtg', 'DRtg', 'NetRtg', 'eFG %', 'TS %',
]

playmaking_a = [
    'Ast %', 'Ast/Tov', 'Ast Ratio','Tov Ratio', 'Passes Made', 'Passes Received',
    'FT Asts', 'Secondary Asts', 'Potential Asts', 'Potential Asts', 'Adj Asts',
    'Drive Points', 'Drive Asts', 'Drives',
]

rebounding_a = [
    'OReb %', 'DReb %', 'Reb %','OReb Chances', 'DReb Chances', 'OReb Contest',
    'DReb Contest',
]

usage_a = [
    'USG %', 'Pace', 'Poss', 'Touches',  'Front Court Touches', 'Time Of Poss',
    'Seconds Per Touch',
]

hustle_a = [
    'Miles', 'Miles Off', 'Miles Def', 'Avg Speed', 'Avg Speed Off', 'Avg Speed Def',
    'Extra Possessions',
]

basic = {key: key for key in basic_a}
advanced = {key: key for key in advanced_a}
playmaking = {key: key for key in playmaking_a}
rebounding = {key: key for key in rebounding_a}
usage = {key: key for key in usage_a}
hustle = {key: key for key in hustle_a}

vars = {"Basic":basic,"Advanced":advanced,"Playmaking":playmaking,"Rebounding":rebounding,"Usage":usage,"Hustle":hustle}

basic_at = [
    'Pts', 'FGM', 'FGA', 'FG %', 'FG3M', 'FG3A',
    'FG3 %', 'FTM', 'FTA', 'FT %', 'OReb', 'DReb', 'Reb', 'Ast', 'Stl',
    'Blk', 'Tov', 'PF', 'Plus Minus',
]

basict = {key: key for key in basic_at}

varst = {"Basic":basict,"Advanced":advanced,"Playmaking":playmaking,"Rebounding":rebounding}

app_ui = ui.page_fluid(
    ui.card(
        ui.panel_title(ui.h2("NBA Stat Distribution and Trends")),
        ui.card_footer(ui.h5(ui.markdown("""
                **By**: [Sravan](https://twitter.com/sradjoker/)
            """
            ))
        )
    ),
    ui.card(
        ui.markdown(""" 
            Plotting Density & Trends for various boxscores stats for from **2004-Current**. Tracking Data available only from **2013-**  
            In the Density plot, the Y value (Frequency), is an indicator of how often the event occurs. More information [here](https://en.wikipedia.org/wiki/Kernel_density_estimation)  
            For the Trends plot, the trend line is a smooth conditional mean. More information [here](https://ggplot2.tidyverse.org/reference/geom_smooth.html)  
            [**Glossary of Stats**](https://www.nba.com/stats/help/glossary)
            """
        ),
    
    ),
    ui.navset_tab(
        # ui.nav_panel("Players",player_dist_ui("tab1",vars,players,seasons)),
        player_dist_ui("Players",vars,players,seasons),
        team_dist_ui("Teams",varst,teams,seasonst),

        # ui.nav_panel("Teams", "Return Some Text"),
    )
)


def server(input, output, session):

    player_dist_server(id="Players",df=dfp) 
    team_dist_server(id="Teams",df=dft)


app = App(app_ui, server)

