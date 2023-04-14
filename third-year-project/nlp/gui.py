import PySimpleGUI as sg
import pandas as pd
from wordcloud import WordCloud
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

data = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                    "Data\\final_results.h5", key="final2")
albums = data.loc[:, "Album"].unique()

layout = [[sg.Input(do_not_clear=True, size=(20, 1), enable_events=True, key="Search")],
          [sg.Listbox(albums, size=(20, 4), enable_events=True, key="List")],
          [sg.Canvas(key="Canvas")]]

# Create the window
window = sg.Window("Album Search", layout)

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


fig_agg = None

# Create an event loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    elif values["Search"] != "":
        search = values["Search"]
        matches = [album for album in albums if search.lower() in album]
        window.Element("List").Update(matches)
    else:
        window.Element("List").Update(albums)
    if event == "List" and len(values["List"]) is not None:
        selected_album = values["List"][0]
        words = data.loc[data["Album"] == selected_album, ["Text", "pos_prob"]]
        words = (words
                 .set_index(words.loc[:, "Text"])
                 .drop(columns="Text")
                 .squeeze()
                 .to_dict())
        word_cloud = WordCloud(width=800, height=400, colormap="Blues", relative_scaling=1).generate_from_frequencies(words)
        if fig_agg is not None:
            fig_agg.get_tk_widget().forget()
            plt.close("all")
        fig = plt.figure(figsize=(18, 10))
        plt.imshow(word_cloud)
        canvas = window.Element("Canvas").TKCanvas
        fig_agg = draw_figure(canvas, fig)
        window.maximize()

window.close()
