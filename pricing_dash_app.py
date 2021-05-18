
"""
Created on Fri Apr 23 20:26:44 2021

@author: LekenoTR
"""
import pandas as pd
import dash
import os
import base64
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output


mapbox_access_token = 'pk.eyJ1IjoidGVib2hvbGVrZW5vIiwiYSI6ImNrbnE3cW9ybjBhN3UycHBmemYxMWVtencifQ.p9ZpEWxK3Hupdklm17QVJg'

xls = pd.ExcelFile(os.getcwd()+'\\Copy of Results_rands_10052021_coordinates.xlsx')
years_list = xls.sheet_names
coordinates_sheet = years_list.pop()
substations = pd.DataFrame()

#combining all the data for different years into a single dataFrame
for index in range(len(years_list)):
    if index == 0:
        substations = pd.read_excel(
            os.getcwd()+'\\Copy of Results_rands_10052021_coordinates.xlsx',
            sheet_name=years_list[0])
        substations['Year'] = int(years_list[0])
    else:
        slaveDataFrame = pd.read_excel(
            os.getcwd()+'\\Copy of Results_rands_10052021_coordinates.xlsx',
            sheet_name=years_list[index])
        slaveDataFrame['Year'] = int(years_list[index])
        substations = substations.append(slaveDataFrame, ignore_index = True)
    
#merging Plants and Assets_name columns
for index in range(len(substations.index)):
    if pd.isnull(substations['Plant'][index]):
        substations['Plant'][index] = substations['Asset_name'][index]
        
del substations['Asset_name'] #removing the Asset_name column after merging
substations.dropna()  #removing empty rows
substations['Marks'] = 1
substations.sort_values(by=['PS_name'], inplace=True)


image_filename = 'logo3.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED],
                suppress_callback_exceptions=True)

logo_card = html.Div(dbc.CardImg(src='data:image/png;base64,{}'.format(encoded_image.decode())))

substations_card = dbc.Card([
    dbc.CardHeader("Power Stations"),
    dbc.CardBody(
        [
            dcc.Dropdown(
                id = 'power-generators',
                options = [
                    {'label': content, 'value': content}
                    for content in substations['PS_name'].unique()
                ],
                value = "", multi = True,
           )
        ] 
    )
])

radio_card = dbc.Card([
    dbc.CardHeader("Select Slider Type"),
    dbc.CardBody(
        [
            dcc.RadioItems(
                id = 'slider-type',
                options = [
                    {'label':'Single Slider', 'value': 'slider'},
                    {'label':'Range Slider', 'value': 'range_slider'}
                ], 
                value = 'range_slider',
                inputStyle={"margin-right": "20px"},
                labelStyle = {'margin-left':'60px', 'margin-right':'40px'}
            )
        ]
    )
])



generic_slider_card = dbc.Card([
    dbc.CardHeader("Study Year"),
    dbc.CardBody(
        [
            radio_card, html.Br(),
            html.Div(id = 'generic-slider-container', children=[])
        ]
    )
])

graph_card = dbc.Card(
    dcc.Graph(id='graph', figure = {}, config={
        'displayModeBar': False, 'scrollZoom': True},style={
            'height':'93vh'})
) 


app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col(
            [
                logo_card, html.Br(), substations_card, html.Br(), generic_slider_card 
            ], width = 4
        ),
            
        dbc.Col(
            [
                html.Br(), graph_card
            ], width = 8
        )
    ], justify = 'around')
    
], fluid = True)


#Output of Generic Slider
@app.callback(Output('generic-slider-container', 'children'),
              Input('slider-type', 'value'))

def update_generic_slider(chosen_slider):
    if chosen_slider == 'range_slider':
        slid = html.Div(
            children = [
                dcc.RangeSlider(
                    id = 'study-years',
                    min = substations["Year"].min(),
                    max = substations["Year"].max(),
                    value = [substations["Year"].min(),substations["Year"].min()+1],
                    dots = True,
                    allowCross = False,
                    disabled = False,
                    pushable = 1,
                    updatemode = 'mouseup',
                    marks = {i: str(i) for i in range(substations["Year"].max()+1)}
                )
            ]
        )
        return slid
    
    elif chosen_slider == 'slider':
        slid = html.Div(
            children = [
                dcc.Slider(
                    id = 'study-years',
                    min = substations["Year"].min(),
                    max = substations["Year"].max(),
                    value = substations["Year"].min(),
                    marks = {i: str(i) for i in range(substations["Year"].max()+1)},
                    included = False
                )
            ]
         ) 
        return slid

# Output of Graph
@app.callback(Output('graph', 'figure'),
              [Input('power-generators', 'value'),
               Input('study-years', 'value'),
               Input('slider-type', 'value')])

def update_figure(chosen_generator,chosen_study_years, chosen_slider):
    
    substations_copy = substations
    
    if bool(chosen_generator):
        substations_copy = substations_copy[substations_copy['PS_name'].isin(chosen_generator)]
    
    if chosen_slider == 'range_slider':
        substations_final =  substations_copy[
            (substations_copy['Year'] >= chosen_study_years[0])&(
                substations_copy['Year'] <= chosen_study_years[1])]
        
    elif chosen_slider == 'slider':
        substations_final = substations_copy[
            substations_copy['Year'] == chosen_study_years]
    
    fig = px.scatter_mapbox(substations_final, lat = "Latitude", lon = "Longitude", 
                            hover_name = "PS_name", hover_data = ["Plant", "Total_cost", "Year"],
                            color = "Total_cost", zoom = 5, size = "Marks", size_max=10)
    
    fig.update_layout (mapbox_style = 'basic'
                       , mapbox_accesstoken = mapbox_access_token, 
                        margin={"r": 2,"t":2,"l":2,"b":2}, 
                        paper_bgcolor = 'rgba(0,0,0,0)',
                        plot_bgcolor = 'rgba(0,0,0,0)')

    return fig

    

if __name__ == '__main__':
    app.run_server(debug=False)
