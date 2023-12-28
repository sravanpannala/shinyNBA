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
    # theme_538,
    guide_legend,
    guides,
    element_text,
    element_blank,
    element_rect,
    scale_fill_manual,
    scale_x_continuous,
    # scale_x_discrete,
    scale_y_continuous,
    geom_point,
    geom_smooth,
    scale_color_manual,
    # facet_wrap,
)
from mizani.formatters import percent_format

# import matplotlib as mpl
# import shutil
# shutil.rmtree(mpl.get_cachedir())


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

df = pd.read_parquet(data_DIR + "NBA_Player_Distribution.parquet")

players = list(df["Player"].unique())
players.append("None")
seasons = list(df["Season"].astype(str).unique())
vars = [
        'Pts', 'Min', 'FGM', 'FGA', 'FG %', 'FG3M', 'FG3A',
        'FG3 %', 'FTM', 'FTA', 'FT %', 'OReb', 'DReb', 'Reb', 'Ast', 'Stl',
        'Blk', 'Tov', 'PF' , 'Plus Minus', 'ORtg', 'DRtg', 'NetRtg',
        'Ast %', 'Ast/Tov', 'Ast Ratio', 'OReb %', 'DReb %', 'Reb %',
        'Tov Ratio', 'eFG %', 'TS %', 'USG %', 'Pace', 'Poss', 'PIE',
        'Off Poss', 'Def Poss', 'Drives', 'Drive FGM', 'Drive FGA', 'Drive FTM',
        'Drive FTA', 'Drive Points', 'Drive Passes', 'Drive Asts', 'Drive Tovs',
        'Drive Fouls', 'Passes Made', 'Passes Received', 'FT Asts',
        'Secondary Asts', 'Potential Asts',
        'Adj Asts', 'Ast Pts', 'Def Rim FGM', 'Def Rim FGA', 'Touches',
        'Front Court Touches', 'Time Of Poss', 'Seconds Per Touch',
        'Dribbles Per Touch', 'Elbow Touches', 'Elbow Touch FGM',
        'Elbow Touch FGA', 'Elbow Touch FTM', 'Elbow Touch FTA',
        'Elbow Touch Points', 'Elbow Touch Passes', 'Elbow Touch Asts',
        'Elbow Touch Tovs', 'Elbow Touch Fouls', 'Paint Touches',
        'Paint Touch FGM', 'Paint Touch FGA', 'Paint Touch FTM',
        'Paint Touch FTA', 'Paint Touch Points', 'Paint Touch Passes',
        'Paint Touch Asts', 'Paint Touch Tovs', 'Paint Touch Fouls',
        'Post Touches',
        'Post Touch FGM', 'Post Touch FGA', 'Post Touch FTM', 'Post Touch FTA',
        'Post Touch Points', 'Post Touch Passes', 'Post Touch Asts',
        'Post Touch Tovs', 'Post Touch Fouls', 'OReb Contest', 'OReb Uncontest',
        'OReb Chances', 'OReb Chance Defer', 'DReb Contest', 'DReb Uncontest',
        'DReb Chances', 'DReb Chance Defer', 'Feet', 'Miles', 'Miles Off',
        'Miles Def', 'Avg Speed', 'Avg Speed Off', 'Avg Speed Def', 'Extra Possessions'
       ]

app_ui = ui.page_fluid(
    # ui.head_content(ui.include_js("gtag.js",method="inline")),
    ui.card(
    ui.panel_title(ui.h2("NBA Player Stat Distribution and Trends")),
        ui.card_footer(ui.h5(ui.markdown("""
                **By**: [SravanNBA](https://twitter.com/SravanNBA/) | **App views**: {0}
            """.format(connections)
            ))
        )
    ),
    ui.card(
        ui.markdown(""" 
            Plotting Density & Trends for various boxscores stats for a players from **2013-Current**.  
            Higher the Density (probability of the event to occur), the more frequent that event is. You can read more about density plots [here](https://en.wikipedia.org/wiki/Kernel_density_estimation)  
            This app is inspired by my NBA Age Distribution tweets: [1](https://twitter.com/SravanNBA/status/1723550795302617520), [2](https://twitter.com/SravanNBA/status/1729870792534724808)  
            [**Glossary of Stats**](https://www.nba.com/stats/help/glossary)
            """
        ),
    
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.row(
                ui.column(12, ui.input_selectize("var","Stat",vars, selected="Pts")),
            ),
            ui.row(
                ui.column(8, ui.input_selectize("player_name1","Player 1",players, selected="LeBron James")),
                ui.column(4, ui.input_selectize("season1","Season",seasons, selected="2024")),
            ),
            ui.row(
                ui.column(8, ui.input_selectize("player_name2","Player 2",players, selected="Giannis Antetokounmpo")),
                ui.column(4, ui.input_selectize("season2","Season",seasons, selected="2024")),
            ),
            ui.row(
                ui.column(8, ui.input_selectize("player_name3","Player 3",players, selected="None")),
                ui.column(4, ui.input_selectize("season3","Season",seasons, selected="2024")),
            ),
            ui.row(
                ui.column(8, ui.input_selectize("player_name4","Player 4",players, selected="None")),
                ui.column(4, ui.input_selectize("season4","Season",seasons, selected="2024")),
            ),
            width = 400,
        ),
        ui.output_plot("plt", width="800px", height="600px"),
        ui.output_plot("plt2", width="800px", height="600px"),
    ),

)

