from abc import ABC
import sys
from datetime import date
from typing import List

from psycopg2.extras import NumericRange

from toy_organizer.models import Toy, Event
from toy_organizer.views import (
    AddEventView,
    AddToyView,
    AgeSearchView,
    CatalogView,
    DeleteByNameView,
    EditEventView,
    EditToyView,
    EventCatalogView,
    IncreaseCostView,
    MainView,
    MostExpensiveToyView,
    NavMenuView,
    View,
    ViewFactory
)


class App:
    @classmethod
    def run(cls, presenter: 'Presenter', navMenuPresenter: 'NavMenuPresenter' = None):
        cls.presenter = presenter
        cls.navMenuPresenter = navMenuPresenter
        cls.presenter.run()
        if navMenuPresenter is not None:
            cls.navMenuPresenter.run()

    @classmethod
    def switchPresenter(cls, presenter: 'Presenter'):
        cls.presenter = presenter

    @classmethod
    def switchNavMenuPresenter(cls, presenter):
        cls.navMenuPresenter = presenter


class Presenter(ABC):
    view: View

    def run(self):
        App.switchPresenter(self)
        self.view.show()


class NavMenuPresenter(Presenter):
    view: NavMenuView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getNavMenuView()
        self.subscribeOnEvents()

    def subscribeOnEvents(self):
        self.view.subscribeOnCatalogAddClick(self.onCatalogAddClick)
        self.view.subscribeOnCatalogMostExpensiveClick(
            self.onCatalogMostExpensiveClick)
        self.view.subscribeOnCatalogWatchClick(
            self.onCatalogWatchClick)
        self.view.subscribeOnFileMenuCatalogClick(
            self.onFileMenuCatalogClick)
        self.view.subscribeOnFileMenuEventsClick(self.onFileMenuEventsClick)
        self.view.subscribeOnFileMenuExitClick(self.onExitClick)
        self.view.subscribeOnEventsAddClick(self.onEventsAddClick)
        self.view.subscribeOnEventsWatchClick(self.onEventsWatchClick)

    def onExitClick(self):
        sys.exit()

    def onCatalogAddClick(self):
        AddToyPresenter(self.viewFactory).run()

    def onCatalogMostExpensiveClick(self):
        MostExpensiveToyPresenter(self.viewFactory).run()

    def onCatalogWatchClick(self):
        CatalogPresenter(self.viewFactory).run()

    def onFileMenuCatalogClick(self):
        CatalogPresenter(self.viewFactory).run()

    def onFileMenuEventsClick(self):
        EventCatalogPresenter(self.viewFactory).run()

    def onEventsAddClick(self):
        AddEventPresenter(self.viewFactory).run()

    def onEventsWatchClick(self):
        EventCatalogPresenter(self.viewFactory).run()


    def run(self):
        App.switchNavMenuPresenter(self)
        self.view.show()


class CatalogPresenter(Presenter):
    view: CatalogView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getCatalogView()
        self.subscribeOnEvents()
        self.setTableData()

    def subscribeOnEvents(self):
        self.view.subscribeOnAddButtonClick(self.onAddButtonClick)
        self.view.subscribeOnEditButtonClick(self.onEditButtonClick)
        self.view.subscribeOnDeleteButtonClick(self.onDeleteButtonClick)
        self.view.subscribeOnMostExpensiveToyButtonClick(
            self.onMostExpensiveToyButtonClick)
        self.view.subscribeOnAgeSearchButtonClick(self.onAgeSearchButtonClick)
        self.view.subscribeOnIncreaseCostButtonClick(
            self.onIncreaseCostButtonClick)
        self.view.subscribeOnDeleteByNameButtonClick(
            self.onDeleteByNameButtonClick)

    def setTableData(self):
        data = []
        toys = Toy.selectAllToys()
        for toy in toys:
            data.append([toy.id, toy.name, toy.cost, toy.quantity,
                        f'{toy.age.lower} - {toy.age.upper - 1}'])

        self.view.tableData = data

    def onAddButtonClick(self):
        AddToyPresenter(self.viewFactory).run()

    def onEditButtonClick(self):
        if len(self.view.selectedItems) == 0:
            self.view.showMessage(
                'Не выбран элемент для редактирования', 'Ошибка')
            return

        if len(self.view.selectedItems) > 1:
            self.view.showMessage('Выбрано слишком много элементов', 'Ошибка')
            return

        EditToyPresenter(self.viewFactory, int(
            self.view.selectedItems[0][0])).run()

    def onDeleteButtonClick(self):
        if len(self.view.selectedItems) == 0:
            self.view.showMessage('Не выбран элемент для удаления', 'Ошибка')
            return

        if len(self.view.selectedItems) > 1:
            self.view.showMessage('Выбрано слишком много элементов', 'Ошибка')
            return

        item = self.view.selectedItems[0]
        toy = Toy.selectById(int(item[0]))
        toy.delete()
        self.setTableData()

    def onAgeSearchButtonClick(self):
        AgeSearchPresenter(self.viewFactory).run()

    def onDeleteByNameButtonClick(self):
        DeleteByNamePresenter(self.viewFactory).run()

    def onIncreaseCostButtonClick(self):
        IncreaseCostPresenter(self.viewFactory).run()

    def onMostExpensiveToyButtonClick(self):
        MostExpensiveToyPresenter(self.viewFactory).run()


