import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc


pd.options.mode.chained_assignment =  None

from shiny import App, ui, render, reactive


if sys.platform == "win32":
# Testing
    data_DIR = "C:\\Users\\pansr\\Documents\\shinyNBA\\data\\"
else:
# Deployment
    data_DIR = "/var/data/shiny/"

df = pd.read_csv(data_DIR + "Kenan_Blackshear_Shot_Chart.csv")
df.columns = map(str.lower, df.columns) # type: ignore
df["dribble_handedness"] = df["dribble_handedness"].fillna("N/A")
df["x"] = df["x"]*12
df["y"] = df["y"]*12
df["half"] = df["half"].astype(str)

half = ["1","2"]
shot_type = ['Layup', 'Jumper', 'Floater', 'Dunk']
shot_mov = ['Power', 'Turnaround Fadeaway', 'Sizeup', 'Drive', 'Fadeaway',
       'Cut', 'Stepthrough', 'Putback', 'Flash', 'Spot Up', 'Turnaround',
       'Slide', 'Stepback', 'Heave']
playtype = ['Post Up', 'High Post', 'Transition', 'PnR', 'Isolation',
       'Spot Up', 'Mid Post', 'Cut', 'OReb', 'Handoff', 'Drive',
       'Mid-Post']
cns_otd = ['C','O']
con_uncon = ['C','U']
shot_hand = ['Right', 'Left', 'Both']
drib_hand = ['Both', 'Left','Right','N/A']

def draw_court(ax=None, color='black', lw=2):
# If an axes object isn't provided to plot onto, just get current one
  if ax is None:
    ax = plt.gca()
    # Create the various parts of an NBA basketball court
    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
  hoop = Circle((300, 55.5), radius=7.5, linewidth=lw, color=color,     fill=False)
  # Create backboard
  backboard = Rectangle((264, 48), 72, -1, linewidth=lw, color=color)
  # The paint
  # Create the outer box 0f the paint, width=16ft, height=19ft
  #outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,fill=False)
  # Create the inner box of the paint, widt=12ft, height=19ft
  inner_box = Rectangle((228, 0), 144, 228, linewidth=lw, color=color,fill=False)
  # Create free throw top arc
  top_free_throw = Arc((300, 228), 144, 144, theta1=0, theta2=180,
  linewidth=lw, color=color, fill=False)
  # Restricted Zone, it is an arc with 4ft radius from center of the hoop
  restricted = Arc((300, 55.5), 72, 72, theta1=0, theta2=180,   linewidth=lw, color=color,linestyle = 'dashed')
  # Create the side 3pt lines, they are ~4.5 ft long before they begin to arc
  corner_three_a = Rectangle((50.5, 0), 0, 55.5, linewidth=lw,color=color)
  corner_three_b = Rectangle((549, 0), 0, 55.5, linewidth=lw, color=color)
  # 3pt arc - center of arc will be the hoop, arc is 20'9" away from hoop
  three_arc = Arc((300, 55.5), 498, 498, theta1=0, theta2=180, linewidth=lw,color=color)
  # # Center Court
  center_outer_arc = Arc((300, 564), 144, 144, theta1=180,   theta2=0,linewidth=lw, color=color)
  center_inner_arc = Arc((300, 564), 48, 48, theta1=180, theta2=0,linewidth=lw, color=color)
  # # List of the court elements to be plotted onto the axes
  court_elements = [hoop,backboard,inner_box,top_free_throw,restricted,corner_three_a,corner_three_b,three_arc,center_outer_arc,center_inner_arc]
  # Add the court elements onto the axes
  for element in court_elements:
      ax.add_patch(element)
  return ax


bball_gray = "#312f30"
bball_white = "#dddee0"
bball_orange = "#f87c24"
bball_light_orange = "#fbaf7b"
bball_black = "#000010"
dark_grey = "#282828"
fontsize = 28
title_size = 48

