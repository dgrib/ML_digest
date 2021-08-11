import typing
from pymongo import MongoClient
from pymongo.collection import Collection


class MyMongoClient:
    def __init__(self):
        self._client = MongoClient('localhost')
        self._db = self._client['ml_base']

    @property
    def client(self):
        return self._client

    @property
    def database(self):
        return self._db

    def create_collection(self, name: str) -> Collection:
        """
        Создать объект коллекции
        """
        return self.database.create_collection(name)

    def get_collection(self, name: str) -> Collection:
        """
        Получить объект коллекции
        """
        return self.database.get_collection(name)

    def save_and_update_database(self, collection: Collection, dataset: typing.List):
        """
        Проверить список данных на наличие в БД, если их нет, то сохранить в БД
        """
        new_objects = []
        for data in dataset:
            filters = {'$and': [{"name": data.get('name')},
                                {"date_publication": data.get('date_publication')}]}
            obj = self.get_documents_collection(collection, filters)
            if not list(obj):
                new_objects.append(data)
        if new_objects:
            collection.insert_many(new_objects)
            [print(f'Записано {_}') for _ in new_objects]

    def get_documents_collection(self, collection: Collection, filters: dict = {}):
        """
        Получить список документов конкретной коллекции, соответствующий фильтру
        """
        return list(collection.find(filters))