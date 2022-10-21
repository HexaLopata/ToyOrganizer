from datetime import date
from decimal import Decimal
from typing import Callable, List, Protocol, Union
import os

from PyQt6.QtGui import QPainter, QAction, QMouseEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QAbstractSpinBox,
    QStyleOption,
    QStyle,
    QDialog,
    QMenuBar,
    QHeaderView,
    QComboBox,
    QApplication,
    QCalendarWidget,
    QDateEdit,
    QTextEdit
)

from toy_organizer.config import STYLES_PATH


def getStyles(fileName: str):
    with open(os.path.join(STYLES_PATH, fileName), 'r', encoding='utf-8') as style:
        return '\n'.join(style.readlines())


class StyleableWidget(QWidget):
    def paintEvent(self, _):
        painter = QPainter(self)
        option = QStyleOption()
        option.initFrom(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, option, painter, self)


class QtTableWidget(QTableWidget):
    def setupTable(self, data, labels: List[str]):
        self.setRowCount(len(data))
        if len(data) > 0:
            self.setColumnCount(len(data[0]))

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                tableItem = QTableWidgetItem(str(item))
                tableItem.setFlags(tableItem.flags() ^
                                   Qt.ItemFlag.ItemIsEditable)
                self.setItem(i, j, tableItem)

        if len(data) > 0:
            self.setHorizontalHeaderLabels(labels)
            header = self.horizontalHeader()
            header.resizeSections(QHeaderView.ResizeMode.ResizeToContents)
        else:
            self.setColumnCount(0)


