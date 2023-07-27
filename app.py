from dash import Dash, html, dcc
import dash

from flask import Response

from carto_editor import APP_INFO_BOX, LOADING_BOX


## CACHE




app = Dash(__name__, use_pages=True)


app.layout = html.Div([
    #Header with white back ground, rounded corners and shadow
    html.H1("Carto Editor", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'}),
    dcc.Loading(html.Div('X', hidden=True, id="long-task"), style={"zIndex":"1000", "position":"absolute", "bottom":"0px", "right":"0px", "width":"100%", "height":"100%"}, type="circle"),
    LOADING_BOX,
    APP_INFO_BOX,
    # #Main content
    dash.page_container,
    #Footer with white back ground, rounded corners and shadow
    html.Div("Author : X", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px','margin':'10px'})
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