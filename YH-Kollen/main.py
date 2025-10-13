import taipy.gui.builder as tgb
from taipy.gui import Gui

from frontend.pages.home import home_page
from frontend.pages.utbildningsomrade import utbildningsomrade
from frontend.pages.demografi import gender_age


pages = {"Home": home_page, "Utbildningsomraden": utbildningsomrade, "Demografi": gender_age}



if __name__ == "__main__":
    Gui(pages=pages, css_file="assets/main.css").run(dark_mode=False, use_reloader=True, port="auto") 