app_ui = ui.page_fluid(
    # ui.head_content(ui.include_js("gtag.js",method="inline")),
    ui.card(
        ui.panel_title(ui.h1("Kenan BlackShear Shot Chart")),
        ui.card_footer(ui.h6(ui.markdown("""
                **By**: [Sravan Pannala](https://twitter.com/sradjoker/) & [Neema Djavadzadeh](https://twitter.com/findingneema23)
            """
            ))
        )
    ),

    ui.row(
        ui.column(4,ui.input_selectize("half","Half",half,selected=half,multiple=True)),
        ui.column(4,ui.input_slider("mins_left", "Mins Left", min=0, max=20, value=[0, 20])),
        ui.column(4,ui.input_slider("shot_clock", "Shot Clock", min=0, max=30, value=[0, 30])),
    ),
    ui.row(
        ui.column(4,ui.input_selectize("shot_type","Shot Type",shot_type,selected=shot_type,multiple=True)),
        ui.column(4,ui.input_selectize("shot_mov","Shot Movement",shot_mov,selected=shot_mov,multiple=True)),
        ui.column(4,ui.input_selectize("playtype","Playtype",playtype,selected=playtype,multiple=True)),
    ),
    ui.row(
        ui.column(4,ui.input_selectize("cns_otd","CnS/OtD",cns_otd,selected=cns_otd,multiple=True)),
        ui.column(4,ui.input_selectize("con_uncon","Cont/Uncont",con_uncon,selected=con_uncon,multiple=True)),
    ),
    ui.row(
        ui.column(4,ui.input_selectize("shot_hand","Shot Hand",shot_hand,selected=shot_hand,multiple=True)),
        ui.column(4,ui.input_selectize("drib_hand","Dribble Hand",drib_hand,selected=drib_hand,multiple=True)),
        ui.column(4,ui.input_slider("shot_quality", "Shot Quality", min=1, max=5, value=[1, 5])),

    ),
    ui.output_plot("plot1",  width="800px", height="800px"),
    # ui.output_plot("plot1"),
    # ui.row(
    #    ui.column(10,ui.output_plot("plot1")),
    # ),
)

def server(input, output, session):

    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        print(input.shot_hand())
        dfc = df[df["half"].isin(input.half())]
        dfc = dfc[(dfc["minutes_left"]>=input.mins_left()[0]) & (dfc["minutes_left"]<=input.mins_left()[1])]
        dfc = dfc[(dfc["shot_clock"]>=input.shot_clock()[0]) & (dfc["shot_clock"]<=input.shot_clock()[1])]
        dfc = dfc[dfc["shot_type"].isin(input.shot_type())]
        dfc = dfc[dfc["shot_movement"].isin(input.shot_mov())]
        dfc = dfc[dfc["playtype"].isin(input.playtype())]
        dfc = dfc[dfc["cns_otd"].isin(input.cns_otd())]
        dfc = dfc[dfc["contested_uncontested"].isin(input.con_uncon())]
        dfc = dfc[dfc["shot_handedness"].isin(input.shot_hand())]
        dfc = dfc[dfc["dribble_handedness"].isin(input.drib_hand())]
        dfc = dfc[(dfc["shot_quality"]>=input.shot_quality()[0]) & (dfc["shot_quality"]<=input.shot_quality()[1])]
        dfc = dfc.reset_index()
        return dfc
    
    @render.plot(alt="Shot Chart")
    def plot1():
        dfs = filtered_df()
        df_make = dfs[dfs['make_miss']== 'Make']
        df_miss = dfs[dfs['make_miss']== 'Miss']
        fig,ax = plt.subplots(1,1,figsize=(20, 20))
        ax.set_xlim(0, 600)
        ax.set_ylim(564, 0)
        # ax.set_facecolor(bball_white)
        # fig.set_facecolor(bball_white)
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        draw_court(ax=ax, lw=3, color=bball_gray)
        ax.scatter(x=df_make.x, y=df_make.y, marker = "o", facecolors="g", s=25, linewidths=2)
        ax.scatter(x=df_miss.x, y=df_miss.y, marker = "x", facecolors="r", s=25, linewidths=2)

        return fig


app = App(app_ui, server)