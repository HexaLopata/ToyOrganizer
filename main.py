import sys
import os

from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor

from toy_organizer.config import DBConfig
from toy_organizer.presenters import App, MainMenuPresenter, NavMenuPresenter
from toy_organizer.views import (
    MainWindow,
    QtAddEventView,
    QtAddToyView,
    QtAgeSearchView,
    QtDeleteByNameView,
    QtEditEventView,
    QtEditToyView,
    QtEventCatalogView,
    QtIncreaseCostView,
    QtMainView,
    QtMostExpensiveToyView,
    QtNavMenuView,
    ViewFactory,
    QtCatalogView
)

if __name__ == '__main__':
    load_dotenv()
    app = QApplication(sys.argv)

    dBConnection = connect(
        host=os.getenv('host'),
        port=os.getenv('port'),
        dbname=os.getenv('dbname'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        cursor_factory=RealDictCursor
    )
    try:
        DBConfig.setDBConnection(dBConnection)

        window = MainWindow()
        viewFactory = ViewFactory(
            lambda: QtCatalogView(window),
            lambda: QtAddToyView(window),
            lambda id_: QtEditToyView(window, id_),
            lambda: QtNavMenuView(window),
            lambda: QtMainView(window),
            lambda: QtMostExpensiveToyView(window),
            lambda: QtAgeSearchView(window),
            lambda: QtIncreaseCostView(window),
            lambda: QtDeleteByNameView(window),
            lambda: QtEventCatalogView(window),
            lambda: QtAddEventView(window),
            lambda id_: QtEditEventView(window, id_)
        )
        window.show()
        App.run(MainMenuPresenter(viewFactory), NavMenuPresenter(viewFactory))
        exitCode = app.exec()

    finally:
        if dBConnection.closed == 0:
            dBConnection.close()

    sys.exit(exitCode)
