from dash import Dash, html, dcc, DiskcacheManager
import dash


from pages.modules.config import INFO_BOX_ID
from pages.modules.data import INFO_BOX_COMP
## CACHE


app = Dash(__name__,use_pages=True)


app.layout = html.Div([
    #Header with white back ground, rounded corners and shadow
    html.H1("Carto Editor", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'}),
    dcc.Loading(children=[INFO_BOX_COMP],id=INFO_BOX_ID, style={"zIndex":"1000",'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px',"margin":"10px"}),
    #Main content
    dash.page_container,
    #Footer with white back ground, rounded corners and shadow
    html.Div("Author : X", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px','margin':'10px'})
])

# print('Refreshed')


if(__name__ == "__main__"):
    app.run(dev_tools_hot_reload=True,debug=True, host='localhost', port=8050)