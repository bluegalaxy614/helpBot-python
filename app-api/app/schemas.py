import orjson
from types import SimpleNamespace
from functools import cached_property
from operator import itemgetter
from jsonschema_rs import validator_for, ValidationError
from starlette.schemas import BaseSchemaGenerator
from app.responses import ORJSONResponse
from app.schemas_util import (
    naive_plural, cast_types, get_validation_errors, key_generator
)


class JsonSchemaDescriber:

    def __init__(self, schema, name, name_plural=None):
        self._schema = schema
        self._properties = self._schema['properties']

        self.name = name
        self.name_plural = name_plural or naive_plural(self.name)

        self.key_field = next(iter(self._properties))
        self.key_getter = itemgetter(self.key_field)

        self.rostered_fields = self._schema.get('rostered', [self.key_field])
        self.filtered_fields = self._schema.get('filtered', [])
        # self.rostered_getter = itemgetter(*self.rostered_fields)

        self._read_validator = validator_for(self.read_schema)
        self._post_validator = validator_for(self.post_schema)

        self._nmz = SimpleNamespace(
            ref_schema=f'{self.name}_ref',
            post_schema=f'{self.name}_post',
            read_schema=f'{self.name}_read',
        )

    @classmethod
    def load(cls, schema_path, name=None, name_plural=None):
        with open(schema_path, mode='rb') as fh:
            schema_json = fh.read()

        schema = orjson.loads(schema_json)
        schema_name = name
        if not schema_name:
            _, schema_name = schema_path.rsplit('/', 1)
            schema_name, _ = schema_name.split('.', 1)

        return cls(schema, schema_name, name_plural=name_plural)

    @cached_property
    def key_schema(self):
        return self._properties[self.key_field]

    @cached_property
    def key_as_parameter(self):
        return {
            'name': self.key_field,
            'in': 'path',
            'required': True,
            'description': self.key_schema.get('description', ''),
            'schema': self.key_schema
        }

    @cached_property
    def defaults(self):
        result = {}

        for name, prop in self._properties.items():
            if name == self.key_field:
                result[name] = key_generator(self.key_schema)

            elif 'default' in prop:
                result[name] = prop['default']

            elif 'null' in prop['type']:
                result[name] = None

            elif prop['type'] == 'object':
                result[name] = dict

            elif prop['type'] == 'array':
                result[name] = list

        return result

    @cached_property
    def ref_schema(self):
        schema = {
            'type': 'object',
            'properties': {}
        }

        for name, prop in self._properties.items():
            if name in self.rostered_fields:
                schema['properties'][name] = prop
        
        return schema

    @cached_property
    def read_schema(self):
        req_fields = set(self._schema.get('required', []))
        req_fields.add(self.key_field)

        properties = {}

        for name, prop in self._properties.items():
            if prop.get('writeOnly', False):
                req_fields.discard(name)
            else:
                properties[name] = prop

        schema = {
            'type': 'object',
            'required': list(req_fields),
            'title': self._schema.get('title', ''),
            'description': self._schema.get('description', ''),
            'additionalProperties': self._schema.get('additionalProperties', False),
            'properties': properties,
        }
        
        return schema

    @cached_property
    def post_schema(self):

        req_fields = set(self._schema.get('required', []))
        properties = {}

        for name, prop in self._properties.items():
            if prop.get('readOnly', False):
                req_fields.discard(name)
            else:
                properties[name] = prop
                if prop['type'] == 'array':
                    pass
                elif prop['type'] == 'object':
                    pass
                elif not prop.get('default') and 'null' not in prop['type']:
                    req_fields.add(name)

        req_fields.discard(self.key_field)
        properties.pop(self.key_field)

        schema = {
            'type': 'object',
            'required': list(req_fields),
            'additionalProperties': False,
            'properties': properties,
        }

        return schema

    def ref_schema_validate(self, raw_data):
        out_data = {n: raw_data.get(n) for n in self.rostered_fields}
        errors = None
        return out_data, errors

    def read_schema_validate(self, raw_data):
        rprops_ = self.read_schema['properties']

        out_data = {k: v for k, v in raw_data.items() if k in rprops_}
        errors = get_validation_errors(self._read_validator, out_data)
        return out_data, errors

    def post_schema_validate(self, raw_data):

        out_data = cast_types(self.post_schema, raw_data)

        errors = get_validation_errors(self._post_validator, out_data)

        return out_data, errors

    def get_operation_schema(self, func):
        func_name = func.__name__
        func_self = getattr(func, '__self__', None)
        func_scopes = []

        if func_self and hasattr(func_self, 'scopes'):
            func_scopes = func_self.scopes.get(func_name, [])

        summary = func.__doc__.strip(' \n') if func.__doc__ else ''
        description = ''

        if '\n\n' in summary:
            summary, description = summary.split('\n\n', 1)
            description = description.strip(' \n')

        if summary and func_self:
            summary = summary.format(**func_self.__dict__)

        if description and func_self:
            description = description.format(**func_self.__dict__)

        operation_schema = {
            'security': [{'ApiKeyAuth': []}] if func_scopes else [],
            'summary': summary,
            'description': description,
            'operationId': f'{self.name_plural}_{func_name}',
            'responses': {}
        }

        components_schemas = {
        }

        res_read_content_ = {
            'application/json': {
                'schema': {
                    "$ref": f"#/components/schemas/{self._nmz.read_schema}"
                }
            }
        }
        req_body_content_ = {
            'application/json': {
                'schema': {
                    "$ref": f"#/components/schemas/{self._nmz.post_schema}"
                }
            },
            'application/x-www-form-urlencoded': {
                'schema': {
                    "$ref": f"#/components/schemas/{self._nmz.post_schema}"
                }
            }
        }
        req_fields_str = '`' + '`, `'.join(self.post_schema.get('required', [])) + '`'


        if func_name == 'list':
            operation_schema['parameters'] = []
            for field_name in self.filtered_fields:
                field_schema = self._properties[field_name]
                operation_schema['parameters'].append({
                    'name': field_name,
                    'in': 'query',
                    'description': field_schema.get('description', ''),
                    'schema': field_schema
                })

            operation_schema['responses']['200'] = {
                'description': f'returns a list of {self.name_plural}',
                'content': {
                    'application/json': {
                        'schema': {
                            "type": "array",
                            "items": {
                                "$ref": f"#/components/schemas/{self._nmz.ref_schema}"
                            }
                        }
                    }
                }
            }
            components_schemas[self._nmz.ref_schema] = self.ref_schema

        elif func_name == 'read':
            operation_schema['parameters'] = [self.key_as_parameter]
            operation_schema['responses']['200'] = {
                'description': f'returns a specific {self.name}',
                'content': res_read_content_
            }
            operation_schema['responses']['404'] = {
                '$ref': "#/components/responses/Http404"
            }
            components_schemas[self._nmz.read_schema] = self.read_schema

        elif func_name == 'create':

            operation_schema['requestBody'] = {
                'description': f'Required fields: {req_fields_str}',
                'content': req_body_content_
            }
            operation_schema['responses']['200'] = {
                'description': f'creates one of {self.name}',
                'content': res_read_content_
            }
            operation_schema['responses']['400'] = {
                '$ref': "#/components/responses/Http400"
            }
            components_schemas[self._nmz.post_schema] = self.post_schema
            components_schemas[self._nmz.read_schema] = self.read_schema

        elif func_name == 'update':
            operation_schema['parameters'] = [self.key_as_parameter]
            operation_schema['requestBody'] = {
                'description': f'Required fields: {req_fields_str}',
                'content': req_body_content_
            }
            operation_schema['responses']['200'] = {
                'description': f'updates a specific {self.name}',
                'content': res_read_content_
            }
            operation_schema['responses']['400'] = {
                '$ref': "#/components/responses/Http400"
            }
            operation_schema['responses']['404'] = {
                '$ref': "#/components/responses/Http404"
            }
            components_schemas[self._nmz.read_schema] = self.read_schema

        elif func_name == 'delete':
            operation_schema['parameters'] = [self.key_as_parameter]
            operation_schema['responses']['204'] = {
                'description': f'deletes a specific {self.name}',
            }
            operation_schema['responses']['404'] = {
                '$ref': "#/components/responses/Http400"
            }

        # else:
        #     schema['responses']['default'] = {
        #         '$ref': "#/components/responses/Http500",
        #     }

        return operation_schema, components_schemas



