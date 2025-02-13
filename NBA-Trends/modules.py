from typing import Callable

import pandas as pd
from pandas import DataFrame
from plots import plt_dist, plt_trends

from shiny import Inputs, Outputs, Session, module, render, ui, reactive


@module.ui
def player_test_ui(vars: list[str],players: list[str],seasons: list[str]):
    return ui.nav_panel(
            "Players",
            ui.page_fluid(
                # ui.head_content(ui.include_js("gtag.js",method="inline")),
                ui.card(
                    ui.panel_title(ui.h2("NBA Player Stat Distribution and Trends")),
                    ui.card_footer(ui.h5(ui.markdown("""
                            **By**: [Sravan](https://x.com/SravanNBA/)
                        """
                        ))
                    )
                ),
            )
    )
    


@module.ui
def player_dist_ui(vars: list[str],players: list[str],seasons: list[str]):
    return ui.nav_panel(
        ui.h3("Players"),
        ui.page_fluid(
            ui.layout_sidebar(
                ui.sidebar(
                    ui.row(
                        ui.column(12, ui.input_selectize("var","Stat",vars, selected="Pts")),
                    ),
                    ui.row(
                        ui.column(8, ui.input_selectize("player_name1","Player 1",players, selected="LeBron James")),
                        ui.column(4, ui.input_selectize("season1","Season",seasons, selected="2025")),
                    ),
                    ui.row(
                        ui.column(8, ui.input_selectize("player_name2","Player 2",players, selected="Giannis Antetokounmpo")),
                        ui.column(4, ui.input_selectize("season2","Season",seasons, selected="2025")),
                    ),
                    ui.row(
                        ui.column(8, ui.input_selectize("player_name3","Player 3",players, selected="None")),
                        ui.column(4, ui.input_selectize("season3","Season",seasons, selected="2025")),
                    ),
                    ui.row(
                        ui.column(8, ui.input_selectize("player_name4","Player 4",players, selected="None")),
                        ui.column(4, ui.input_selectize("season4","Season",seasons, selected="2025")),
                    ),
                    width = 400,
                ),
                ui.output_plot("player_dist", width="800px", height="600px"),
                ui.output_plot("player_trends", width="800px", height="600px"),
            ),

        )
    )

@module.ui
def team_dist_ui(vars: list[str],teams: list[str],seasons: list[str]):
    return ui.nav_panel(
        ui.h3("Teams"),
        ui.page_fluid(
            ui.layout_sidebar(
                ui.sidebar(
                    ui.row(
                        ui.column(12, ui.input_selectize("vart","Stat",vars, selected="Pts")),
                    ),
                    ui.row(
                        ui.column(8, ui.input_selectize("team_name1","Team 1",teams, selected="Denver Nuggets")),
                        ui.column(4, ui.input_selectize("season1t","Season",seasons, selected="2025")),
                    ),
                    ui.row(
                        ui.column(8, ui.input_selectize("team_name2","Team 2",teams, selected="Miami Heat")),
                        ui.column(4, ui.input_selectize("season2t","Season",seasons, selected="2025")),
                    ),
                    ui.row(
                        ui.column(8, ui.input_selectize("team_name3","Team 3",teams, selected="None")),
                        ui.column(4, ui.input_selectize("season3t","Season",seasons, selected="2025")),
                    ),
                    ui.row(
                        ui.column(8, ui.input_selectize("team_name4","Team 4",teams, selected="None")),
                        ui.column(4, ui.input_selectize("season4t","Season",seasons, selected="2025")),
                    ),
                    width = 400,
                ),
                ui.output_plot("team_dist", width="800px", height="600px"),
                ui.output_plot("team_trends", width="800px", height="600px"),
            ),

        )
    )


@module.server
def player_dist_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: DataFrame,
):
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
        dff["Player Season"] = dff["Player Season"].astype("category")
        cats = []
        if p1 != "None":
            cats.append(f"{s1} {p1}")
        if p2 != "None":
            cats.append(f"{s2} {p2}")
        if p3 != "None":
            cats.append(f"{s3} {p3}")
        if p4 != "None":
            cats.append(f"{s4} {p4}")
        dff["Player Season"] = dff["Player Season"].cat.set_categories(cats)
        return dff
    
    @render.plot(alt="Player Stat Distribution")
    def player_dist():
        df1 = filtered_df()
        var = input.var()
        group = "Player Season"
        return plt_dist(df1,var,group)
    
    @render.plot(alt="Player Stat Trends")
    def player_trends():
        df1 = filtered_df()
        var = input.var()
        group = "Player Season"
        return plt_trends(df1,var,group)

@module.server
def team_dist_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: DataFrame,
):
    @reactive.Calc
    def filtered_dft() -> pd.DataFrame:
        t1, s1 = input.team_name1(), input.season1t()
        t2, s2 = input.team_name2(), input.season2t()
        t3, s3 = input.team_name3(), input.season3t()
        t4, s4 = input.team_name4(), input.season4t()
        dff1 = df.query(f'(Team == "{t1}" & Season == {s1})')
        dff2 = df.query(f'(Team == "{t2}" & Season == {s2})')
        dff3 = df.query(f'(Team == "{t3}" & Season == {s3})')
        dff4 = df.query(f'(Team == "{t4}" & Season == {s4})')
        dff = pd.concat([dff1,dff2,dff3,dff4])
        dff["Team Season"] = dff["Team Season"].astype("category")
        cats = []
        if t1 != "None":
            cats.append(f"{s1} {t1}")
        if t2 != "None":
            cats.append(f"{s2} {t2}")
        if t3 != "None":
            cats.append(f"{s3} {t3}")
        if t4 != "None":
            cats.append(f"{s4} {t4}")
        dff["Team Season"] = dff["Team Season"].cat.set_categories(cats)
        return dff
    
    @render.plot(alt="Team Stat Distribution")
    def team_dist():
        df1 = filtered_dft()
        var = input.vart()
        group = "Team Season"
        return plt_dist(df1,var,group)
    
    @render.plot(alt="Team Stat Trends")
    def team_trends():
        df1 = filtered_dft()
        var = input.vart()
        group = "Team Season"
        return plt_trends(df1,var,group)
