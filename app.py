from dash import Dash, html
import dash



app = Dash(__name__,use_pages=True)


app.layout = html.Div([
    #Header with white back ground, rounded corners and shadow
    html.H1("Carto Editor", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'}),
    html.Div(id='info-box', style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'}),
    #Main content
    dash.page_container,
    #Footer with white back ground, rounded corners and shadow
    html.Div("Author : X", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px','margin':'10px'})
])


# print('Refreshed')


if(__name__ == "__main__"):
    app.run(dev_tools_hot_reload=True,debug=True)