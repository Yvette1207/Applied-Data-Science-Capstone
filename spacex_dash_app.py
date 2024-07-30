# Bring in the necessary libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the SpaceX launch data into a DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize the Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'All Sites'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                 ],
                 placeholder='Select a Launch Site Here',
                 value='All Sites',
                 searchable=True),
    html.Br(),

    # Pie chart to show the success rate for selected site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Range slider to filter payload
    dcc.RangeSlider(id='payload-slider',
                    min=0,
                    max=10000,
                    step=1000,
                    marks={i: '{}'.format(i) for i in range(0, 10001, 1000)},
                    value=[min_payload, max_payload]),

    # Scatter chart to show payload vs. success correlation
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback to update pie chart based on selected site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        fig = px.pie(values=spacex_df.groupby('Launch Site')['class'].mean(), 
                     names=spacex_df.groupby('Launch Site')['Launch Site'].first(),
                     title='Total Success Launches by Site')
    else:
        fig = px.pie(values=spacex_df[spacex_df['Launch Site'] == selected_site]['class'].value_counts(normalize=True),
                     names=spacex_df['class'].unique(),
                     title=f'Total Success Launches for Site {selected_site}')
    return fig

# Callback to update scatter chart based on selected site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
    if selected_site == 'All Sites':
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         hover_data=['Launch Site'],
                         title='Correlation Between Payload and Success for All Sites')
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(site_df,
                         x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         hover_data=['Launch Site'],
                         title=f'Correlation Between Payload and Success for Site {selected_site}')
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server()
