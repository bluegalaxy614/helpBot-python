import time
import uuid
import string
import random


def naive_plural(word):

    if not word or len(word) <= 2:
        return word

    one = word[-1]
    two = word[-2:]

    if one in {'s', 'x', 'z', 'o'} or two in {'ss', 'sh', 'ch'}:
        # potato –> potatoes
        # pass -> passes
        return word + 'es'

    if two in {'ay', 'ey', 'iy', 'oy', 'uy'}:
        # boy -> boys
        return word + 's'

    if one == 'y':
        # entry -> entries
        return word[:-1] + 'ies'

    if two == 'is':
        # analysis – analyses
        return word[:-2] + 'es'

    return word + 's'


def cast_types(schema, raw_data):
    result_data = {}

    # allow types: "null", "boolean", "number", "integer", "string", "object", "array"
    for key, value in raw_data.items():
        prop = schema['properties'].get(key)
        prop_type = set()
        if prop and isinstance(prop['type'], list):
            prop_type = set(prop['type'])
        elif prop:
            prop_type = set([prop['type']])

        if prop is None or not prop_type:
            result_data[key] = value
        elif not isinstance(value, str):
            result_data[key] = value
        elif 'integer' in prop_type:
            try:
                result_data[key] = int(value)
            except ValueError:
                result_data[key] = value
        elif 'number' in prop_type:
            try:
                result_data[key] = float(value)
            except ValueError:
                result_data[key] = value
        else:
            result_data[key] = value

    return result_data


IS_REQ_PROP_MSG = ' is a required property'
IS_REQ_PROP_LEN = len(IS_REQ_PROP_MSG) + 1


def get_validation_errors(validator, data):

    errors = {}

    err_num = 0

    for err in validator.iter_errors(data):
        if err.instance_path:
            err_key = '.'.join(err.instance_path)
        elif err.message.endswith(IS_REQ_PROP_MSG):
            # "property_name" is a required property
            err_key = err.message[1:-IS_REQ_PROP_LEN]
        else:
            err_num += 1
            err_key = f'_{err_num}'

        errors[err_key] = err.message

    return errors

ALPHABET = string.ascii_lowercase + string.digits
BASE = len(ALPHABET)

def key_int_as_string(num: int) -> str:
    result = []
    
    while num > 0:
        num, remainder = divmod(num, BASE)
        result.append(ALPHABET[remainder])
    
    return ''.join(reversed(result)) or '0'


KEY_INT_GENERATOR_SUFIX = random.randint(10, 99)

def key_int_generator():
    return int(time.monotonic() * 1000) + KEY_INT_GENERATOR_SUFIX

def key_generator(key_schema):

    ks_type = key_schema['type']
    ks_format = key_schema.get('format')

    def _generator():
        key = None

        if ks_type == 'string' and ks_format == 'uuid':
            key = str(uuid.uuid4())

        elif ks_type == 'string':
            key = key_int_as_string(key_int_generator())

        elif ks_type == 'integer':
            key = key_int_generator()

        return key

    return _generator
