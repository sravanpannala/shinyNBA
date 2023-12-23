
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine.ggplot import ggplot
from plotnine import geom_density

from shiny import App, ui, render, reactive

data_DIR = "/var/data/shiny/"

df = pd.read_csv(data_DIR + "NBA_Player_Comparison.csv")
df = df.drop(columns=["Blank"])

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
    "How turnover prone are you?",
    "How much do you contribute to your team's offense overall?",
    "How often do you guard the other team's best player(s)?",
    "How good is your perimeter defense on the ball?",
    "How good is your defense in the passing lanes?",
    "How skilled of a rim protector are you?",
    "How active of a help defender are you?",
    "How skilled of an offensive rebounder are you?",
    "How skilled of a defensive rebounder are you?"
]

app_ui = ui.page_fluid(
    ui.card(
    ui.panel_title("NBA Comparision Tool"),
        ui.card_footer(ui.markdown("""
                **Data and Idea**: [automaticnba](https://twitter.com/automaticnba/) | **Application**: [SravanNBA](https://twitter.com/SravanNBA/)
            """
            )
        )
    ),
    # ui.h2("NBA Comparision Tool"),
    ui.card(
        ui.markdown(""" 
            Simply answer these 18 basic questions about your basketball ability to 
            see which NBA players from 2016-17 to 2022-23 your skills most match with  
            **Numbers for 2023-24 not available yet**  
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
    ui.layout_column_wrap(
        ui.value_box(
            "Player Most Similar to you is:",
            ui.output_text("similar_player"),
            theme="purple",
            full_screen=True,
        ),
    ),
    # ui.card(
    #     ui.card_header("Player most similar to you is:"),
    #     ui.output_text_verbatim("similar_player"),
    # ),
    ui.card(
        ui.card_header("Similarity Table"),
        ui.output_data_frame("similarity_score"),
    ),
)


def server(input, output, session):
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
        ]
        df1 = df.copy()
        entry = np.array(inputs)
        matrix = df1.iloc[:,2:].to_numpy()
        smat = matrix - entry
        norm = np.linalg.norm(smat, axis=1) 
        df1["Similarity Score"] = 100-np.round(np.sqrt(norm)/18*100,1)
        # df1.insert(1,"Similarity Score",df1.pop("Similarity Score"))
        # df1 = df1.sort_values(by="Similarity Score", ascending=False).reset_index(drop=True)
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
        txt = text_df.iloc[0,0]
        return f"{txt}"


app = App(app_ui, server)
