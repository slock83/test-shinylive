import mimetypes


from shiny import App, render, ui
from shiny import Inputs, Outputs, Session
import plotly.offline as py
import plotly.graph_objects as go
import pandas as pd

MAX_SIZE = 1000

app_ui = ui.page_fluid(
    ui.h3("Dataviz"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file(
                "data_in",
                "Ouvrir un fichier",
                button_label="Explorer...",
                placeholder="Aucun fichier choisi",
                multiple=True),
        ),
        ui.panel_main(
            #ui.output_text_verbatim("file_content"),
            ui.output_ui("tst")
        )
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def file_content():
        
        file_infos = input.data_in()
        if not file_infos:
            return

        # file_infos is a list of dicts; each dict represents one file. Example:
        # [
        #   {
        #     'name': 'data.csv',
        #     'size': 2601,
        #     'type': 'text/csv',
        #     'datapath': '/tmp/fileupload-1wnx_7c2/tmpga4x9mps/0.csv'
        #   }
        # ]
        out_str = ""
        for file_info in file_infos:
            out_str += (
                "=" * 47
                + "\n"
                + file_info["name"]
                + "\nMIME type: "
                + str(mimetypes.guess_type(file_info["name"])[0])
            )
            if file_info["size"] > MAX_SIZE:
                out_str += f"\nTruncating at {MAX_SIZE} bytes."

            out_str += "\n" + "=" * 47 + "\n"

            with open(file_info["datapath"], "r") as f:
                out_str += f.read(MAX_SIZE)

        return out_str

    @output
    @render.ui
    def tst():
        file_infos = input.data_in()
        if not file_infos:
            return
        for f in file_infos:
            df = pd.read_csv(f["datapath"])
            df.index = df[df.columns[0]]
            df = df[[x for x in df.columns[1:]]]
        t = []
        for col in df.columns:
            t.append(go.Scatter(
                x=df.index,
                y=df[col],
                name=col
            ))
        return ui.HTML(py.plot(t, output_type="div"))


app = App(app_ui, server)
