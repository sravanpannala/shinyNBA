from pathlib import Path
import os, sys
import time
from datetime import datetime
import numpy as np
import pandas as pd
from plotnine.ggplot import ggplot
from plotnine import (
    aes,
    labs,
    geom_bar,
    theme,
    theme_xkcd,
    element_text,
    coord_flip,
    scale_color_identity,
    theme_classic,
    geom_hline,
)

from shiny import App, ui, render, reactive
from shiny.types import ImgData

pd.options.mode.chained_assignment =  None

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

filepath = data_DIR + "NBA_games_minutes_war_missed.parquet"
tstamp = os.path.getmtime(filepath)
date_updated = datetime.fromtimestamp(tstamp).strftime('%A %d %b, %Y - %H:%M:%S')
df = pd.read_parquet(filepath)
dff = df.drop(columns="colorsTeam")


app_ui = ui.page_fluid(
    ui.card(
        # ui.card_header(ui.output_image("image", inline=True)),
        ui.panel_title(
            ui.row(
                ui.column(10, ui.h2("NBA Wins Missed")),
                ui.column(2, ui.output_image("image", inline=True)),                
            ),
        ),
        ui.card_footer(ui.h5(ui.markdown("""
                **By**: [Sravan](https://twitter.com/sradjoker/) | 
                **Idea**: [Krishna Narsu](https://twitter.com/knarsu3/)  
                **App views**: {0} | Updated on **{1} UTC**
            """.format(ui.output_text("views",inline=True),date_updated)
            ))
        )
    ),
    ui.card(
        ui.markdown(""" 
            Tracking **Games** Missed, **Minutes** Missed and **multiLEBRON WAR** Missed due to Injury, Suspensions and Personal Reasons.  
            **multiLEBRON** is a new version of LEBRON which is predictive in nature and uses past season's data in addition to current season.  
            Data Source for Missed Games: [pbpstats](https://pbpstats.readthedocs.io/en/latest/), [nba_api](https://github.com/swar/nba_api)
            """
        ),
    
    ),
    ui.output_plot("plot",  width="1000px", height="800px"),
    ui.output_data_frame("output_table"),
)

def server(input, output, session):

    @render.text
    def views():
        try:
            txt = str(get_viewcount())
        except:
            txt = ""
        return txt

    @render.data_frame
    def output_table():
        display_df = dff
        # display_df.style.background_gradient(axis=0, cmap="PiYG")  
        return render.DataGrid(display_df, filters=True)
    
    @render.plot(alt="Games Missed")
    def plot():
        lb_mean = df["LEBRON_WAR_Missed"].mean()
        lb_mean = round(lb_mean,2)
        # df1 = df.copy()
        # df1["LEBRON_WAR_Missed"] = df1["LEBRON_WAR_Missed"] - lb_mean
        # df1["LEBRON_WAR_Missed"] = df1["LEBRON_WAR_Missed"].round(3)
        
        p = (
            ggplot(df, aes(x='Team', y='LEBRON_WAR_Missed'))
            + geom_bar(aes(fill="colorsTeam"),stat="identity", alpha=0.7)
            + geom_hline(yintercept=lb_mean, linetype="dashed")
            + coord_flip()
            + scale_color_identity(aesthetics=["fill"],guide=None)
            # + theme_538(base_size=12)
            + theme_classic(base_size=12)
            + theme(
                figure_size=(10,8),
                plot_title=element_text(size=20, weight="bold"),
            )
            + labs(
                title="Wins Missed",
                subtitle=f"League Average = {lb_mean} WAR Missed\nPlayers missing the game due to injury/personal reasons/suspension",
                caption="@sradjoker | Source: nba.com/stats, pbpstats, bball-index",
                y= "Wins Missed",
                x="",
            )
        )
        return p

    @render.image
    def image():
        from pathlib import Path

        dir = Path(__file__).parent / "www"
        img: ImgData = {"src": str(dir) + "/" + "logo.webp", "width": "100px"}
        return img

www_dir = Path(__file__).parent / "www"

app = App(app_ui, server, static_assets=www_dir)