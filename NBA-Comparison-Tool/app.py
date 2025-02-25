import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine.ggplot import ggplot
from plotnine import geom_density

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

connections = str(get_viewcount())


data_DIR = "/var/data/shiny/"

img_DIR = data_DIR + "player_images/"

df = pd.read_parquet(data_DIR + "NBA_Player_Comparison_V3_2024.parquet")

questions = [
    "How often do you shoot the ball?",
    "How skilled of a finisher are you?",
    "How skilled of a midrange shooter are you?",
    "How skilled of a pullup 3pt shooter are you?",
    "How skilled of a spotup 3pt shooter are you?",
    "How skilled are you at creating your own shot?",
    "How often do you have the ball in your hands?",
    "How willing/active of a passer are you?",
    "How versatile of a passer are you?",
    "How turnover prone are you? (0: alot 100: not much)",
    "How much do you contribute to your team's offense overall?",
    "How often do you guard the other team's best player(s)?",
    "How good is your perimeter defense on the ball?",
    "How good is your defense in the passing lanes?",
    "How skilled of a rim protector are you?",
    "How active of a help defender are you?",
    "How skilled of an offensive rebounder are you?",
    "How skilled of a defensive rebounder are you?",
    "How often do you drive to the basket?",
    "How often do you post up?",
]

app_ui = ui.page_fluid(
    # ui.head_content(ui.include_js("gtag.js",method="inline")),
    ui.card(
    ui.panel_title("NBA Pickup Comparison Finder v3.0"),
        ui.card_footer(ui.markdown("""
                **Data and Idea**: [automaticnba](https://twitter.com/automaticnba/) | 
                **Application**: [Sravan](https://twitter.com/sradjoker/) | 
                **App Views**: {0}
            """.format(ui.output_text("views",inline=True))
            )
        )
    ),
    # ui.h2("NBA Comparision Tool"),
    ui.card(
        ui.markdown(""" 
            Simply answer these **20 basic questions** about your basketball ability to 
            see which NBA players from **2016-17** to **2023-24** your skills most match with  
                           
            Comparing to players with at least **500** minutes played during a season | 
            Data updated till **2023-24** NBA Season
            """
        ),
    
    ),
    ui.row(
        ui.column(4,ui.input_slider( "q0", questions[0], 0, 100, 50)),
        ui.column(4,ui.input_slider( "q1", questions[1], 0, 100, 50)),
        ui.column(4,ui.input_slider( "q2", questions[2], 0, 100, 50)),
    ),
    ui.row(
        ui.column(4, ui.input_slider( "q3", questions[3], 0, 100, 50)),
        ui.column(4, ui.input_slider( "q4", questions[4], 0, 100, 50)),
        ui.column(4, ui.input_slider( "q5", questions[5], 0, 100, 50)),
    ),
    ui.row(
        ui.column(4, ui.input_slider( "q6", questions[6], 0, 100, 50)),
        ui.column(4, ui.input_slider( "q7", questions[7], 0, 100, 50)),
        ui.column(4, ui.input_slider( "q8", questions[8], 0, 100, 50)),
    ),
    ui.row(
        ui.column(4, ui.input_slider( "q9", questions[9], 0, 100, 50)),
        ui.column(4, ui.input_slider( "q10", questions[10], 0, 100, 50)),
        ui.column(4, ui.input_slider("q11", questions[11], 0, 100, 50)),
    ),
    ui.row(
        ui.column(4, ui.input_slider("q12", questions[12], 0, 100, 50)),
        ui.column(4, ui.input_slider("q13", questions[13], 0, 100, 50)),
        ui.column(4, ui.input_slider("q14", questions[14], 0, 100, 50)),
    ),
    ui.row(
        ui.column(4, ui.input_slider("q15", questions[15], 0, 100, 50)),
        ui.column(4, ui.input_slider("q16", questions[16], 0, 100, 50)),
        ui.column(4, ui.input_slider("q17", questions[17], 0, 100, 50)),
    ),
    ui.row(
        ui.column(4, ui.input_slider("q18", questions[18], 0, 100, 50)),
        ui.column(4, ui.input_slider("q19", questions[19], 0, 100, 50)),
        # ui.column(4, ui.input_slider("q17", questions[17], 0, 100, 50)),
    ),
    ui.layout_column_wrap(
        ui.value_box(
            "Player Most Similar to you is:",
            ui.output_text("similar_player"),
            ui.output_text("similar_year"),
            theme="purple",
            showcase=ui.output_image("image",inline=True),
            # showcase_layout="bottom",
        ),
        width = 1/2,
    ),
    # ui.card(
    #     ui.card_header("Player most similar to you is:"),
    #     ui.output_text_verbatim("similar_player"),
    # ),
    ui.card(
        ui.card_header(ui.h4("Similarity Table")),
        ui.output_data_frame("similarity_score"),
    ),
)


def server(input, output, session):

    @render.text
    def views():
        txt = str(get_viewcount())
        return txt
    
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        inputs = [
            input.q0(),
            input.q1(),
            input.q2(),
            input.q3(),
            input.q4(),
            input.q5(),
            input.q6(),
            input.q7(),
            input.q8(),
            input.q9(),
            input.q10(),
            input.q11(),
            input.q12(),
            input.q13(),
            input.q14(),
            input.q15(),
            input.q16(),
            input.q17(),
            input.q18(),
            input.q19(),
        ]
        df1 = df.copy()
        entry = np.array(inputs)
        matrix = df1.iloc[:,4:].to_numpy()
        smat = matrix - entry
        # norm = np.linalg.norm(smat, ord=2, axis=1) 
        # df1["Similarity Score"] = 100-np.round(norm/20,1)
        norm = np.linalg.norm(smat, ord=1, axis=1) 
        df1["Similarity Score"] = 100-np.round(norm/20,1)
        df1 = df1.nlargest(10,"Similarity Score")

        return df1
    
    @render.data_frame
    def similarity_score():
        display_df = filtered_df()
        return render.DataGrid(display_df, filters=False)
        # return render.table(display_df)

    @render.text
    def similar_player():
        text_df = filtered_df()
        txt = str(text_df.iloc[0,2])
        return f"{txt}"

    @render.text
    def similar_year():
        text_df = filtered_df()
        txt = str(text_df.iloc[0,1]) 
        return f"{txt}"

    
    @render.text
    def similar_pID():
        text_df = filtered_df()
        pID = str(text_df.iloc[0,0])
        # img = f'<img src="https://cdn.nba.com/headshots/nba/latest/260x190/{pID}.png" alt="alternatetext">'
        return pID

    @render.image
    def image():
        from pathlib import Path

        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(img_DIR) + str(similar_pID()) + ".png", "height": "80px"}
        return img

app = App(app_ui, server)
