from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash

from flask import Response

from carto_editor import APP_INFO_BOX, LOADING_BOX, SELECTOR


## CACHE




app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUMEN, dbc.icons.BOOTSTRAP,'assets/custom_range_slider.css'])


app.layout = html.Div([
    #Header with white back ground, rounded corners and shadow
    dbc.NavbarSimple(brand="Carto Editor",color='primary',dark=True),
    SELECTOR,
    LOADING_BOX,
    APP_INFO_BOX,
    # #Main content
    dash.page_container,
    #Footer with white back ground, rounded corners and shadow
    dbc.Container("Author : X", class_name='h4 bg-primary text-light text-center position-absolute fixed-bottom', fluid=True)
])

# # print('Refreshed')
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
def send_pdf(path):
    content = get_file(path)
    return Response(content, mimetype="application/pdf")



if(__name__ == "__main__"):
    app.run(debug=True, host='localhost', port=8050)