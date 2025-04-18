import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

from shiny import App, ui, render, reactive
from shiny.types import ImgData

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

df1 = pd.read_parquet(data_DIR + "playoff_model_probabilities_2024.parquet")
df2 = df1.sort_values("Team")
teams1 = df2["Team"].unique()
teams = {p: p for p in teams1}

# table colors
cmap = plt.get_cmap('RdYlGn')
colors1 = []
for i in np.linspace(0,1,101):
    colors1.append(to_hex(cmap(i)))
colors2 = []
for i in np.linspace(0,1,51):
    colors2.append(to_hex(cmap(i)))


app_ui = ui.page_fluid(
    ui.card(
        ui.panel_title(ui.h1("NBA Playoff Probabilities 2024-25")),
        ui.card_footer(ui.h6(ui.markdown("""
                **By**: [Sravan](https://twitter.com/sradjoker/) & [Krishna Narsu](https://twitter.com/sradjoker/) | **App views**: {0}
            """.format(ui.output_text("views",inline=True))
            ))
        )
    ),
    ui.card(
        ui.markdown(""" 
            Predicting playoff probilities using various publicly availalbe advanced metrics.  
            Chose the 1st team and the 2nd team and you'll get the probabilities for that combination. 
            You can get probabilities for any combination of playoff teams.
            """
        ), 
    ),
    
    ui.row(
        ui.column(6, ui.input_selectize("t1","Team 1",teams, selected="CLE")),
        ui.column(6, ui.input_selectize("t2","Team 2",teams, selected="ATL")),
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
        t1 = input.t1()
        t2 = input.t2()
        df1q = df1[(df1["Team"] == t1) & (df1["Opponent"] == t2)]
        df1q = df1q.sort_values("Model").reset_index(drop=True)
        dff = df1q.copy()
        return dff
    
    @reactive.Calc
    def get_bgcolor():
        dff = filtered_df()
        bgcolor = []
        for r in range(8):
            for c in range(3,5):
                colors = colors1
                ci = int(dff.iloc[r,c].round()) # type: ignore
                if ci>80 or ci<20:
                    color = "white",
                else:
                    color = "black"
                b = {
                    "rows": [r],  
                    "cols": [c],  
                    "style": {
                        "background-color": colors[ci],
                        "font-weight":"bold",
                        "color":color,
                        },  
                }
                bgcolor.append(b)
            for c in range(5,13):
                colors = colors2
                ci = int(dff.iloc[r,c].round()) # type: ignore
                if ci>50:
                    ci = 50
                if ci>40 or ci<10:
                    color = "white",
                else:
                    color = "black"
                b = {
                    "rows": [r],  
                    "cols": [c],  
                    "style": {
                        "background-color": colors[ci],
                        "font-weight":"bold",
                        "color":color,
                        },  
                }
                bgcolor.append(b)
        return bgcolor 

    
    @render.data_frame
    def df_display():
        display_df = filtered_df()
        return render.DataGrid(
            display_df,
            styles=get_bgcolor(),
            height='350px',
            )


app = App(app_ui, server)