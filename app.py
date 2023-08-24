from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash
import flask
from flask import Response

from carto_editor import APP_INFO_BOX, LOADING_BOX, SELECTOR


## CACHE



server = flask.Flask(__name__) # define flask app.server
app = Dash(__name__, use_pages=True, external_stylesheets=['assets/bootstrap.min.css', dbc.themes.LUMEN, dbc.icons.BOOTSTRAP,'assets/custom_range_slider.css'],server=server)

app.layout = html.Div([
    #Header with white back ground, rounded corners and shadow
    html.Div([
    dbc.Navbar(
    dbc.Container(
        [
            dcc.Link(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='./assets/logo.png', height="50px")),
                        dbc.Col(dbc.NavbarBrand("Carto Editor", className="ms-2 text-dark")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href=dash.page_registry['pages.docs']['relative_path']+'/index',
                style={"textDecoration": "none"},
            )
        ]
    ),
    color="light",
    dark=False,
    ),
    SELECTOR,
    LOADING_BOX,
    APP_INFO_BOX],className='shadow-sm rounded',style={'height':'8vh'}),
    # #Main content
    html.Div(id='page-content',children=dash.page_container),
    #Footer with white back ground, rounded corners and shadow
    dbc.Container("Parc National du Mercantour - Tous droits réservés.", class_name='h4 bg-secondary text-dark text-center align-item-center', style={'height':'5vh'},fluid=True)
])

import os


def get_file(filename):  # pragma: no cover
    try:
        src = './pdf/' + filename
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src,'rb').read()
    except IOError as exc:
        return str(exc)



@app.server.route('/pdf/<path:path>')
def serve_media(path):
    return flask.send_from_directory("./pdf/", path)




if(__name__ == "__main__"):
    app.run(debug=True, host='localhost')
