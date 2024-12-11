import orjson
import aiofiles
import aiofiles.os
from heapq import heappush, heappop

class BaseBackend:

    def __init__(self, data_dir):
        self.data_dir = data_dir

    async def ainit(self):
        await aiofiles.os.makedirs(self.data_dir, exist_ok=True)

    async def aclose(self):
        pass

    def _get_key(self, key):
        return key() if callable(key) else key

    def _get_path(self, key):
        return f'{self.data_dir}/{key}.json'

    async def _dump_file(self, key, data):
        file_path = self._get_path(key)

        async with aiofiles.open(file_path, 'wb') as fh:
            file_data = orjson.dumps(data, option=orjson.OPT_INDENT_2)
            await fh.write(file_data)
        return file_path

    async def _delete_file(self, key):
        file_path = self._get_path(key)
        await aiofiles.os.remove(file_path)

    async def _get_keys(self):
        keys_items = []

        for entry in await aiofiles.os.scandir(self.data_dir):
            if entry.is_file() and entry.name.endswith('.json'):
                stat = entry.stat()
                # max-heap implementation
                # https://stackoverflow.com/questions/2501457/
                heappush(keys_items, (-stat.st_mtime, entry.name[:-5]))

        keys = []

        while keys_items:
            _, key = heappop(keys_items)
            keys.append(key)

        return keys

    async def items(self):

        keys = await self._get_keys()
        for key in keys:
            item_data = await self.get(key)
            yield item_data

    async def has(self, key):
        file_path = self._get_path(key)
        file_exist = await aiofiles.os.path.exists(file_path)

        return file_exist

    async def get(self, key):
        item_data = None

        file_path = self._get_path(key)
        file_exist = await aiofiles.os.path.exists(file_path)

        if file_exist:
            async with aiofiles.open(file_path, 'rb') as fh:
                file_data = await fh.read()
                item_data = orjson.loads(file_data)

        return item_data

    async def insert(self, data, key_getter, defaults=None):

        item_data = {}
        if isinstance(defaults, dict):
            for name, value in defaults.items():
                item_data[name] = value() if callable(value) else value
        item_data.update(data)

        await self._dump_file(key_getter(item_data), item_data)

        return item_data


    async def update(self, data, key_getter, previous=None):

        item_data = dict(previous) if isinstance(previous, dict) else {}
        item_data.update(data)

        await self._dump_file(key_getter(item_data), item_data)

        return item_data

    async def delete(self, key):

        file_path = self._get_path(key)
        file_exist = await aiofiles.os.path.exists(file_path)

        if file_exist:
            await aiofiles.os.remove(file_path)

        return file_exist
