from dash import dcc
import dash
from dash import html
from pages.modules.config import NS_RENDER, PageConfig, arrow_function, CONTENT_STYLE
import os
dash.register_page(__name__, path='/docs',path_template='/docs/<page>')

not_found = (f"""
# 404
## Page not found
""")

mardown_style = {
      'overflow': 'auto',
      'height': '100%',

}

def layout(page=None):
      mardown = dcc.Markdown(not_found, style=mardown_style, dangerously_allow_html=True)
      if page is not None:
            page = page.replace(".md","")
            if os.path.exists(f"./docs/{page}.md"):
                  with open(f"./docs/{page}.md", 'r', encoding='utf-8') as f:
                        mardown.children = f.read()


      return html.Div(mardown, style=CONTENT_STYLE)

