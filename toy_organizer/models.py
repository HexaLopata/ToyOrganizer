from datetime import date
from decimal import Decimal
from typing import List, Union
from psycopg2.extras import NumericRange

from .config import DBConfig


class Event:
    def __init__(self, description: str, dateCreated: date) -> None:
        self._description = description
        self._dateCreated = dateCreated
        self._saved = False
        self._id = -1

# region Properties
    @property
    def id(self) -> int:
        return self._id

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def dateCreated(self) -> date:
        return self._dateCreated

    @dateCreated.setter
    def dateCreated(self, value: date):
        self._dateCreated = value
# endregion

    def save(self):
        if self._saved:
            self._update()
        else:
            self._create()

    def _update(self):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(
                f'UPDATE events '
                f'SET description = \'{self._description}\', '
                f'date_created = \'{self._dateCreated}\' '
                f'WHERE id = {self._id};'
            )
        dBConnection.commit()

    def _create(self):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(
                f'INSERT INTO events(description, date_created) '
                f'VALUES(\'{self._description}\', '
                f'\'{self._dateCreated}\') '
                f'RETURNING id;'
            )
            data = cursor.fetchone()
            self._id = data['id']
            self._saved = True

        dBConnection.commit()

    @classmethod
    def _createFromDBData(
        cls,
        id_: int,
        description: str,
        dateCreated: date
    ) -> 'Event':
        event = Event(description, dateCreated)
        event._id = id_
        event._saved = True
        return event

    def delete(self):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(
                f'DELETE FROM events '
                f'WHERE id = {self._id};'
            )
            self._saved = False
            self._id = -1
        dBConnection.commit()

    @classmethod
    def selectByDate(cls, dateCreated: date):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            query = f'SELECT * FROM events WHERE date_created = \'{dateCreated}\''
            cursor.execute(query)
            events = cursor.fetchall()
            result = []
            for event in events:
                result.append(cls._createFromDBData(
                    event['id'],
                    event['description'],
                    event['date_created']
                ))
        return result

    @classmethod
    def selectById(cls, id_: int):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            query = f'SELECT * FROM events WHERE id = {id_}'
            cursor.execute(query)
            eventData = cursor.fetchone()
            if eventData is None:
                raise ValueError('There is no event with such id')
            event = cls._createFromDBData(
                eventData['id'],
                eventData['description'],
                eventData['date_created']
            )

            return event

    @classmethod
    def selectAll(cls):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            query = 'SELECT * FROM events '
            cursor.execute(query)
            events = cursor.fetchall()
            result = []
            for event in events:
                result.append(cls._createFromDBData(
                    event['id'],
                    event['description'],
                    event['date_created']
                ))
        return result


class Toy:
    def __init__(self, name: str, cost: Decimal, quantity: int, age: NumericRange) -> None:
        self._name = name
        self._cost = cost
        self._quantity = quantity
        self._age = age
        self._saved = False
        self._id = -1

# region Properties
    @property
    def id(self) -> int:
        if not self.saved:
            raise ValueError(
                'You can`t get id from item, which is not saved in DB')
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def cost(self) -> Decimal:
        return self._cost

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def age(self) -> NumericRange:
        return self._age

    @property
    def saved(self) -> bool:
        return self._saved

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @cost.setter
    def cost(self, value: Decimal) -> None:
        self._cost = value

    @quantity.setter
    def quantity(self, value: int) -> None:
        self._quantity = value

    @age.setter
    def age(self, value: NumericRange) -> None:
        self._age = value
