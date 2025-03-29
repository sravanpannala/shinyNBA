import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

from shiny import App, ui, render, reactive

if sys.platform == "win32":
# Testing
    data_DIR = "C:\\Users\\pansr\\Documents\\shinyNBA\\data\\"
else:
# Deployment
    data_DIR = "/var/data/shiny/"

df1 = pd.read_csv(data_DIR + "bSPARQ_data.csv")
df2 = df1.iloc[:,52:-2]
df2s = df1.iloc[:,:52]
players1 = df1["Player"].unique()
players = {p: p for p in players1}

cols3 = ["Player","Year","POSITION","HEIGHT","WEIGHT","WINGSPAN","STANDING REACH",
     "LANE AGILITY TIME (SECONDS)","THREE QUARTER SPRINT (SECONDS)",
     'STANDING VERTICAL LEAP (INCHES)','MAX VERTICAL LEAP (INCHES)','bSPARQ',
     "y Score Normalized"]
colsd = ["Rank","Player","Year","Position","Height","Weight",
         "Wingspan","Reach","Lane Agility","3/4 Sprint","Standing Vert","Max Vert",
         "bSPARQ","Similarity"]
colsf = ["Rank","Player","Year","Position","bSPARQ","Similarity"]

cmap = plt.get_cmap('Greens')
colors = []
for i in np.linspace(0.7,0.25,21):
    colors.append(to_hex(cmap(i)))

bgcolor = []
b = {
        "rows": [0],  
        "style": {"background-color": "darkslateblue",
                  "font-weight":"bold",
                  "color":"white"},  
    }
bgcolor.append(b)
for r in range(0,21):
    b = {
        "rows": [r],  
        "cols": [5],  
        "style": {"background-color": colors[r],
                  "font-weight":"bold"},  
    }
    bgcolor.append(b)


app_ui = ui.page_fluid(
    ui.card(
        ui.panel_title(ui.h1("bSPARQ Athletic Similarity Scores")),
        ui.card_footer(ui.h6(ui.markdown("""
                **By**: [Jared Dubin](https://twitter.com/JADubin5/)
            """
            ))
        )
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.row(
                ui.column(12,ui.input_selectize("player","Player",players, selected="Kel'el Ware")),
            ),
        ),
        ui.output_data_frame("df_display"),
    )
)

def server(input, output, session):
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        pl = input.player()
        df1q = df1.query(f'Player == "{pl}"')
        df2q = df1q.iloc[:,52:-2]
        dfa = []
        for i in range(len(df2)):
            dfa.append(df2.iloc[i]-df2q)
        df3 = pd.concat(dfa).reset_index(drop=True)
        df4 = df3.map(lambda x: x**2)
        df4.iloc[:,0] = 2*df4.iloc[:,0]
        df4.iloc[:,1] = 4*df4.iloc[:,1]
        df4.iloc[:,3] = 4*df4.iloc[:,3]
        df4["Similarity Score"] = np.sqrt(df4.sum(axis=1))
        smax = df4["Similarity Score"].max()
        smin = df4["Similarity Score"].min()
        df4["y Score Normalized"]=100-(df4["Similarity Score"]-smin)/(smax-smin)*100
        df4["y Score Normalized"] = round(df4["y Score Normalized"],1)
        df5 = df2s.join(df4)
        df5 = df5.iloc[:,1:]
        df6 = (df5
        .sort_values("y Score Normalized",ascending=False)
        .head(21).reset_index(drop=True))
        cols1 = list(df6.columns)
        cols2 = []
        for c in cols1:
            c2 = c.replace('\n','')
            cols2.append(c2)
        df6.columns = cols2
        df7 = df6[cols3]
        df7 = df7.reset_index()
        df7.columns = colsd
        df8 = df7[colsf]
        dff = df8.copy()
        return dff
    
    @render.data_frame
    def df_display():
        display_df = filtered_df()
        return render.DataGrid(
            display_df,
            styles=bgcolor,
            )

app = App(app_ui, server)
