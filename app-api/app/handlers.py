import orjson
from operator import itemgetter
from starlette.routing import Route
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.responses import Response
from app.auth import SCOPE_ADMIN, SCOPE_OWNER, SCOPE_MEMBER
from app.responses import ORJSONResponse, HTTPValidationException


DEFAULT_SCOPES = {
    'list': [SCOPE_MEMBER],
    'read': [SCOPE_MEMBER],
    'create': [SCOPE_OWNER],
    'update': [SCOPE_OWNER],
    'delete': [SCOPE_OWNER],
}


DEFAULT_METHODS = {
    'list': 'GET',
    'read': 'GET',
    'create': 'POST',
    'update': 'POST',
    'delete': 'DELETE',
}


class JsonSchemaHandlers:
    def __init__(self, schema, backend, scopes=DEFAULT_SCOPES):
        self.schema = schema
        self.backend = backend

        self.scopes = {}

        for op_name, scps in scopes.items():
            if scps is None:
                pass
            elif isinstance(scps, str):
                self.scopes[op_name] = set([scps])
            else:
                self.scopes[op_name] = set(scps)

    def get_routes(self):
        routes = [
            # Route(
            #     path=f'/{self.schema.name_plural}/form',
            #     endpoint=self.form_create,
            #     methods=['GET'],
            #     name=f'api_{self.schema.name_plural}_form_create',
            # ),
            # Route(
            #     path=f'/{self.schema.name_plural}/{{{self.schema.key_field}}}/form',
            #     endpoint=self.form_update,
            #     methods=['GET'],
            #     name=f'api_{self.schema.name_plural}_form_update',
            # )
        ]

        for op_name, scopes in self.scopes.items():
            route_path = f'/{self.schema.name_plural}'
            if op_name not in {'list', 'create'}:
                route_path += '/{' + self.schema.key_field + '}'

            method = DEFAULT_METHODS[op_name]

            route = Route(
                path=route_path,
                endpoint=getattr(self, op_name),
                methods=[method],
                name=f'{self.schema.name_plural}_{op_name}',
            )
            routes.append(route)

        return routes

    async def request_body_as_dict(self, request):
        request_data = {}

        content_type = request.headers['content-type']

        # The request body as bytes: await request.body()
        # The request body, parsed as form data or multipart: async with request.form() as form:
        # The request body, parsed as JSON: await request.json()
        if content_type == 'application/json':
            body = await request.body()
            request_data = orjson.loads(body)

        # elif content_type == 'multipart/form-data':
        elif content_type in {'multipart/form-data', 'application/x-www-form-urlencoded'}:
            async with request.form() as form:
                for key, val in form.multi_items():
                    prev = request_data.get(key)

                    if prev is None:
                        request_data[key] = val

                    elif isinstance(prev, list):
                        request_data[key].append(val)

                    else:
                        request_data[key] = [request_data[key], val]

        return request_data

    def raise_for_invalid_scope(self, op_name, request: Request):
        # scopes = self.scopes.get(op_name)

        if op_name not in self.scopes:
            raise HTTPException(status_code=404, detail='Not Found')

        def_scopes = self.scopes[op_name]
        req_scopes = set(request.auth.scopes)

        if SCOPE_ADMIN in req_scopes:
            pass

        elif not def_scopes:
            pass

        elif def_scopes & req_scopes:
            pass

        else:
            raise HTTPException(status_code=403, detail='Forbidden')


    def raise_for_invalid_read_data(self, data):
        reponse_data, errors = self.schema.read_schema_validate(data)

        if errors:
            raise HTTPValidationException(errors=errors)

        return reponse_data


    async def list(self, request: Request):
        """ List of {schema.name_plural}
        """
        self.raise_for_invalid_scope('list', request)

        # proxy_set_header X-Req-Id      $request_id;
        # proxy_set_header X-Req-Sid     $request_sid;
        # proxy_set_header X-Req-Lang    $request_lang;
        # proxy_set_header X-Req-Theme   $request_theme;
        # proxy_set_header X-Req-Base    "/$request_lang/$request_section";
        # proxy_set_header X-User-Email  $user_email;
        # print('X-Req-Id', request.headers.get('X-Req-Id'))
        # print('X-Req-Lang', request.headers.get('X-Req-Lang'))
        # print('X-User-Email', request.headers.get('X-User-Email'))

        flt_fields = [
            f for f in self.schema.filtered_fields if f in request.query_params
        ]
        flt_getter = None
        flt_value = None
        if flt_fields:
            flt_getter = itemgetter(*flt_fields)
            flt_filter = flt_getter(request.query_params)

        response_data = []

        async for data in self.backend.values():
            data, errors = self.schema.ref_schema_validate(data)
            if errors:
                raise HTTPValidationException(errors=errors)

            if flt_fields:
                flt_value = flt_getter(data)
                if flt_value == flt_filter:
                    response_data.append(data)
            else:
                response_data.append(data)

        return ORJSONResponse(response_data)

    async def read(self, request: Request):
        """ Get an exist {schema.name}
        """
        self.raise_for_invalid_scope('read', request)

        key = request.path_params[self.schema.key_field]

        read_data = await self.backend.get(key)

        if not read_data:
            raise HTTPException(
                status_code=404,
                detail=f'The {self.schema.name} "{key}" was not found'
            )

        resp_data = self.raise_for_invalid_read_data(read_data)
        return ORJSONResponse(resp_data)

    async def create(self, request: Request):
        """ Create a new {schema.name}
        """
        self.raise_for_invalid_scope('create', request)

        req_data = await self.request_body_as_dict(request)

        new_data, errors = self.schema.post_schema_validate(req_data)

        if errors:
            raise HTTPValidationException(errors=errors)

        read_data = await self.backend.insert(
            new_data,
            key_getter=self.schema.key_getter,
            defaults=self.schema.defaults
        )

        resp_data = self.raise_for_invalid_read_data(read_data)
        return ORJSONResponse(resp_data)

    async def update(self, request: Request):
        """ Replace an exist {schema.name}
        """
        self.raise_for_invalid_scope('update', request)

        key = request.path_params[self.schema.key_field]

        req_data = await self.request_body_as_dict(request)

        new_data, errors = self.schema.post_schema_validate(req_data)

        if errors:
            raise HTTPValidationException(errors=errors)

        prev_data = await self.backend.get(key)
        if not prev_data:
            raise HTTPException(
                status_code=404,
                detail=f'The {self.schema.name} "{key}" was not found'
            )

        read_data = await self.backend.update(
            new_data,
            key_getter=self.schema.key_getter,
            previous=prev_data,
        )

        resp_data = self.raise_for_invalid_read_data(read_data)
        return ORJSONResponse(resp_data)

    async def delete(self, request: Request):
        """ Delete an exist {schema.name}
        """
        self.raise_for_invalid_scope('delete', request)

        key = request.path_params[self.schema.key_field]

        is_success = await self.backend.delete(key)

        if not is_success:
            raise HTTPException(
                status_code=404,
                detail=f'The {self.schema.name} "{key}" was not found'
            )

        return Response(status_code=204)

    # def _get_form(self):
    #     req_firlds = set(self.schema.post_schema.get('required', []))

    #     result = {}

    #     for name, prop in self.schema.post_schema['properties'].items():
    #         if prop['type'] not in {'string', 'number', 'integer', 'boolean'}:
    #             continue

    #         result[name] = {
    #             'name': name,
    #             'type': 'text',
    #             'value': prop.get('default', ''),
    #             'required': name in req_firlds,
    #             'label': name.title(),
    #             'description': prop.get('description', ''),
    #         }
    #         if prop['type'] == 'string':
    #             result[name]['minlength'] = prop.get('minLength', '')
    #             result[name]['maxlength'] = prop.get('maxLength', '')

    #             if prop.get('maxLength', 0) > 64:
    #                 result[name]['type'] = 'textarea'

    #         elif prop['type'] == 'number':
    #             result[name]['type'] = 'number'
    #             result[name]['min'] = prop.get('minimum', '')
    #             result[name]['max'] = prop.get('maximum', '')

    #     return result

    # async def form_create(self, request: Request):
    #     """ {schema.name} create form
    #     """

    #     form_data = self._get_form()
    #     return ORJSONResponse(form_data)

    # async def form_update(self, request: Request):
    #     """ {schema.name} update form
    #     """

    #     key = request.path_params[self.schema.key_field]

    #     resp_data = await self.backend.get(key)
    #     if not resp_data:
    #         raise HTTPException(
    #             status_code=404,
    #             detail=f'The {self.schema.name} "{key}" was not found'
    #         )

    #     form_data = self._get_form()

    #     for key, value in resp_data.items():
    #         if key in form_data:
    #             form_data[key]['value'] = value

    #     return ORJSONResponse(form_data)
