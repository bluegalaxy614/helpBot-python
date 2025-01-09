import httpx
from openai import AsyncOpenAI
from app import settings
from app.backends.base import BaseBackend
from app.responses import HTTPValidationException


openai = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)

class AssistantsBackend(BaseBackend):

    def __init__(self, file_path, api_key, model='gpt-4o-mini'):
        super().__init__(file_path)

        self._model = model

        self._http_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'OpenAI-Beta': 'assistants=v2',
        }
        self._http_client = None
        self._api_prefix = 'https://api.openai.com/v1'

    async def loads(self):
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(headers=self._http_headers)

        resp = await self._http_client.get(
            f'{self._api_prefix}/assistants?order=desc&limit=100',
        )

        resp_data = resp.json()

        self.data = {}
        for item_data in resp_data['data']:
            item_key = item_data['id']
            item_data['user_email'] = item_data['metadata']['user_email']
            self.data[item_key] = item_data

        self._mutated = True

    async def insert(self, data, key_getter, defaults=None):

        assistant_name = data['name']
        user_email = data.pop('user_email', '')

        resp = await self._http_client.post(
            f'{self._api_prefix}/vector_stores',
            headers=self._http_headers,
            json={'name': f'Vector Store for {assistant_name!r}'}
        )
        vstore_data = resp.json()
        vstore_id = vstore_data['id']

        submit_data = {
            'model': self._model,
            'tools': [{'type': 'file_search'}],
            'tool_resources': {
                "file_search": {
                    "vector_store_ids": [vstore_id]
                }
            },
            'metadata': {
                'user_email': user_email,
                'vector_store_id': vstore_id,
            }
        }
        submit_data.update(data)

        resp = await self._http_client.post(
            'https://api.openai.com/v1/assistants',
            headers=self._http_headers,
            json=submit_data
        )

        assistant_data = resp.json()

        if 'error' in assistant_data:
            raise HTTPValidationException(
                detail=str(assistant_data)
            )

        assistant_data['vector_store_id'] = vstore_id
        assistant_data['user_email'] = user_email

        return await super().insert(
            assistant_data,
            key_getter,
            defaults=defaults
        )


    async def update(self, data, key_getter, previous=None):

        submit_data = dict(data)
        user_email = submit_data.pop('user_email', '')

        upload_files = submit_data.pop('upload_files', [])
        upload_files = [n for n in upload_files if n]

        assistant_id = previous['id']
        vstore_id = previous['metadata'].get('vector_store_id')

        if upload_files:
            old_files = previous.get('upload_files', [])
            new_files = set(upload_files) - set(old_files)

            upload_files = list(set(old_files) | set(upload_files))

            fpaths = [f'{settings.DATA_DIR}{path}' for path in new_files]
            fstreams = [open(path, "rb") for path in fpaths]

            if fstreams:
                file_batch = await openai.beta.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=vstore_id,
                    files=fstreams
                )
                print(f'uploaded {len(fpaths)} files for {assistant_id}', file_batch)

        resp = await self._http_client.post(
            f'{self._api_prefix}/assistants/{assistant_id}',
            headers=self._http_headers,
            json=submit_data
        )

        assistant_data = resp.json()

        if 'error' in assistant_data:
            raise HTTPValidationException(
                detail=str(assistant_data)
            )

        assistant_data['upload_files'] = upload_files
        assistant_data['user_email'] = user_email

        return await super().update(
            assistant_data,
            key_getter,
            previous=previous
        )

    async def delete(self, key):

        assistant_data = await self.get(key)
        success = False

        if assistant_data:
            vstore_id = assistant_data['metadata'].get('vector_store_id')
            if vstore_id:
                await self._http_client.delete(
                    f'{self._api_prefix}/vector_stores/{vstore_id}',
                    headers=self._http_headers,
                )

            await self._http_client.delete(
                f'{self._api_prefix}/assistants/{key}',
                headers=self._http_headers,
            )

            await super().delete(key)

            success = True

        return success