class AddToyPresenter(Presenter):
    view: AddToyView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getAddToyView()
        self.subscribeOnEvents()

    def subscribeOnEvents(self):
        self.view.subscribeOnAddButtonClick(self.onAddButtonClick)
        self.view.subscribeOnCancelButtonClick(self.onCancelButtonClick)

    def onAddButtonClick(self):
        if self.view.ageLower >= self.view.ageUpper:
            self.view.showMessage(
                'Минимальный возраст должен быть меньше максимального', 'Ошибка')
            return

        if self.view.name == 0 or str(self.view.name).strip() == '':
            self.view.showMessage('Название не должно быть пустым', 'Ошибка')
            return

        toy = Toy(
            self.view.name,
            self.view.cost,
            self.view.quantity,
            NumericRange(self.view.ageLower, self.view.ageUpper + 1)
        )
        toy.save()
        CatalogPresenter(self.viewFactory).run()

    def onCancelButtonClick(self):
        CatalogPresenter(self.viewFactory).run()


class EditToyPresenter(Presenter):
    view: EditToyView

    def __init__(self, viewFactory: ViewFactory, id_: int) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getEditToyView(id_)
        self.subscribeOnEvents()
        self.toy = Toy.selectById(id_)
        self.setToyAttributes()

    def subscribeOnEvents(self):
        self.view.subscribeOnEditButtonClick(self.onEditButtonClick)
        self.view.subscribeOnCancelButtonClick(self.onCancelButtonClick)

    def setToyAttributes(self):
        self.view.name = self.toy.name
        self.view.cost = self.toy.cost
        self.view.quantity = self.toy.quantity
        self.view.ageLower = self.toy.age.lower
        self.view.ageUpper = self.toy.age.upper

    def onEditButtonClick(self):
        if self.view.ageLower >= self.view.ageUpper:
            self.view.showMessage(
                'Минимальный возраст должен быть меньше максимального', 'Ошибка')
            return

        if self.view.name == 0 or str(self.view.name).strip() == '':
            self.view.showMessage('Название не должно быть пустым', 'Ошибка')
            return

        self.toy.name = self.view.name
        self.toy.cost = self.view.cost
        self.toy.quantity = self.view.quantity
        self.toy.age = NumericRange(self.view.ageLower, self.view.ageUpper)
        self.toy.save()
        CatalogPresenter(self.viewFactory).run()

    def onCancelButtonClick(self):
        CatalogPresenter(self.viewFactory).run()


class MostExpensiveToyPresenter(Presenter):
    view: MostExpensiveToyView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getMostExpensiveToyView()
        self.view.subscribeOnSearchButton(self.onSearchButtonClick)
        self.view.subscribeOnCancelButton(self.onCancelButtonClick)

    def onSearchButtonClick(self):
        self.view.hasToy = True
        ageLower = self.view.ageLower
        ageUpper = self.view.ageUpper
        maxCost = self.view.maxCost

        toy = Toy.selectMostExpensive(ageLower, ageUpper, maxCost)
        if toy is None:
            self.view.hasToy = False
            self.view.tableData = []
        else:
            self.view.tableData = [[toy.name, toy.cost]]

    def onCancelButtonClick(self):
        CatalogPresenter(self.viewFactory).run()


class IncreaseCostPresenter(Presenter):
    view: IncreaseCostView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getIncreaseCostView()
        self.view.subscibeOnUpdateButton(self.onUpdateButtonClick)
        self.view.subscibeOnCancelButton(self.onCancelButtonClick)

    def onUpdateButtonClick(self):
        ageLower = self.view.ageLower
        ageUpper = self.view.ageUpper
        multiplier = self.view.multiplierAsPercentage
        Toy.increaseCostForAge(ageLower, ageUpper, multiplier)
        CatalogPresenter(self.viewFactory).run()

    def onCancelButtonClick(self):
        CatalogPresenter(self.viewFactory).run()


class AgeSearchPresenter(Presenter):
    view: AgeSearchView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getAgeSearchView()
        self.view.subscribeOnSearchButtonClick(self.onSearchButtonClick)
        self.view.subscribeOnCancelButtonClick(self.onCancelButtonClick)

    def onSearchButtonClick(self):
        ageLower = self.view.ageLower
        ageUpper = self.view.ageUpper
        orderBy = self.view.orderBy

        toys = Toy.selectByAge(ageLower, ageUpper, orderBy)
        data = []
        for toy in toys:
            data.append([toy.name, toy.cost])

        self.view.tableData = data

    def onCancelButtonClick(self):
        CatalogPresenter(self.viewFactory).run()