def server(input, output, session):
    # ...
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        p1, s1 = input.player_name1(), input.season1()
        p2, s2 = input.player_name2(), input.season2()
        p3, s3 = input.player_name3(), input.season3()
        p4, s4 = input.player_name4(), input.season4()
        dff1 = df.query(f'(Player == "{p1}" & Season == {s1})')
        dff2 = df.query(f'(Player == "{p2}" & Season == {s2})')
        dff3 = df.query(f'(Player == "{p3}" & Season == {s3})')
        dff4 = df.query(f'(Player == "{p4}" & Season == {s4})')
        dff = pd.concat([dff1,dff2,dff3,dff4])
        # dff["Player Season"] = dff["Player Season"].astype("category")
        # cats = [f"{s1} {p1}", f"{s2} {p2}", f"{s3} {p3}", f"{s4} {p4}"]
        # dff["Player Season"] = dff["Player Season"].cat.set_categories(cats)
        return dff
    
    @render.data_frame
    def output_table():
        display_df = filtered_df()
        display_df = display_df.sort_values(by=["Player","Season","Game Date"])
        return render.DataGrid(display_df, filters=False)

    colors = [
        '#0057e7',
        '#d62d20',
        '#008744',
        '#ffa700',
        # '#f4522b',
        '#4d1b7b',
    ]
    
    @render.plot(alt="Player Stat Distribution")
    def plt():
        df1 = filtered_df()
        var = input.var()
        scale_x = []
        kwargs_legend = {"alpha":0.0}
        if "%" in var:
            scale_x = scale_x_continuous(labels=percent_format())
            if var == "FT %":
                limits = [.50,1.00]
                scale_x = scale_x_continuous(labels=percent_format(), limits = limits)
        elif var in ["ORtg","DRtg"]:
            x_breaks = np.arange(90,140,5)
            x_labels = list(x_breaks.astype(str))
            # scale_x = scale_x_continuous(breaks=x_breaks, labels= x_labels, limits = [x_breaks[0],x_breaks[-1]])
            scale_x = scale_x_continuous(limits = [x_breaks[0],x_breaks[-1]])
        elif var in ["NRtg"]:
            x_breaks = np.arange(-25,25,5)
            x_labels = list(x_breaks.astype(str))
            scale_x = scale_x_continuous(breaks=x_breaks, labels= x_labels, limits = [x_breaks[0],x_breaks[-1]])
        plot = (
            ggplot(df1)  
            + geom_density(
                aes(x=var,fill="Player Season"),
                alpha=0.5,
            )
            + scale_fill_manual(values=colors)
            + scale_x
            + labs(
                x=var,
                y="Density",
                title=f"NBA Stat Distribution:  {var}",
                caption="@SravanNBA | source: nba.com/stats",
            )
            + theme_xkcd(base_size=14)
            # + theme_538(base_size=12)
            + theme(
                plot_title=element_text(face="bold", size=22),
                plot_subtitle=element_text(size=14),
                plot_margin=0.025,
                figure_size=[8,6]
            )
            + theme(
                legend_title=element_blank(),
                legend_position = [0.80,0.78],
                legend_box_margin=0,
                legend_background=element_rect(color="grey", size=0.001,**kwargs_legend),
                legend_box_background = element_blank(),
                legend_text=element_text(size=13),
            )
            +  guides(fill=guide_legend(ncol=1))
        )
    
        return plot

    @render.plot(alt="Player Stat Mean")
    def plt2():
        df1 = filtered_df()
        var = input.var()
        scale_y = []
        kwargs_legend = {"alpha":0.0}
        if "%" in var:
            scale_y = scale_y_continuous(labels=percent_format())
            if var == "FT %":
                limits = [.50,1.00]
                scale_y = scale_y_continuous(labels=percent_format(), limits = limits)
        elif var in ["ORtg","DRtg"]:
            x_breaks = np.arange(90,140,5)
            x_labels = list(x_breaks.astype(str))
            # scale_y = scale_y_continuous(breaks=x_breaks, labels= x_labels, limits = [x_breaks[0],x_breaks[-1]])
            scale_y = scale_y_continuous(limits = [x_breaks[0],x_breaks[-1]])
        elif var in ["NRtg"]:
            x_breaks = np.arange(-25,25,5)
            x_labels = list(x_breaks.astype(str))
            scale_y = scale_y_continuous(breaks=x_breaks, labels= x_labels, limits = [x_breaks[0],x_breaks[-1]])
        plot = (
            ggplot(df1,aes(x="Games Played",y=var,color="Player Season"))  
            + geom_point()
            + geom_smooth(size=2,se=False,method="lowess",span=0.4)
            # + facet_wrap(facets = "~ Player Season",ncol=1)
            + scale_color_manual(values=colors)
            + scale_y
            + labs(
                x="Games Played",
                y=var,
                title=f"NBA Stat Trends:  {var}",
                caption="@SravanNBA | source: nba.com/stats",
            )
            + theme_xkcd(base_size=14)
            # + theme_538(base_size=14)
            + theme(
                plot_title=element_text(face="bold", size=22),
                plot_subtitle=element_text(size=14),
                plot_margin=0.025,
                figure_size=[8,6]
            )
            + theme(
                legend_title=element_blank(),
                legend_position = [0.32,0.78],
                legend_box_margin=0,
                legend_background=element_rect(color="grey", size=0.001,**kwargs_legend),
                legend_box_background = element_blank(),
                legend_text=element_text(size=13),
            )
            +  guides(color=guide_legend(ncol=1))
        )
    
        return plot  

    
app = App(app_ui, server)
