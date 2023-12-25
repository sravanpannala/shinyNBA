import os
import numpy as np
import pandas as pd
from plotnine.ggplot import ggplot
from plotnine import (
    aes,
    labs,
    geom_density,
    theme,
    theme_xkcd,
    theme_538,
    guide_legend,
    guides,
    element_text,
    element_blank,
    scale_fill_manual
)

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

connections = str(get_viewcount())

data_DIR = "/var/data/shiny/"
df = pd.read_parquet(data_DIR + "NBA_Player_Distribution.parquet")

players = list(df["Player"].unique())
seasons = list(df["Season"].astype(str).unique())
vars = ['Pts', 'Min', 'FGM', 'FGA',
       'FG Pct', 'FG3M', 'FG3A', 'FG3 Pct', 'FTM', 'FTA', 'FT Pct', 'OReb',
       'DReb', 'Reb', 'Ast', 'Stl', 'Blk', 'Tov', 'PF']

app_ui = ui.page_fluid(
    # ui.head_content(ui.include_js("gtag.js",method="inline")),
    ui.card(
    ui.panel_title("NBA Player Stat Distribution"),
        ui.card_footer(ui.markdown("""
                **By**: [SravanNBA](https://twitter.com/SravanNBA/) | **App views**: {0}
            """.format(connections)
            )
        )
    ),
    ui.card(
        ui.markdown(""" 
            Plotting Density and comparing them for various boxscores stats for a players from 2004-Current.
            Choose the stat, then player 1 and season, and finally player 2 and season.  
            Higher the Density (probability of the event to occur), the more frequent that event is. You can read more about density plots [here](https://en.wikipedia.org/wiki/Kernel_density_estimation)  
            This app is inspired by my NBA Age Distribution tweets: [1](https://twitter.com/SravanNBA/status/1723550795302617520), [2](https://twitter.com/SravanNBA/status/1729870792534724808)
            """
        ),
    
    ),
    ui.row(
        ui.column(2, ui.input_selectize("var","Stat",vars, selected="Pts")),
        ui.column(3, ui.input_selectize("player_name1","Player 1",players, selected="LeBron James")),
        ui.column(1, ui.input_selectize("season1","Season",seasons, selected="2024")),
        ui.column(3, ui.input_selectize("player_name2","Player 2",players, selected="Giannis Antetokounmpo")),
        ui.column(1, ui.input_selectize("season2","Season",seasons, selected="2024")),

    ),
    ui.output_plot("plt", width="800px", height="600px"),

)

def server(input, output, session):
    # ...
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        dff = df.query(f'(Player == "{input.player_name1()}" & Season == {input.season1()}) | (Player == "{input.player_name2()}" & Season == {input.season2()}) ')

        return dff
    
    @render.data_frame
    def output_table():
        display_df = filtered_df()
        display_df = display_df.sort_values(by=["Player","Season","Game Date"])
        return render.DataGrid(display_df, filters=False)
    
    @render.plot(alt="Player Stat Distribution")
    def plt():
        df1 = filtered_df()
        var = input.var()
        plot = (
            ggplot(df1)  
            + geom_density(
                aes(x=var,fill="Player Season"),
                alpha=0.5,
            )
            + scale_fill_manual(values=["blue","red"])

            + labs(
                x=var,
                y="Density",
                title=f"NBA Stat Distribution: {var}",
                caption="@SravanNBA | source: nba.com/stats",
            )
            + theme_xkcd(base_size=14)
            # + theme_538(base_size=12)
            + theme(
                plot_title=element_text(face="bold", size=20),
                plot_subtitle=element_text(size=14),
                plot_margin=0.025,
                figure_size=[8,6]
            )
            + theme(
                legend_title=element_blank(),
                legend_position = [0.82,0.82],
                legend_box_margin=0,
                legend_background=element_blank(),
                legend_box_background = element_blank(),
            )
            +  guides(fill=guide_legend(ncol=1))
        )
    
        return plot
    
app = App(app_ui, server)
