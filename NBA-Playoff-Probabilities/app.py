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
            Predicting playoff probabilities using various publicly available advanced metrics.  
            Choose the 1st team and the 2nd team and you'll get the probabilities for that combination. You can get probabilities for any combination of playoff teams.  
            For detailed explanation and methodology, scroll down to the bottom of the page.
            Our preferred model is `pred_ridge` at the top of the table.
            """
        ), 
    ),
    
    ui.row(
        ui.column(6, ui.input_selectize("t1","Team 1",teams, selected="LAL")),
        ui.column(6, ui.input_selectize("t2","Team 2",teams, selected="MIN")),
    ),
    ui.output_data_frame("df_display"),
    ui.card(
        ui.markdown("""
            ## Methodology
            For the metric models, each one of the metrics is multiplied by projected minutes (provided by [@AmericanNumbers](https://twitter.com/AmericanNumbers/)), summed up by team to get projected team impact ratings for each metric. These projected team impact ratings for each metric are then used to predict playoff game outcomes (using the team rating, opponent team rating and which team was at home). This generates probabilities for each team to win a playoff game at home and on the road. Then each series is simulated 10,000 times using these probablities to get series probabilities.  
            All of these models were run for every possible matchup combination that can happen in this 2025 playoffs, including possible Finals matchups. Tiebreakers like opponent conference record for a possible Nuggets-Pacers series were also included (the teams split their season series).
            ### `pred_ridge` Model
            For the `pred_ridge` model, the structure of the model is different. One of the difficulties with projecting series is developing a good minutes model. And so the metric models are highly dependent on how good the minutes projections are. This model predicts the series outcome (win in 4, win in 5, etc.) using an ordinal logistic ridge regression. So it is different because there is no prediction made for each game. That is one of the drawbacks to the model: it just predicts each series. But one of the benefits is that instead of needing good minute projections for each player, the model instead uses a top 8 rotation for each team where each player is ranked based on where they rank in predictive epm. So it looks something like this: predictive epm best player + predictive epm 2nd best player and so on until you get the top 8 players in the rotation. This is used for the ranking of the top 8. Then predictive epm, lebron and darko for the top 8 players are used in the model. Some of our other bball-index stats are also used such as Overall Shooting Talent, Catch and Shoot 3pt Talent, Ball Dominance etc. And again, the Overall Shooting Talent etc. for the best player is based on which player is ranked the highest on the team in predictive epm.  
            In addition to these player stats, other team stats are used like rim attempt rate, corner 3pt rate, above the break 3pt rate etc. as well as the opponent's stats so that the style of the team and opponent can be captured. Also included are regular season series win/loss record + Net Rating in the matchups so that if a team goes 4-0 in a matchup and wins every regular season game easily, that effect can be included.  
            
            ## Credits
            1. Minutes Projections: [@AmericanNumbers](https://twitter.com/AmericanNumbers/)
            2. EPM: [Dunks & Threes](https://dunksandthrees.com/)
            3. DARKO DPM: [DARKO](https://darko.app/)
            4. BPM: [basketball reference](https://www.basketball-reference.com/)     
            5. raptor: [Neil Paine](https://neilpaine.substack.com/)
            6. xrapm: [xrapm](https://xrapm.com/)
            """
        ), 
    ),
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
        r = 0
        c = 2
        b = {
            "rows": [r],  
            "cols": [c],  
            "style": {
                "background-color": "grey",
                "font-weight":"bold",
                "color":"white",
            },  
        }
        bgcolor.append(b)
        for r in range(9):
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