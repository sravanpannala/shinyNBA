from typing import Callable

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import date
import asyncio

from shiny import Inputs, Outputs, Session, module, render, ui, reactive


def ui_func(stats_str,ops_str):
    app_ui = ui.page_fluid(
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
                ui.column(3,ui.input_action_button("go", "Go!", class_="btn-success")),
                ui.column(3,ui.download_button(id="downloadData", label="Download")),
            ),
        ),
        ui.output_data_frame("df_display"),
    )
    return app_ui


@module.ui
def player_box_ui(stats_str: str,ops_str: str):
    return ui.nav_panel(
            ui.h4("NBA Player Box Scores"),
            ui.page_fluid(
                ui.card(
                    ui.panel_title(ui.h4("Instructions")),
                    ui.markdown(""" 
                        **Available stats**: {0}  
                        **Available operators**: {1}  
                        Write down the stat name, then the operator and the value. You can use "," as a separator for multiple queries.          
                        """.format(stats_str,ops_str)
                    ), 
                    ui.row(
                        ui.column(12, ui.input_text("query1",ui.h4("Query Box"),value="season >=1984, pts >=60",width="80%")),
                    ),
                    ui.row(
                        ui.column(3,ui.input_action_button("go1", "Go!", class_="btn-success")),
                        ui.column(3,ui.download_button(id="downloadData1", label="Download")),
                    ),
                ),
                ui.output_data_frame("df_display1"),
            )   
    )

@module.ui
def player_season_ui(stats_str: str,ops_str: str):
    return ui.nav_panel(
            ui.h4("NBA Player Season"),
            ui.page_fluid(
                ui.card(
                    ui.panel_title(ui.h4("Instructions")),
                    ui.markdown(""" 
                        **Available stats**: {0}  
                        **Available operators**: {1}  
                        Write down the stat name, then the operator and the value. You can use "," as a separator for multiple queries.          
                        """.format(stats_str,ops_str)
                    ), 
                    ui.row(
                        ui.column(12, ui.input_text("query2",ui.h4("Query Box"),value="season >=1984, pts >=30",width="80%")),
                    ),
                    ui.row(
                        ui.column(3,ui.input_action_button("go2", "Go!", class_="btn-success")),
                        ui.column(3,ui.download_button(id="downloadData2", label="Download")),
                    ),
                ),
                ui.output_data_frame("df_display2"),
            )   
    )

@module.ui
def player_box_ui_w(stats_str: str,ops_str: str):
    return ui.nav_panel(
            ui.h4("WNBA Player Box Scores"),
            ui.page_fluid(
                ui.card(
                    ui.panel_title(ui.h4("Instructions")),
                    ui.markdown(""" 
                        **Available stats**: {0}  
                        **Available operators**: {1}  
                        Write down the stat name, then the operator and the value. You can use "," as a separator for multiple queries.          
                        """.format(stats_str,ops_str)
                    ), 
                    ui.row(
                        ui.column(12, ui.input_text("query3",ui.h4("Query Box"),value="season >=1997, pts >=40",width="80%")),
                    ),
                    ui.row(
                        ui.column(3,ui.input_action_button("go3", "Go!", class_="btn-success")),
                        ui.column(3,ui.download_button(id="downloadData3", label="Download")),
                    ),
                ),
                ui.output_data_frame("df_display3"),
            )   
    )

@module.ui
def player_season_ui_w(stats_str: str,ops_str: str):
    return ui.nav_panel(
            ui.h4("WNBA Player Season"),
            ui.page_fluid(
                ui.card(
                    ui.panel_title(ui.h4("Instructions")),
                    ui.markdown(""" 
                        **Available stats**: {0}  
                        **Available operators**: {1}  
                        Write down the stat name, then the operator and the value. You can use "," as a separator for multiple queries.          
                        """.format(stats_str,ops_str)
                    ), 
                    ui.row(
                        ui.column(12, ui.input_text("query4",ui.h4("Query Box"),value="season >=1997, pts >=20",width="80%")),
                    ),
                    ui.row(
                        ui.column(3,ui.input_action_button("go4", "Go!", class_="btn-success")),
                        ui.column(3,ui.download_button(id="downloadData4", label="Download")),
                    ),
                ),
                ui.output_data_frame("df_display4"),
            )   
    )

# @module.ui
# def player_season_ui(stats_str: str,ops_str: str):
#     return ui.nav_panel(
#             "Player Season",
#             ui_func(stats_str,ops_str)    
#     )

@module.server
def player_box_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: DataFrame,
):
    @reactive.Calc
    def filtered_df1() -> pd.DataFrame:
        qstr1 = input.query1()
        qstr = qstr1.replace(","," & ")
        qstr = qstr.lower()
        dfc = df.query(qstr)

        return dfc
    
    @render.data_frame
    @reactive.event(input.go1, ignore_none=False)
    def df_display1():
        display_df = filtered_df1()
        return render.DataGrid(display_df, filters=False)
    
    @session.download(
        filename=lambda: f"stats_query-{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData1():
        await asyncio.sleep(0.25)
        yield filtered_df1().to_csv()

@module.server
def player_season_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: DataFrame,
):
    @reactive.Calc
    def filtered_df2() -> pd.DataFrame:
        qstr1 = input.query2()
        qstr = qstr1.replace(","," & ")
        qstr = qstr.lower()
        dfc = df.query(qstr)

        return dfc
    
    @render.data_frame
    @reactive.event(input.go2, ignore_none=False)
    def df_display2():
        display_df = filtered_df2()
        return render.DataGrid(display_df, filters=False)
    
    @session.download(
        filename=lambda: f"stats_query-{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData2():
        await asyncio.sleep(0.25)
        yield filtered_df2().to_csv()

@module.server
def player_box_server_w(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: DataFrame,
):
    @reactive.Calc
    def filtered_df3() -> pd.DataFrame:
        qstr1 = input.query3()
        qstr = qstr1.replace(","," & ")
        qstr = qstr.lower()
        dfc = df.query(qstr)

        return dfc
    
    @render.data_frame
    @reactive.event(input.go3, ignore_none=False)
    def df_display3():
        display_df = filtered_df3()
        return render.DataGrid(display_df, filters=False)
    
    @session.download(
        filename=lambda: f"stats_query-{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData3():
        await asyncio.sleep(0.25)
        yield filtered_df3().to_csv()

@module.server
def player_season_server_w(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: DataFrame,
):
    @reactive.Calc
    def filtered_df4() -> pd.DataFrame:
        qstr1 = input.query4()
        qstr = qstr1.replace(","," & ")
        qstr = qstr.lower()
        dfc = df.query(qstr)

        return dfc
    
    @render.data_frame
    @reactive.event(input.go4, ignore_none=False)
    def df_display4():
        display_df = filtered_df4()
        return render.DataGrid(display_df, filters=False)
    
    @session.download(
        filename=lambda: f"stats_query-{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData4():
        await asyncio.sleep(0.25)
        yield filtered_df4().to_csv()