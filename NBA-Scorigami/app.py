import os
from datetime import datetime
import numpy as np
import pandas as pd
from plotnine.ggplot import ggplot
from plotnine import aes, scale_fill_gradient, theme, element_blank,element_text, geom_tile, geom_text, labs, theme_xkcd, element_rect, element_text

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

filepath = data_DIR + "NBA_Player_Scorigami.parquet"
tstamp = os.path.getmtime(filepath)
date_updated = datetime.fromtimestamp(tstamp).strftime('%A %d %b, %Y - %H:%M:%S')

df = pd.read_parquet(filepath)

players = list(df["Player"].unique())
vars = ["Points", "Assists", "Rebounds", "Steals", "Blocks","Turnovers", "3Pt Shots Made", "Free Throws Made"]

def get_cat(var):
    var_cat = ""
    if var == "Points":
        var_cat = "Pts_cat"
    elif var == "Assists":
        var_cat = "Ast_cat"
    elif var == "Rebounds":
        var_cat = "Reb_cat"
    elif var == "Steals":
        var_cat = "Stl_cat"
    elif var == "Blocks":
        var_cat = "Blk_cat"
    elif var == "Turnovers":
        var_cat = "Tov_cat"
    elif var == "3Pt Shots Made":
        var_cat = "Fg3M_cat"
    elif var == "Free Throws Made":
        var_cat = "Ftm_cat"
    return var_cat

app_ui = ui.page_fluid(
    # ui.head_content(ui.include_js("gtag.js",method="inline")),
    ui.card(
        ui.panel_title(ui.h1("NBA Box Scorigami")),
        ui.card_footer(ui.h6(ui.markdown("""
                **By**: [SravanNBA](https://twitter.com/SravanNBA/) | **App views**: {0} | Updated on **{1} UTC**
            """.format(ui.output_text("views",inline=True),date_updated)
            ))
        )
    ),
    ui.card(
        ui.markdown(""" 
            Heavily inpsired by [Todd Whitehead's](https://twitter.com/CrumpledJumper) [Box Scorigami](https://x.com/CrumpledJumper/status/1740251518840996135?s=20) of Kevin Durant.  
            Includes **Regular Season** & **Playoffs** | Data available only from **1996-97** onwards
            """
        ), 
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.row(
                ui.column(12, ui.input_selectize("player","Player",players, selected="LeBron James")),
            ),
            ui.row(
                ui.column(12, ui.input_selectize("var1","Stat 1",vars, selected="Points")),
            ),
            ui.row(
                ui.column(12, ui.input_selectize("var2","Stat 2",vars, selected="Assists")),
            ),
        ),
        ui.output_plot("plt", width="600px", height="600px"),
    )
)

def server(input, output, session):

    @render.text
    def views():
        txt = str(get_viewcount())
        return txt

    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        player = input.player()
        var1 = input.var1()
        var2 = input.var2()
        dff = df.query(f'Player == "{player}"')
        cat1 = get_cat(var1)
        cat2 = get_cat(var2)
        dfc = dff.groupby([cat1,cat2], observed=False)[["Player"]].count()
        dfc.columns = ["Counts"]
        dfc = dfc.reset_index()

        return dfc
    
    @render.plot(alt="NBA Scorigami")
    def plt():
        dfc = filtered_df()
        player = input.player()
        var1 = input.var1()
        var2 = input.var2()
        cat1 = get_cat(var1)
        cat2 = get_cat(var2)
        p = (
            ggplot(dfc,aes(x=cat1, y=cat2, fill="Counts"))
            + geom_tile(aes(width=.88, height=.88))
            + geom_text(aes(label='Counts'), size=14, show_legend=False, fontweight = "bold") 
            + scale_fill_gradient(low = "#f2f2f2", high = "red")
            + labs(
                title = player + ": Box Scorigami",
                subtitle = f"# NBA Games with different combinations of\n  {var1} & {var2}",
                caption = "@SravanNBA\nshiny.sradjoker.cc/NBA-Scorigami",
                x = var1,
                y = var2,
            )
            + theme_xkcd(base_size=14, stroke_color="none")
            + theme(
                plot_background = element_rect(fill = 'white', color = "white"),
                legend_position="none",
                plot_title=element_text(face="bold", size=18),
                plot_subtitle=element_text(size=13),
                plot_caption=element_text(hjust=0),
                figure_size= (6,6),
                axis_text_y = element_text(size = 12, vjust=1),
            )
            + theme(
                axis_ticks_major_y=element_blank(),
                axis_ticks_major_x=element_blank(),
                axis_ticks_minor_y=element_blank(),
                axis_ticks_minor_x=element_blank(),
                panel_grid_major_y=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_border=element_blank(),

            )
        )
        return p
    
app = App(app_ui, server)
