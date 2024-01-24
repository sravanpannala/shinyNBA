import os,sys
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

if sys.platform == "win32":
# Testing
    data_DIR = "C:\\Users\\pansr\\Documents\\shinyNBA\\data\\"
else:
# Deployment
    data_DIR = "/var/data/shiny/"

df = pd.read_parquet(data_DIR + "NBA_Box_P_Base_All.parquet")
df.columns = map(str.lower, df.columns) # type: ignore
df = df.sort_values("game_date",ascending=False)
df["fg_pct"] = df["fg_pct"]*100
df["fg3_pct"] = df["fg3_pct"]*100
df["ft_pct"] = df["ft_pct"]*100
cols = ['player_name', 'season', 
       'team_name', 'wl', 'pts',
       'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 
       'plus_minus', 'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 
       'fg3_pct', 'ftm', 'fta', 'ft_pct', 'matchup',]
df = df[cols]

stats = ['pts', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 
       'plus_minus', 'season', 'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 
       'fg3_pct', 'ftm', 'fta', 'ft_pct']
stats_str = stats[0]
for i in range(len(stats)-1):
    stats_str = stats_str + ", "+ stats[i+1] 
operators = [">", ">=", "==", "<", "<="]
ops_str = operators[0]
for i in range(len(operators)-1):
    ops_str = ops_str + ", "+ operators[i+1] 

app_ui = ui.page_fluid(
    # ui.head_content(ui.include_js("gtag.js",method="inline")),
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
            Simple NBA Stat Query Tool.  
            Includes **Regular Season** | Data available from **1946-47** onwards and **updated daily**  
            """
        ), 
    ),
    ui.card(
        ui.panel_title(ui.h4("Instructions")),
        ui.markdown(""" 
            **Available stats**: {0}  
            **Available operators**: {1}  
            Write down the stat name, then the operator and the value. You can use "," as a separator for multiple queries.          
            """.format(stats_str,ops_str)
        ), 
        ui.row(
            ui.column(12, ui.input_text("query",ui.h4("Query Box"),value="season >=1984, pts >=60",width="80%")),
        ),
        ui.row(
            ui.column(3,ui.input_action_button("go", "Go!", class_="btn-success"),)
        ),
    ),
    
    ui.output_data_frame("df_display"),
    
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
    def filtered_df() -> pd.DataFrame:
        qstr1 = input.query()
        qstr = qstr1.replace(","," & ")
        qstr = qstr.lower()
        dfc = df.query(qstr)

        return dfc
    
    @render.data_frame
    @reactive.event(input.go, ignore_none=False)
    def df_display():
        display_df = filtered_df()
        return render.DataGrid(display_df, filters=False)
    

app = App(app_ui, server)