class DeleteByNamePresenter(Presenter):
    view: DeleteByNameView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getDeleteByNameView()
        self.view.subscribeOnDeleteButtonClick(self.onDeleteButtonClick)
        self.view.subscribeOnCancelButtonClick(self.onCancelButtonClick)

    def onDeleteButtonClick(self):
        name = self.view.name
        Toy.deleteByName(name)
        CatalogPresenter(self.viewFactory).run()

    def onCancelButtonClick(self):
        CatalogPresenter(self.viewFactory).run()


class MainMenuPresenter(Presenter):
    view: MainView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getMainView()
        self.subscribeOnEvents()
        events: List[Event] = Event.selectByDate(date.today())
        eventsData = []
        for event in events:
            eventsData.append(
                [str(event.id), event.description, str(event.dateCreated)])
        self.view.setEventsData(eventsData)

    def subscribeOnEvents(self):
        self.view.subscribeOnAddEventClick(self.onAddEventClick)
        self.view.subscribeOnCatalogClick(self.onCatalogClick)

    def onAddEventClick(self):
        AddEventPresenter(self.viewFactory).run()

    def onCatalogClick(self):
        CatalogPresenter(self.viewFactory).run()


class EventCatalogPresenter(Presenter):
    view: EventCatalogView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getEventsCatalogView()
        self.subscribeOnEvents()
        self.setTableData()

    def setTableData(self):
        events: List[Event] = Event.selectAll()
        eventsData = []
        for event in events:
            eventsData.append(
                [str(event.id), event.description, str(event.dateCreated)])
        self.view.tableData = eventsData

    def subscribeOnEvents(self):
        self.view.subscribeOnAddButtonClick(self.onAddButtonClick)
        self.view.subscribeOnDeleteButtonClick(self.onDeleteButtonClick)
        self.view.subscribeOnEditButtonClick(self.onEditButtonClick)

    def onAddButtonClick(self):
        AddEventPresenter(self.viewFactory).run()

    def onEditButtonClick(self):
        if len(self.view.selectedItems) == 0:
            self.view.showMessage(
                'Не выбран элемент для редактирования', 'Ошибка')
            return

        if len(self.view.selectedItems) > 1:
            self.view.showMessage('Выбрано слишком много элементов', 'Ошибка')
            return

        EditEventPresenter(self.viewFactory,  int(
            self.view.selectedItems[0][0])).run()


    def onDeleteButtonClick(self):
        if len(self.view.selectedItems) == 0:
            self.view.showMessage('Не выбран элемент для удаления', 'Ошибка')
            return

        if len(self.view.selectedItems) > 1:
            self.view.showMessage('Выбрано слишком много элементов', 'Ошибка')
            return

        item = self.view.selectedItems[0]
        event = Event.selectById(int(item[0]))
        event.delete()
        self.setTableData()


class AddEventPresenter(Presenter):
    view: AddEventView

    def __init__(self, viewFactory: ViewFactory) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getAddEventView()
        self.subscribeOnEvents()

    def subscribeOnEvents(self):
        self.view.subscribeOnAddButtonClick(self.onAddButtonClick)
        self.view.subscribeOnCancelButtonClick(self.onCancelButtonClick)

    def onAddButtonClick(self):
        if self.view.description == 0 or str(self.view.description).strip() == '':
            self.view.showMessage('Описание не должно быть пустым', 'Ошибка')
            return

        event = Event(
            self.view.description,
            self.view.dateCreated
        )
        event.save()
        EventCatalogPresenter(self.viewFactory).run()

    def onCancelButtonClick(self):
        EventCatalogPresenter(self.viewFactory).run()


class EditEventPresenter(Presenter):
    view: EditEventView

    def __init__(self, viewFactory: ViewFactory, id_: int) -> None:
        self.viewFactory = viewFactory
        self.view = viewFactory.getEditEventView(id_)
        self.subscribeOnEvents()
        self.event = Event.selectById(id_)
        self.setEventAttributes()

    def subscribeOnEvents(self):
        self.view.subscribeOnEditButtonClick(self.onEditButtonClick)
        self.view.subscribeOnCancelButtonClick(self.onCancelButtonClick)

    def setEventAttributes(self):
        self.view.dateCreated = self.event.dateCreated
        self.view.description = self.event.description

    def onEditButtonClick(self):
        if self.view.description == 0 or str(self.view.description).strip() == '':
            self.view.showMessage('Описание не должно быть пустым', 'Ошибка')
            return

        self.event.dateCreated = self.view.dateCreated
        self.event.description = self.view.description
        self.event.save()
        EventCatalogPresenter(self.viewFactory).run()

    def onCancelButtonClick(self):
        EventCatalogPresenter(self.viewFactory).run()