OPENAPI_SCHEMA_BASE = {
    "openapi": "3.1.0",
    "info": {
        "version": "3.1.0",
        "title": "The Project API",
        "summary": "",
        "description": ""
    },
    "paths": {},
    "components": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header"
            }
        },
        "schemas": {},
        "responses": {
            "Http204": {
                "description": "Success (No Content)",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["code", "message"],
                            "properties": {
                                "code": {"type": "integer", "const": 204},
                                "message": {"type": "string"}
                            },
                            "examples": [{
                                "code": 204,
                                "message": "No Content"
                            }]
                        }
                    }
                }
            },

            "Http400": {
                "description": "Bad Request (Validation Errors)",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["code", "message", "errors"],
                            "properties": {
                                "code": {"type": "integer", "const": 400},
                                "message": {"type": "string"},
                                "errors": {"type": "object"}
                            },
                            "examples": [{
                                "code": 400,
                                "message": "Validation Errors",
                                "errors": {
                                    "slug": "\"slug\" is shorter than 6 characters",
                                    "name": "\"name\" is a required property"
                                }
                            }]
                        }
                    }
                }
            },

            "Http404": {
                "description": "Entity not found",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["code", "message"],
                            "properties": {
                                "code": {"type": "integer", "const": 404},
                                "message": {"type": "string"}
                            },
                            "examples": [{
                                "code": 404,
                                "message": "The category \"main_news\" was not found"
                            }]
                        }
                    }
                }
            },

            "Http500": {
                "description": "Unexpected error",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["code", "message"],
                            "properties": {
                                "code": {
                                    "type": "integer",
                                    "minimum": 500,
                                    "maximum": 599
                                },
                                "message": {"type": "string"}
                            },
                            "examples": [{
                                "code": 500,
                                "message": "Internal Server Error",
                            }]
                        }
                    }
                }
            }
        },
        "parameters": {
            "idParam": {
                "name": "id",
                "in": "path",
                "description": "ID of enttity",
                "required": True,
                "schema": {
                    "type": "string"
                }
            }
        }
    }
}


