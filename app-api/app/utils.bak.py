
def form_data_to_dict(form):
    result = {}

    for key, val in form.multi_items():
        prev = result.get(key)

        if prev is None:
            result[key] = val

        elif isinstance(prev, list):
            result[key].append(val)

        else:
            result[key] = [result[key], val]

    return result