# endregion

    def __str__(self) -> str:
        return (f'(id: {self._id}, name: {self._name}, '
                f'cost: {self._cost}, quantity: {self._quantity}, '
                f'age: {self._age})')

    def __repr__(self) -> str:
        return self.__str__()

    def save(self):
        if self._saved:
            self._update()
        else:
            self._create()

    def delete(self):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(
                f'DELETE FROM toys '
                f'WHERE id = {self._id};'
            )
            self._saved = False
            self._id = -1
        dBConnection.commit()

    @classmethod
    def deleteByName(cls, name: str):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(f'DELETE FROM toys WHERE name = \'{name}\'')

        dBConnection.commit()

    @classmethod
    def selectByAge(cls, ageLower: int, ageUpper: int, orderBy: str = None) -> List['Toy']:
        dBConnection = DBConfig.getDBConnection()
        with dBConnection.cursor() as cursor:
            query = (f'SELECT * FROM toys '
                     f'WHERE lower(age_restriction) <= {ageLower}'
                     f'AND upper(age_restriction) >= {ageUpper + 1} ')
            if orderBy is not None and orderBy in {'cost', 'name', 'quantity'}:
                query += f'ORDER BY {orderBy}'

            cursor.execute(query)

            result = []
            for data in cursor.fetchall():
                result.append(cls._createFromDBData(
                    data['id'],
                    data['name'],
                    data['cost'],
                    data['quantity'],
                    data['age_restriction']
                ))
        return result

    @classmethod
    def selectMostExpensive(
        cls,
        ageLower: int,
        ageUpper: int,
        maxCost: Decimal
    ) -> Union['Toy', None]:
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            query = (
                'SELECT * FROM toys '
                f'WHERE lower(age_restriction) <= {ageLower} '
                f'AND upper(age_restriction) >= {ageUpper + 1} '
                f'AND cost <= {maxCost}::money '
                'ORDER BY cost DESC '
                'LIMIT 1'
            )
            cursor.execute(query)

            data = cursor.fetchone()
            if not data:
                return None

            result = cls._createFromDBData(
                data['id'],
                data['name'],
                data['cost'],
                data['quantity'],
                data['age_restriction']
            )
        return result

    @classmethod
    def increaseCostForAge(cls, ageLower: int, ageUpper: int, multiplierAsPercentage: int):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(
                'UPDATE toys '
                f'SET cost = cost * {multiplierAsPercentage / 100}'
                f'WHERE lower(age_restriction) <= {ageLower} '
                f'AND upper(age_restriction) >= {ageUpper + 1}'
            )
        dBConnection.commit()

    def _update(self):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(
                f'UPDATE toys '
                f'SET name = \'{self._name}\', '
                f'cost = {self._cost}, '
                f'quantity = {self._quantity}, '
                f'age_restriction = \'{self._age}\' '
                f'WHERE id = {self._id};'
            )
        dBConnection.commit()

    def _create(self):
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(
                f'INSERT INTO toys(name, cost, quantity, age_restriction) '
                f'VALUES(\'{self._name}\', '
                f'{self._cost}, '
                f'{self._quantity}, '
                f'\'{self._age}\') '
                f'RETURNING id;'
            )
            data = cursor.fetchone()
            self._id = data['id']
            self._saved = True

        dBConnection.commit()

    @classmethod
    def _createFromDBData(
        cls,
        id_: int,
        name: str,
        cost: str,
        quantity: int,
        age: NumericRange
    ) -> 'Toy':
        toy = Toy(name, Decimal(
            cost.split()[0].replace(',', '.')), quantity, age)
        toy._id = id_
        toy._saved = True
        return toy

    @classmethod
    def selectById(cls, id_) -> 'Toy':
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM toys WHERE id = {id_};')
            data = cursor.fetchone()
            if not data:
                raise ValueError('There is no toy with specified id.')

            result = cls._createFromDBData(
                data['id'],
                data['name'],
                data['cost'],
                data['quantity'],
                data['age_restriction']
            )
        return result

    @classmethod
    def selectAllToys(cls) -> List['Toy']:
        dBConnection = DBConfig.getDBConnection()

        with dBConnection.cursor() as cursor:
            cursor.execute('SELECT * FROM toys;')

            result = []
            for data in cursor.fetchall():
                result.append(cls._createFromDBData(
                    data['id'],
                    data['name'],
                    data['cost'],
                    data['quantity'],
                    data['age_restriction']
                ))
        return result
