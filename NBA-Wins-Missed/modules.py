from typing import Callable

import pandas as pd
from pandas import DataFrame
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

from shiny import Inputs, Outputs, Session, module, render, ui, reactive


@module.ui
def league_ui():
    return ui.nav_panel(
            ui.h4("League"),
            ui.page_fluid(
                ui.output_plot("plot",  width="1000px", height="800px"),
                ui.output_data_frame("output_table1"),
            )   
    )

@module.ui
def player_ui():
    return ui.nav_panel(
            ui.h4("Player"),
            ui.page_fluid(
                ui.output_data_frame("output_table2"),
            )   
    )

@module.server
def league_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: DataFrame,
):
    @render.data_frame
    def output_table1():
        display_df = df.drop(columns="colorsTeam")
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
    
@module.server
def player_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: DataFrame,
):
    @render.data_frame
    def output_table2():
        display_df = df
        # display_df.style.background_gradient(axis=0, cmap="PiYG")  
        return render.DataGrid(display_df, filters=True)