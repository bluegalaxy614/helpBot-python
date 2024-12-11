import httpx


class OpenApiEndpoint:
    def __init__(
        self, client, url, method,
        path_parameters=None,
        query_parameters=None,
        request_schema=None, response_schema=None,
        summary=None, description=None
    ):
        self.client = client
        self.url = url
        self.method = method
        self.request_schema = request_schema
        self.response_schema = response_schema
        self.summary = summary
        self.description = description

    def _get_form(self, request):
        req_firlds = set(self.request_schema.get('required', []))

        result = {}

        for name, prop in self.request_schema['properties'].items():
            if not isinstance(prop['type'], str):
                continue

            if prop['type'] not in {'string', 'number', 'integer', 'boolean'}:
                continue

            result[name] = {
                'name': name,
                'type': 'text',
                'value': prop.get('default', ''),
                'required': name in req_firlds,
                'label': prop.get('title', name.title()),
                'description': prop.get('description', ''),
            }
            if name == 'user_email':
                result[name]['type'] = 'hidden'
                result[name]['value'] = request.user.email

            elif prop['type'] == 'string':
                result[name]['minlength'] = prop.get('minLength', '')
                result[name]['maxlength'] = prop.get('maxLength', '')

                if prop.get('maxLength', 0) > 64:
                    result[name]['type'] = 'textarea'

            elif prop['type'] == 'number':
                result[name]['type'] = 'number'
                result[name]['min'] = prop.get('minimum', '')
                result[name]['max'] = prop.get('maximum', '')

        return result

    async def _get_form_data(self, request):
        form_data = {}

        async with request.form() as form:
            for key, val in form.multi_items():
                prev = form_data.get(key)

                if prev is None:
                    form_data[key] = val

                elif isinstance(prev, list):
                    form_data[key].append(val)

                else:
                    form_data[key] = [form_data[key], val]

        return form_data

    async def __call__(self, request, **params):
        params = {k: v for k, v in params.items() if v}
        result_data = None

        try:
            req_url = self.url.format(**params)
        except KeyError:
            return result_data

        if self.method == 'get':
            resp = await self.client.http_client.get(req_url, params=params)
            if resp.status_code == 200:
                result_data = resp.json()

        elif request.method == 'POST':
            submit_data = await self._get_form_data(request)

            if 'delete-action' in submit_data:
                await self.client.http_client.delete(req_url)

            else:
                resp = await self.client.http_client.post(req_url, data=submit_data)

                object_data = resp.json()
                errors_data = object_data.get('errors', {})

                if resp.status_code == 200:
                    result_data = {'form_success_data': object_data}

                elif errors_data:
                    result_data = self._get_form(request)

                    for key in tuple(result_data.keys()):
                        if key in submit_data:
                            result_data[key]['value'] = submit_data[key]
                        if key in errors_data:
                            result_data[key]['error'] = errors_data[key]
                # else:
                #     # result_data = object_data
                #     result_data = self._get_form(request)

                #     for key in tuple(result_data.keys()):
                #         if key in object_data:
                #             result_data[key]['value'] = object_data[key]

        elif self.method == 'post' and not params:
            result_data = self._get_form(request)

        elif self.method == 'post':

            result_data = self._get_form(request)

            for key in tuple(result_data.keys()):
                if key in params:
                    result_data[key]['value'] = params[key]

        return result_data


def deep_key(dct, path, sep='/'):
    result = dct

    for key in path.split(sep):
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            result = None
            break

    return result


class OpenApiClient:

    def __init__(self, schema_url, host=None, headers=None):
        self.base_url = host
        self.schema_url = schema_url
        self.schema = None

        self.http_client = None
        self.http_headers = headers

    def __await__(self):
        return self.ainit().__await__()

    async def ainit(self):
        self.http_client_timeout = httpx.Timeout(10.0, write=60.0, read=60.0)
        self.http_client = httpx.AsyncClient(
            verify=False,
            timeout=self.http_client_timeout,
            headers=self.http_headers or {}
        )

        resp = await self.http_client.get(self.schema_url)
        self.schema = resp.json()

        self._parse_schema()

        return self

    async def aclose(self):
        await self.http_client.aclose()

    def _component_schema(self, info):
        # 'content': {
        #     'application/json': {
        #         'schema': {
        #             '$ref': '#/components/schemas/item_read'
        #         }
        #         OR
        #         'schema': {
        #             'type': 'array',
        #             'items': {'$ref': '#/components/schemas/item_ref'}
        #         }
        #     }
        # }
        schema = deep_key(info, 'content;application/json;schema', sep=';')

        if not schema:
            pass

        elif '$ref' in schema:
            schema = deep_key(self.schema, schema['$ref'][2:], sep='/')

        elif schema['type'] == 'array' and '$ref' in schema['items']:
            schema['items'] = deep_key(self.schema, schema['items']['$ref'][2:], sep='/')

        return schema

    def _parse_schema(self):

        for url_path, methods in self.schema['paths'].items():
            for method, info in methods.items():
                opid = info.get('operationId')
                rsps = info.get('responses')

                if not opid or not rsps:
                    continue

                endpoint = OpenApiEndpoint(
                    client=self,
                    url=f'{self.base_url}{url_path}',
                    method=method,
                    request_schema=self._component_schema(info.get('requestBody')),
                    response_schema=self._component_schema(rsps.get('200')),
                    summary=info.get('summary'),
                    description=info.get('description'),
                )

                setattr(self, opid, endpoint)
                print(opid, url_path)
