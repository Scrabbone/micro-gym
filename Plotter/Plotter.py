from bokeh.models.axes import LinearAxis
from bokeh.plotting import figure, show, save, output_file
from bokeh.io import curdoc
from bokeh.models.tools import HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, ZoomInTool, ZoomOutTool
from bokeh.models import BoxAnnotation, LinearAxis, Range1d
import pandas as pd

db_10_000 = pd.read_csv("trained_csv/model_10_000.csv")
db_25_000 = pd.read_csv("trained_csv/model_25_000.csv")
db_75_000 = pd.read_csv("trained_csv/model_75_000.csv")
db_125_000 = pd.read_csv("trained_csv/model_125_000.csv")
db_250_000 = pd.read_csv("trained_csv/model_250_000.csv")
db_500_000 = pd.read_csv("trained_csv/model_500_000.csv")
db_750_000 = pd.read_csv("trained_csv/model_750_000.csv")
db_random = pd.read_csv("trained_csv/random.csv")

#Konfigurieren und Erstellen des Plots
curdoc().theme = "light_minimal"
wheel_zoom_tool = WheelZoomTool()

plot = figure(title="Trained Model comparison",
sizing_mode="stretch_both",
x_axis_label='Episode',
y_axis_label='Reward-Sum in episode',
tools=[HoverTool(), BoxZoomTool(), ResetTool(), PanTool(), wheel_zoom_tool, SaveTool(), ZoomOutTool(dimensions="height"), ZoomInTool(dimensions="height")],
tooltips="Datenpunkt @x hat den Wert @y")

x = []
y = []
index = 0
for reward in db_10_000['model_sum_rewards']:
    x.append(index)
    y.append(db_10_000['model_sum_rewards'].iloc[index])
    index+=1

#Hauptkurve
plot.line(x,db_10_000["model_sum_rewards"], line_width=4, legend_label="Model 10_000", line_color="blue")
plot.line(x,db_25_000["model_sum_rewards"], line_width=4, legend_label="Model 25_000", line_color="yellow")
plot.line(x,db_75_000["model_sum_rewards"], line_width=4, legend_label="Model 75_000", line_color="green")
plot.line(x,db_125_000["model_sum_rewards"], line_width=4, legend_label="Model 125_000", line_color="purple")
plot.line(x,db_250_000["model_sum_rewards"], line_width=4, legend_label="Model 250_000", line_color="black")
plot.line(x,db_500_000["model_sum_rewards"], line_width=4, legend_label="Model 500_000", line_color="brown")
plot.line(x,db_750_000["model_sum_rewards"], line_width=4, legend_label="Model 750_000", line_color="orange")
plot.line(x,db_random["random_sum_rewards"], line_width=4, legend_label="Random", line_color="red")

plot.legend.location = "top_left"
plot.legend.click_policy = "hide"
plot.legend.label_text_font = "sans-serif"
plot.legend.label_text_font_size = "10pt"

plot.axis.axis_label_text_font_size = "30pt"

save(plot)