class QtSideMenu(StyleableWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(15)
        self.setContentsMargins(7, 15, 7, 0)
        self.setLayout(self.layout)

    def addWidget(self, widget):
        self.layout.addWidget(widget)


class QtHeader(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class ViewFactory:
    def __init__(
        self,
        getCatalogView: Callable[[], 'CatalogView'],
        getAddToyView: Callable[[], 'AddToyView'],
        getEditToyView: Callable[[int], 'EditToyView'],
        getNavMenuView: Callable[[], 'NavMenuView'],
        getMainView: Callable[[], 'MainView'],
        getMostExpensiveToyView: Callable[[], 'MostExpensiveToyView'],
        getAgeSearchView: Callable[[], 'AgeSearchView'],
        getIncreaseCostView: Callable[[], 'IncreaseCostView'],
        getDeleteByNameView: Callable[[], 'DeleteByNameView'],
        getEventsCatalogView: Callable[[], 'EventCatalogView'],
        getAddEventView: Callable[[], 'AddEventView'],
        getEditEventView: Callable[[int], 'EditEventView'],
    ) -> None:
        self.getCatalogView = getCatalogView
        self.getAddToyView = getAddToyView
        self.getEditToyView = getEditToyView
        self.getNavMenuView = getNavMenuView
        self.getMainView = getMainView
        self.getMostExpensiveToyView = getMostExpensiveToyView
        self.getAgeSearchView = getAgeSearchView
        self.getIncreaseCostView = getIncreaseCostView
        self.getDeleteByNameView = getDeleteByNameView
        self.getEventsCatalogView = getEventsCatalogView
        self.getAddEventView = getAddEventView
        self.getEditEventView = getEditEventView


class View(Protocol):
    def show(self): ...
    def showMessage(self, message, title): ...


class QtView(StyleableWidget):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__()
        self.mainWindow = mainWindow

    def show(self):
        self.mainWindow.switchPage(self)

    def showMessage(self, message, title='Внимание'):
        messageDialog = QDialog(self)
        messageDialog.setWindowTitle(title)
        messageDialog.setFixedWidth(300)
        messageDialog.setFixedHeight(150)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        okButton = QPushButton('Ок')
        okButton.clicked.connect(messageDialog.close)
        layout.addWidget(okButton)
        messageDialog.setLayout(layout)
        messageDialog.exec()


class QtPage(QtView):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.formLayout = QVBoxLayout()
        self.formLayout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.sideMenu = QtSideMenu()
        widget = QWidget()
        widget.setLayout(self.formLayout)
        self.layout.addWidget(widget, 3)
        self.layout.addWidget(self.sideMenu, 1)
        self.setLayout(self.layout)


class CatalogView(View):
    @property
    def tableData(self): ...

    @tableData.setter
    def tableData(self, data): ...

    @property
    def selectedItems(self): ...

    def subscribeOnAddButtonClick(self, handler): ...
    def subscribeOnEditButtonClick(self, handler): ...
    def subscribeOnDeleteButtonClick(self, handler): ...
    def subscribeOnMostExpensiveToyButtonClick(self, handler): ...
    def subscribeOnAgeSearchButtonClick(self, handler): ...
    def subscribeOnIncreaseCostButtonClick(self, handler): ...
    def subscribeOnDeleteByNameButtonClick(self, handler): ...


class QtCatalogView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.addButton = QPushButton('Добавить')
        self.editButton = QPushButton('Редактировать')
        self.deleteButton = QPushButton('Удалить')
        self.mostExpensiveToyButton = QPushButton('Наиболее дорогая игрушка')
        self.ageSearchButton = QPushButton('Подобрать по возрасту')
        self.increaseCostButton = QPushButton('Увеличить стоимость')
        self.deleteByNameButton = QPushButton('Удалить по названию')
        self.sideMenu.addWidget(self.addButton)
        self.sideMenu.addWidget(self.editButton)
        self.sideMenu.addWidget(self.deleteButton)
        self.sideMenu.addWidget(self.mostExpensiveToyButton)
        self.sideMenu.addWidget(self.ageSearchButton)
        self.sideMenu.addWidget(self.increaseCostButton)
        self.sideMenu.addWidget(self.deleteByNameButton)
        self.table = QtTableWidget(0, 0)
        self.table.setRowCount(1)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.formLayout.addWidget(self.table)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self._tableData = []
        self.setStyleSheet(getStyles('catalog.qss'))

    @property
    def selectedItems(self):
        selectedItems = self.table.selectedItems()
        rowIndexes = set()
        for item in selectedItems:
            row = item.row()
            rowIndexes.add(row)

        items = []
        for row in rowIndexes:
            item = []
            for column in range(self.table.columnCount()):
                item.append(self.table.item(row, column).text())
            items.append(item)
        return items

    @property
    def tableData(self):
        return self._tableData

    @tableData.setter
    def tableData(self, data):
        self._tableData = data
        self.table.setupTable(
            data, ['Id', 'Название', 'Стоимость', 'Количество', 'Возраст'])

    def subscribeOnAddButtonClick(self, handler):
        self.addButton.clicked.connect(handler)

    def subscribeOnEditButtonClick(self, handler):
        self.editButton.clicked.connect(handler)

    def subscribeOnDeleteButtonClick(self, handler):
        self.deleteButton.clicked.connect(
            handler)

    def subscribeOnMostExpensiveToyButtonClick(self, handler):
        self.mostExpensiveToyButton.clicked.connect(
            handler)

    def subscribeOnAgeSearchButtonClick(self, handler):
        self.ageSearchButton.clicked.connect(handler)

    def subscribeOnIncreaseCostButtonClick(self, handler):
        self.increaseCostButton.clicked.connect(handler)

    def subscribeOnDeleteByNameButtonClick(self, handler):
        self.deleteByNameButton.clicked.connect(handler)


class MostExpensiveToyView(View):
    def subscribeOnSearchButton(self, handler): ...

    def subscribeOnCancelButton(self, handler): ...

    @property
    def maxCost(self) -> Decimal: ...

    @property
    def ageLower(self) -> int: ...

    @property
    def ageUpper(self) -> int: ...

    @property
    def hasToy(self) -> bool: ...

    @hasToy.setter
    def hasToy(self, value: bool): ...

    @property
    def tableData(self): ...

    @tableData.setter
    def tableData(self, value): ...


class QtMostExpensiveToyView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.header = QtHeader('Поиск самой дорогой игрушки')
        self.maxCostLabel = QLabel('Максимальная стоимость')
        self.maxCostSpinBox = QDoubleSpinBox()
        self.maxCostSpinBox.setRange(0, 1_000_000_000)
        self.ageLabel = QLabel('Возраст')
        self.ageLowerSpinBox = QSpinBox()
        self.ageUpperSpinBox = QSpinBox()
        self.maxCostSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.ageLowerSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.ageUpperSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.hasToyLabel = QLabel('')
        self.table = QtTableWidget(0, 0)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setMaximumWidth(500)
        self.searchButton = QPushButton('Поиск')
        self.cancelButton = QPushButton('Назад')
        self._hasToy = False
        self._tableData = []
        self.formLayout.addWidget(self.header)
        self.formLayout.addWidget(self.maxCostLabel)
        self.formLayout.addWidget(self.maxCostSpinBox)
        self.formLayout.addWidget(self.ageLabel)
        self.formLayout.addWidget(self.ageLowerSpinBox)
        self.formLayout.addWidget(self.ageUpperSpinBox)
        self.formLayout.addWidget(self.hasToyLabel)
        self.formLayout.addWidget(self.table)
        self.sideMenu.addWidget(self.searchButton)
        self.sideMenu.addWidget(self.cancelButton)

    def subscribeOnSearchButton(self, handler):
        self.searchButton.clicked.connect(handler)

    def subscribeOnCancelButton(self, handler):
        self.cancelButton.clicked.connect(handler)

    @property
    def maxCost(self) -> Decimal:
        return Decimal(self.maxCostSpinBox.value())

    @property
    def ageLower(self) -> int:
        return self.ageLowerSpinBox.value()

    @property
    def ageUpper(self) -> int:
        return self.ageUpperSpinBox.value()

    @property
    def hasToy(self) -> bool:
        return self._hasToy

    @hasToy.setter
    def hasToy(self, value: bool):
        self._hasToy = value
        if value:
            self.hasToyLabel.setText('')
        else:
            self.hasToyLabel.setText(
                'Игрушка с заданными параметрами не найдена')

    @property
    def tableData(self):
        return self._tableData

    @tableData.setter
    def tableData(self, value):
        self._tableData = value
        self.table.setupTable(value, ['Название', 'Стоимость'])


class AgeSearchView(View):
    def subscribeOnSearchButtonClick(self, handler): ...

    def subscribeOnCancelButtonClick(self, handler): ...

    @property
    def tableData(self): ...

    @tableData.setter
    def tableData(self, value): ...

    @property
    def ageLower(self) -> int: ...

    @property
    def ageUpper(self) -> int: ...

    @property
    def orderBy(self) -> Union[str, None]: ...


class QtAgeSearchView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.header = QtHeader('Поиск по возрасту')
        self.ageLabel = QLabel('Возраст')
        self.ageLowerSpinBox = QSpinBox()
        self.ageUpperSpinBox = QSpinBox()
        self.ageLowerSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.ageUpperSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.searchButton = QPushButton('Поиск')
        self.cancelButton = QPushButton('Назад')
        self.orderByLabel = QLabel('Сортировка по')
        self.orderByComboBox = QComboBox()
        self.orderByComboBox.addItems(['Название', 'Стоимость', 'Ничего'])
        self.table = QtTableWidget(0, 0)
        self.table.setMaximumWidth(500)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._tableData = []
        self.formLayout.addWidget(self.header)
        self.formLayout.addWidget(self.ageLabel)
        self.formLayout.addWidget(self.ageLowerSpinBox)
        self.formLayout.addWidget(self.ageUpperSpinBox)
        self.formLayout.addWidget(self.orderByLabel)
        self.formLayout.addWidget(self.orderByComboBox)
        self.formLayout.addWidget(self.table)
        self.sideMenu.addWidget(self.searchButton)
        self.sideMenu.addWidget(self.cancelButton)

    def subscribeOnSearchButtonClick(self, handler):
        self.searchButton.clicked.connect(handler)

    def subscribeOnCancelButtonClick(self, handler):
        self.cancelButton.clicked.connect(handler)

    @property
    def tableData(self):
        return self._tableData

    @tableData.setter
    def tableData(self, value):
        self._tableData = value
        self.table.setupTable(value, ['Название', 'Стоимость'])

    @property
    def ageLower(self) -> int:
        return self.ageLowerSpinBox.value()

    @property
    def ageUpper(self) -> int:
        return self.ageUpperSpinBox.value()

    @property
    def orderBy(self) -> Union[str, None]:
        if self.orderByComboBox.currentText() == 'Ничего':
            return None
        columnDict = {'Название': 'name', 'Стоимость': 'cost'}
        return columnDict[self.orderByComboBox.currentText()]


class IncreaseCostView(View):
    def subscibeOnUpdateButton(self, handler): ...

    def subscibeOnCancelButton(self, handler): ...

    @property
    def ageLower(self) -> int: ...

    @property
    def ageUpper(self) -> int: ...

    @property
    def multiplierAsPercentage(self) -> int: ...


class QtIncreaseCostView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.header = QtHeader('Увеличение цены по возрасту')
        self.ageLabel = QLabel('Возраст')
        self.ageLowerSpinBox = QSpinBox()
        self.ageUpperSpinBox = QSpinBox()
        self.multiplierLabel = QLabel('Множитель (в процентах)')
        self.multiplierSpinBox = QSpinBox()
        self.multiplierSpinBox.setRange(0, 100000)
        self.ageLowerSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.ageUpperSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.multiplierSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.updateButton = QPushButton('Обновить')
        self.cancelButton = QPushButton('Отмена')
        self.formLayout.addWidget(self.header)
        self.formLayout.addWidget(self.ageLabel)
        self.formLayout.addWidget(self.ageLowerSpinBox)
        self.formLayout.addWidget(self.ageUpperSpinBox)
        self.formLayout.addWidget(self.multiplierLabel)
        self.formLayout.addWidget(self.multiplierSpinBox)
        self.sideMenu.addWidget(self.updateButton)
        self.sideMenu.addWidget(self.cancelButton)

    def subscibeOnUpdateButton(self, handler):
        self.updateButton.clicked.connect(handler)

    def subscibeOnCancelButton(self, handler):
        self.cancelButton.clicked.connect(handler)

    @property
    def ageLower(self) -> int:
        return self.ageLowerSpinBox.value()

    @property
    def ageUpper(self) -> int:
        return self.ageUpperSpinBox.value()

    @property
    def multiplierAsPercentage(self) -> int:
        return self.multiplierSpinBox.value()


class DeleteByNameView(View):
    def subscribeOnDeleteButtonClick(self, handler): ...

    def subscribeOnCancelButtonClick(self, handler): ...

    @property
    def name(self) -> str: ...


class QtDeleteByNameView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.header = QtHeader('Удаление по названию')
        self.nameLabel = QLabel('Название')
        self.nameLineEdit = QLineEdit()
        self.deleteButton = QPushButton('Удалить')
        self.cancelButton = QPushButton('Отмена')
        self.formLayout.addWidget(self.header)
        self.formLayout.addWidget(self.nameLabel)
        self.formLayout.addWidget(self.nameLineEdit)
        self.sideMenu.addWidget(self.deleteButton)
        self.sideMenu.addWidget(self.cancelButton)

    def subscribeOnDeleteButtonClick(self, handler):
        self.deleteButton.clicked.connect(handler)

    def subscribeOnCancelButtonClick(self, handler):
        self.cancelButton.clicked.connect(handler)

    @property
    def name(self) -> str:
        return self.nameLineEdit.text()


class AddToyView(View):
    @property
    def name(self) -> str: ...

    @property
    def cost(self) -> Decimal: ...

    @property
    def quantity(self) -> int: ...

    @property
    def ageLower(self) -> int: ...

    @property
    def ageUpper(self) -> int: ...

    def subscribeOnAddButtonClick(self, handler): ...
    def subscribeOnCancelButtonClick(self, handler): ...


class QtAddToyView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.header = QtHeader('Добавление игрушки')
        self.nameLineEdit = QLineEdit()
        self.costSpinBox = QDoubleSpinBox()
        self.costSpinBox.setRange(0, 1_000_000_000)
        self.quantitySpinBox = QSpinBox()
        self.quantitySpinBox.setRange(0, 1_000_000_000)
        self.ageLowerSpinBox = QSpinBox()
        self.ageUpperSpinBox = QSpinBox()
        self.quantitySpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.costSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.ageLowerSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.ageUpperSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.formLayout.addWidget(self.header)
        self.formLayout.addWidget(QLabel('Название'))
        self.formLayout.addWidget(self.nameLineEdit)
        self.formLayout.addWidget(QLabel('Цена'))
        self.formLayout.addWidget(self.costSpinBox)
        self.formLayout.addWidget(QLabel('Количество'))
        self.formLayout.addWidget(self.quantitySpinBox)
        self.formLayout.addWidget(QLabel('Возраст'))
        self.formLayout.addWidget(self.ageLowerSpinBox)
        self.formLayout.addWidget(self.ageUpperSpinBox)
        self.addButton = QPushButton('Добавить')
        self.cancelButton = QPushButton('Отмена')
        self.sideMenu.addWidget(self.addButton)
        self.sideMenu.addWidget(self.cancelButton)

    @property
    def name(self) -> str:
        return self.nameLineEdit.text()

    @property
    def cost(self) -> Decimal:
        return Decimal(self.costSpinBox.value())

    @property
    def quantity(self) -> int:
        return self.quantitySpinBox.value()

    @property
    def ageLower(self) -> int:
        return self.ageLowerSpinBox.value()

    @property
    def ageUpper(self) -> int:
        return self.ageUpperSpinBox.value()

    def subscribeOnAddButtonClick(self, handler):
        self.addButton.clicked.connect(handler)

    def subscribeOnCancelButtonClick(self, handler):
        self.cancelButton.clicked.connect(handler)


class EditToyView(View):
    @property
    def name(self) -> str: ...

    @property
    def id(self) -> int: ...

    @property
    def cost(self) -> Decimal: ...

    @property
    def quantity(self) -> int: ...

    @property
    def ageLower(self) -> int: ...

    @property
    def ageUpper(self) -> int: ...

    @name.setter
    def name(self, value: str) -> None: ...

    @cost.setter
    def cost(self, value: Decimal) -> None: ...

    @quantity.setter
    def quantity(self, value: int) -> None: ...

    @ageLower.setter
    def ageLower(self, value: int) -> None: ...

    @ageUpper.setter
    def ageUpper(self, value: int) -> None: ...

    def subscribeOnEditButtonClick(self, handler): ...
    def subscribeOnCancelButtonClick(self, handler): ...


class QtEditToyView(QtPage):
    def __init__(self, mainWindow: 'MainWindow', id_: int) -> None:
        super().__init__(mainWindow)
        self._id = id_
        self.header = QtHeader('Редактирование игрушки')
        self.saveButton = QPushButton('Сохранить')
        self.cancelButton = QPushButton('Отмена')
        self.nameLineEdit = QLineEdit()
        self.costSpinBox = QDoubleSpinBox()
        self.costSpinBox.setRange(0, 1_000_000_000)
        self.quantitySpinBox = QSpinBox()
        self.quantitySpinBox.setRange(0, 1_000_000_000)
        self.ageLowerSpinBox = QSpinBox()
        self.ageUpperSpinBox = QSpinBox()
        self.quantitySpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.costSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.ageLowerSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.ageUpperSpinBox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.formLayout.addWidget(self.header)
        self.formLayout.addWidget(QLabel('Название'))
        self.formLayout.addWidget(self.nameLineEdit)
        self.formLayout.addWidget(QLabel('Цена'))
        self.formLayout.addWidget(self.costSpinBox)
        self.formLayout.addWidget(QLabel('Количество'))
        self.formLayout.addWidget(self.quantitySpinBox)
        self.formLayout.addWidget(QLabel('Возраст'))
        self.formLayout.addWidget(self.ageLowerSpinBox)
        self.formLayout.addWidget(self.ageUpperSpinBox)
        self.sideMenu.addWidget(self.saveButton)
        self.sideMenu.addWidget(self.cancelButton)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self.nameLineEdit.text()

    @property
    def cost(self) -> Decimal:
        return Decimal(self.costSpinBox.value())

    @property
    def quantity(self) -> int:
        return self.quantitySpinBox.value()

    @property
    def ageLower(self) -> int:
        return self.ageLowerSpinBox.value()

    @property
    def ageUpper(self) -> int:
        return self.ageUpperSpinBox.value()

    @name.setter
    def name(self, value: str) -> None:
        self.nameLineEdit.setText(value)

    @cost.setter
    def cost(self, value: Decimal) -> None:
        self.costSpinBox.setValue(value)

    @quantity.setter
    def quantity(self, value: int) -> None:
        self.quantitySpinBox.setValue(value)

    @ageLower.setter
    def ageLower(self, value: int) -> None:
        self.ageLowerSpinBox.setValue(value)

    @ageUpper.setter
    def ageUpper(self, value: int) -> None:
        self.ageUpperSpinBox.setValue(value)

    def subscribeOnEditButtonClick(self, handler):
        self.saveButton.clicked.connect(handler)

    def subscribeOnCancelButtonClick(self, handler):
        self.cancelButton.clicked.connect(handler)


class NavMenuView(View):
    def subscribeOnFileMenuCatalogClick(self, handler): ...

    def subscribeOnFileMenuEventsClick(self, handler): ...

    def subscribeOnFileMenuExitClick(self, handler): ...

    def subscribeOnCatalogWatchClick(self, handler): ...

    def subscribeOnCatalogMostExpensiveClick(self, handler): ...

    def subscribeOnCatalogAddClick(self, handler): ...

    def subscribeOnEventsWatchClick(self, handler): ...

    def subscribeOnEventsAddClick(self, handler): ...


class QtNavMenuView(QMenuBar):
    def __init__(self, window: 'MainWindow') -> None:
        super().__init__()
        self.mainWindow = window
        self.fileMenu = self.addMenu('Файл')
        self.catalogMenu = self.addMenu('Каталог')
        self.eventsMenu = self.addMenu('События')

    def show(self) -> None:
        return self.mainWindow.setNavMenu(self)

    def showMessage(self, message, title='Внимание'):
        messageDialog = QDialog(self)
        messageDialog.setWindowTitle(title)
        messageDialog.setFixedWidth(300)
        messageDialog.setFixedHeight(150)
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        okButton = QPushButton('Ок')
        okButton.clicked.connect(messageDialog.close)
        layout.addWidget(okButton)
        messageDialog.setLayout(layout)
        messageDialog.exec()

    def subscribeOnFileMenuCatalogClick(self, handler):
        action = QAction('Каталог', self.mainWindow)
        action.triggered.connect(handler)
        self.fileMenu.addAction(action)

    def subscribeOnFileMenuEventsClick(self, handler):
        action = QAction('События', self.mainWindow)
        action.triggered.connect(handler)
        self.fileMenu.addAction(action)

    def subscribeOnFileMenuExitClick(self, handler):
        action = QAction('Выход', self.mainWindow)
        action.triggered.connect(handler)
        self.fileMenu.addAction(action)

    def subscribeOnCatalogWatchClick(self, handler):
        action = QAction('Просмотреть', self.mainWindow)
        action.triggered.connect(handler)
        self.catalogMenu.addAction(action)

    def subscribeOnCatalogMostExpensiveClick(self, handler):
        action = QAction('Наиболее дорогая игрушка', self.mainWindow)
        action.triggered.connect(handler)
        self.catalogMenu.addAction(action)

    def subscribeOnCatalogAddClick(self, handler):
        action = QAction('Добавить игрушку', self.mainWindow)
        action.triggered.connect(handler)
        self.catalogMenu.addAction(action)

    def subscribeOnEventsWatchClick(self, handler):
        action = QAction('Просмотреть', self.mainWindow)
        action.triggered.connect(handler)
        self.eventsMenu.addAction(action)

    def subscribeOnEventsAddClick(self, handler):
        action = QAction('Добавить событие', self.mainWindow)
        action.triggered.connect(handler)
        self.eventsMenu.addAction(action)


class MainView(View):
    def subscribeOnCatalogClick(self, handler): ...

    def subscribeOnAddEventClick(self, handler): ...

    def setEventsData(self, data): ...


class QtMainView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.catalogButton = QPushButton('Каталог')
        self.catalogButton.setAutoDefault(True)
        self.addEventClick = QPushButton('Напомнить о...')
        self.addEventClick.setAutoDefault(True)
        self.formLayout.addWidget(QtHeader('Toy Organizer'))
        self.descriptionLabel = QLabel(
            'Приложение органайзер для ведения учета игрушек в детском магазине'
        )
        self.descriptionLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.formLayout.addWidget(self.descriptionLabel)
        self.eventTable = QtTableWidget()
        self.eventTable.setupTable(
            [['1', 'test', '2022-10-03']], ['1', '2', '3'])
        self.eventTable.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.calendar = QCalendarWidget()
        self.eventLayout = QVBoxLayout()
        self.eventLayout.addWidget(QLabel('События на сегодня'))
        self.eventLayout.addWidget(self.eventTable)
        self.eventLayout.addWidget(self.calendar)
        self.calendarContainer = QWidget()
        self.calendarContainer.setLayout(self.eventLayout)
        self.formLayout.addWidget(self.calendarContainer)
        self.sideMenu.addWidget(self.catalogButton)
        self.sideMenu.addWidget(self.addEventClick)

    def subscribeOnCatalogClick(self, handler):
        self.catalogButton.clicked.connect(handler)

    def subscribeOnAddEventClick(self, handler):
        self.addEventClick.clicked.connect(handler)

    def setEventsData(self, data):
        self.eventTable.setupTable(data, ['Id', 'Описание', 'Дата'])


class EventCatalogView(View):
    @property
    def tableData(self): ...

    @tableData.setter
    def tableData(self, data): ...

    def subscribeOnEditButtonClick(self, handler): ...

    def subscribeOnAddButtonClick(self, handler): ...

    def subscribeOnDeleteButtonClick(self, handler): ...


class QtEventCatalogView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.addButton = QPushButton('Добавить')
        self.editButton = QPushButton('Редактировать')
        self.deleteButton = QPushButton('Удалить')
        self._tableData = []
        self.sideMenu.addWidget(self.addButton)
        self.sideMenu.addWidget(self.editButton)
        self.sideMenu.addWidget(self.deleteButton)
        self.table = QtTableWidget()
        self.formLayout.addWidget(self.table)

    @property
    def tableData(self):
        return self._tableData

    @tableData.setter
    def tableData(self, data):
        self._tableData = data
        self.table.setupTable(data, ['Id', 'Описание', 'Дата'])

    @property
    def selectedItems(self):
        selectedItems = self.table.selectedItems()
        rowIndexes = set()
        for item in selectedItems:
            row = item.row()
            rowIndexes.add(row)

        items = []
        for row in rowIndexes:
            item = []
            for column in range(self.table.columnCount()):
                item.append(self.table.item(row, column).text())
            items.append(item)
        return items

    def subscribeOnAddButtonClick(self, handler):
        self.addButton.clicked.connect(handler)

    def subscribeOnEditButtonClick(self, handler):
        self.editButton.clicked.connect(handler)

    def subscribeOnDeleteButtonClick(self, handler):
        self.deleteButton.clicked.connect(handler)


class AddEventView(View):
    @property
    def description(self) -> str: ...

    @property
    def dateCreated(self) -> date: ...

    def subscribeOnAddButtonClick(self, handler): ...
    def subscribeOnCancelButtonClick(self, handler): ...


class QtAddEventView(QtPage):
    def __init__(self, mainWindow: 'MainWindow') -> None:
        super().__init__(mainWindow)
        self.header = QtHeader('Добавление события')
        self.addButton = QPushButton('Добавить')
        self.cancelButton = QPushButton('Отмена')
        self.dateInput = QDateEdit()
        self.descriptionTextArea = QTextEdit()
        self.dateInput.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.formLayout.addWidget(self.header)
        self.formLayout.addWidget(QLabel('Описание'))
        self.formLayout.addWidget(self.descriptionTextArea)
        self.formLayout.addWidget(QLabel('Дата'))
        self.formLayout.addWidget(self.dateInput)
        self.sideMenu.addWidget(self.addButton)
        self.sideMenu.addWidget(self.cancelButton)

    @property
    def description(self) -> str:
        return self.descriptionTextArea.toPlainText()

    @property
    def dateCreated(self) -> date:
        return self.dateInput.date().toPyDate()

    def subscribeOnAddButtonClick(self, handler):
        self.addButton.clicked.connect(handler)

    def subscribeOnCancelButtonClick(self, handler):
        self.cancelButton.clicked.connect(handler)


class EditEventView(View):
    @property
    def description(self) -> str: ...

    @property
    def dateCreated(self) -> date: ...

    @property
    def id(self) -> int: ...

    @description.setter
    def description(self, value: str) -> None: ...

    @dateCreated.setter
    def dateCreated(self, value: date) -> None: ...

    def subscribeOnEditButtonClick(self, handler): ...
    def subscribeOnCancelButtonClick(self, handler): ...


class QtEditEventView(QtPage):
    def __init__(self, mainWindow: 'MainWindow', id_: int) -> None:
        super().__init__(mainWindow)
        self._id = id_
        self.header = QtHeader('Редактирование события')
        self.saveButton = QPushButton('Сохранить')
        self.cancelButton = QPushButton('Отмена')
        self.dateInput = QDateEdit()
        self.dateInput.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.descriptionTextArea = QTextEdit()
        self.formLayout.addWidget(self.header)
        self.formLayout.addWidget(QLabel('Описание'))
        self.formLayout.addWidget(self.descriptionTextArea)
        self.formLayout.addWidget(QLabel('Дата'))
        self.formLayout.addWidget(self.dateInput)
        self.sideMenu.addWidget(self.saveButton)
        self.sideMenu.addWidget(self.cancelButton)

    @property
    def description(self) -> str:
        return self.descriptionTextArea.toPlainText()

    @property
    def dateCreated(self) -> date:
        return self.dateInput.date().toPyDate()

    @property
    def id(self) -> int:
        return self._id

    @description.setter
    def description(self, value: str) -> None:
        self.descriptionTextArea.setText(value)

    @dateCreated.setter
    def dateCreated(self, value: date) -> None:
        self.dateInput.setDate(value)

    def subscribeOnEditButtonClick(self, handler):
        self.saveButton.clicked.connect(handler)

    def subscribeOnCancelButtonClick(self, handler):
        self.cancelButton.clicked.connect(handler)


class MainWindow(QMainWindow):
    def __init__(self, page: QWidget = None, navMenu=None) -> None:
        super().__init__()
        self.setWindowTitle('Toy Organizer')
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(400)
        self.setMinimumWidth(800)
        self.setContentsMargins(0, 0, 0, 0)
        if page is None:
            page = QWidget()
        if navMenu is None:
            navMenu = QMenuBar()
        self.navMenu = navMenu
        self.page = page
        self.setCentralWidget(self.page)
        self.setMenuBar(self.navMenu)
        self.setStyleSheet(getStyles('mainStyles.qss'))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        focusedWidget = QApplication.focusWidget()
        if focusedWidget is not None:
            focusedWidget.clearFocus()
        super().mousePressEvent(event)

    def switchPage(self, page: QWidget):
        self.page = page
        self.setCentralWidget(page)

    def setNavMenu(self, navMenu: QMenuBar):
        self.navMenu = navMenu
        self.setMenuBar(navMenu)