def generate_openapi_schema(
        routes, version='1.0.0', title='The Project API', description='',
        terms_of_service=None, contact=None, license=None
):
    schema = dict(OPENAPI_SCHEMA_BASE)

    schema['info'].update({
        "version": version,
        "title": title,
        "description": description,
    })

    if terms_of_service:
        schema['info']['termsOfService'] = terms_of_service

    if contact:
        schema['info']['contact'] = dict(contact)

    if license:
        schema['info']['license'] = dict(license)

    # look to https://github.com/encode/starlette/blob/master/starlette/schemas.py
    schema_gen_ = BaseSchemaGenerator()

    for endpoint in schema_gen_.get_endpoints(routes):
        if not endpoint.func.__doc__:
            continue

        func_self = getattr(endpoint.func, '__self__', None)
        if not func_self:
            continue

        describer = getattr(func_self, 'schema', None)
        if not describer:
            continue

        if endpoint.path not in schema['paths']:
            schema['paths'][endpoint.path] = {}

        if describer:
            op_schema, cp_schemas = describer.get_operation_schema(endpoint.func)
            schema['paths'][endpoint.path][endpoint.http_method] = op_schema
            schema['components']['schemas'].update(cp_schemas)

    return schema


def openapi_schema_handler(request):
    app = request.app

    if not hasattr(app.state, 'openapi_schema'):
        app.state.openapi_schema = generate_openapi_schema(app.routes)

    return ORJSONResponse(app.state.openapi_schema)
