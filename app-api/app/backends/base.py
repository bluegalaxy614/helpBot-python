import orjson
import aiofiles
import aiofiles.os
import collections.abc


class FileStorage(collections.abc.MutableMapping):

    def __init__(self, file_path):
        self.path = file_path
        self.data = {}

        self._loaded = False
        self._mutated = False

    def __iter__(self):
        for key in self.data.keys():
            yield key

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self._mutated = True

    def __delitem__(self, key):
        del self.data[key]
        self._mutated = True

    async def __aenter__(self):
        if not self._loaded:
            self._loaded = True
            await self.loads()

        return self

    async def __aexit__(self, exc_type, exc, traceback):
        await self.aclose()

    async def aclose(self):
        if self._mutated:
            self._mutated = False
            await self.dumps()

    async def loads(self):
        file_exist = await aiofiles.os.path.exists(self.path)
        if file_exist:
            async with aiofiles.open(self.path, 'rb') as fh:
                file_data = await fh.read()
                self.data = orjson.loads(file_data)

    async def dumps(self):
        async with aiofiles.open(self.path, 'wb') as fh:
            file_data = orjson.dumps(self.data, option=orjson.OPT_INDENT_2)
            await fh.write(file_data)


class BaseBackend(FileStorage):

    async def keys(self):
        async with self:
            for key in self:
                yield key

    async def items(self):
        async with self:
            for key in self:
                yield key, self.data[key]

    async def values(self):
        async with self:
            for key in self:
                yield self.data[key]

    async def has(self, key):
        async with self:
            return key in self.data

    async def get(self, key, default=None):
        async with self:
            return self.data.get(key, default)

    async def put(self, key, value):
        async with self:
            self[key] = value

    async def insert(self, data, key_getter, defaults=None):

        item_data = {}
        if isinstance(defaults, dict):
            for name, value in defaults.items():
                item_data[name] = value() if callable(value) else value
        item_data.update(data)
        item_key = key_getter(item_data)

        await self.put(item_key, item_data)

        return item_data


    async def update(self, data, key_getter, previous=None):

        item_data = dict(previous) if isinstance(previous, dict) else {}
        item_data.update(data)

        item_key = key_getter(item_data)

        await self.put(item_key, item_data)

        return item_data

    async def delete(self, key):
        success = await self.has(key)
        if success:
            del self[key]
        return success


# class BaseBackend:

#     def __init__(self, file_path):
#         self.stor_dict = FileStorage(file_path)

#     async def items(self):
#         async with self.stor_dict as stor_dict:
#             for item_data in stor_dict.values():
#                 yield item_data

#     async def has(self, key):
#         async with self.stor_dict as stor_dict:
#             return key in stor_dict

#     async def get(self, key):
#         async with self.stor_dict as stor_dict:
#             return stor_dict.get(key)

#     async def insert(self, data, key_getter, defaults=None):

#         item_data = {}
#         if isinstance(defaults, dict):
#             for name, value in defaults.items():
#                 item_data[name] = value() if callable(value) else value
#         item_data.update(data)
#         item_key = key_getter(item_data)

#         async with self.stor_dict as stor_dict:
#             stor_dict[item_key] = item_data

#         return item_data


#     async def update(self, data, key_getter, previous=None):

#         item_data = dict(previous) if isinstance(previous, dict) else {}
#         item_data.update(data)

#         item_key = key_getter(item_data)

#         async with self.stor_dict as stor_dict:
#             stor_dict[item_key] = item_data

#         return item_data

#     async def delete(self, key):

#         success = False

#         async with self.stor_dict as stor_dict:
#             if key in stor_dict:
#                 del stor_dict[key]
#                 success = True

#         return success
