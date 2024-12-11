import asyncio
import httpx
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.websockets import WebSocketDisconnect


OPENAI_API_KEY = "sk-proj-OTVCGTlvFJZ7GwKbeCVzT3BlbkFJ4SwowCGeKYG1DrlebdhJ"
OPENAI_HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {OPENAI_API_KEY}',
    'OpenAI-Beta': 'assistants=v2',
}


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


def cast_message(msg):
    return {
        'id': msg['id'],
        'thread_id': msg['thread_id'],
        'assistant_id': msg['assistant_id'],
        'created_at': msg['created_at'],
        'role': msg['role'],
        'content': msg['content'][0]['text']['value'],
        'annotations': msg['content'][0]['text']['annotations'],
    }


async def wait_run_response(ahttp, assistant_id, thread_id):
    resp = await ahttp.post(
        f'https://api.openai.com/v1/threads/{thread_id}/runs',
        headers=OPENAI_HEADERS,
        json={'assistant_id': assistant_id}
    )
    run = resp.json()
    run_id = run['id']
    run_status = run['status']

    while run_status in {'queued', 'in_progress', 'cancelling'}:
        await asyncio.sleep(0.9)
        resp = await ahttp.get(
            f'https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}',
            headers=OPENAI_HEADERS,
        )
        run = resp.json()
        run_status = run['status']
        if run_status == 'failed':
            print('recv failed:', run, flush=True)

    return run

async def helpbot_ws_handler(ws):

    await ws.accept()

    ahttp = httpx.AsyncClient()

    assistant_id = ws.query_params.get('assistant')
    thread_id = ws.query_params.get('thread')

    try:
        resp = await ahttp.get(
            f'https://api.openai.com/v1/assistants/{assistant_id}',
            headers=OPENAI_HEADERS
        )
        assistant = resp.json()
        await ws.send_json(assistant)

        if thread_id:
            resp = await ahttp.get(
                f'https://api.openai.com/v1/threads/{thread_id}/messages',
                headers=OPENAI_HEADERS,
            )
            messages = resp.json()
            if 'error' in messages:
                thread_id = None
            else:
                for message in reversed(messages['data']):
                    await ws.send_json(cast_message(message))

        if not thread_id:
            resp = await ahttp.post(
                'https://api.openai.com/v1/threads',
                headers=OPENAI_HEADERS,
            )
            thread = resp.json()
            thread_id = thread['id']
            await ws.send_json(thread)

        while True:
            recv_msg = await ws.receive_text()

            resp = await ahttp.post(
                f'https://api.openai.com/v1/threads/{thread_id}/messages',
                headers=OPENAI_HEADERS,
                json={'role': 'user', 'content': recv_msg}
            )
            message = resp.json()
            await ws.send_json(cast_message(message))

            run = await wait_run_response(ahttp, assistant_id, thread_id)
            # await ws.send_json(run)

            resp = await ahttp.get(
                f'https://api.openai.com/v1/threads/{thread_id}/messages',
                headers=OPENAI_HEADERS,
                params={'run_id': run['id']}
            )
            messages = resp.json()
            if 'data' in messages and messages['data']:
                await ws.send_json(cast_message(messages['data'][0]))
            else:
                print('api.openai.com response:', messages)

    except WebSocketDisconnect:
        pass

    finally:
        await ahttp.aclose()


PRFX = 'http://core:8080/api/v1'


async def helpbot_assistants(request):
    ahttpx = request.app.state.http_client

    assistant_id = request.query_params.get('id')

    if request.method == 'POST':
        async with request.form() as form:
            submit_data = form_data_to_dict(form)

        if assistant_id and submit_data.get('delete') == assistant_id:
            resp = await ahttpx.delete(f'{PRFX}/assistants/{assistant_id}')
            return RedirectResponse(
                status_code=302,
                url=f'{request.url.path}'
            )

        elif assistant_id:
            resp = await ahttpx.post(
                f'{PRFX}/assistants/{assistant_id}',
                json=submit_data
            )
            submit_result = resp.json()
            submit_errors = submit_result.get('errors', {})

            if submit_errors:
                resp = await ahttpx.get(f'{PRFX}/assistants/{assistant_id}/form')
                form_data = resp.json()
                for key in tuple(form_data.keys()):
                    if key in submit_data:
                        form_data[key]['value'] = submit_data[key]
                    if key in submit_errors:
                        form_data[key]['error'] = submit_errors[key]
            else:
                return RedirectResponse(
                    status_code=302,
                    url=f'{request.url.path}?id={assistant_id}'
                )

        else:
            resp = await ahttpx.post(
                f'{PRFX}/assistants',
                json=submit_data
            )
            submit_result = resp.json()
            submit_errors = submit_result.get('errors', {})

            if submit_errors:
                resp = await ahttpx.get(f'{PRFX}/assistants/form')
                form_data = resp.json()
                for key in tuple(form_data.keys()):
                    if key in submit_data:
                        form_data[key]['value'] = submit_data[key]
                    if key in submit_errors:
                        form_data[key]['error'] = submit_errors[key]
            else:
                assistant_id = submit_result['id']
                return RedirectResponse(
                    status_code=302,
                    url=f'{request.url.path}?id={assistant_id}'
                )

    else:
        if assistant_id:
            resp = await ahttpx.get(f'{PRFX}/assistants/{assistant_id}/form')
            form_data = resp.json()
        else:
            resp = await ahttpx.get(f'{PRFX}/assistants/form')
            form_data = resp.json()

    resp = await ahttpx.get(f'{PRFX}/assistants')
    assistants_data = resp.json()

    context = {
        'request': request,
        'assistant_id': assistant_id,
        'assistants_data': assistants_data,
        'form_data': form_data
    }

    tmpl = request.app.state.templates
    template_path = request.scope['path']
    template_path = tmpl.get_template_path(f'{template_path}.html')
    template = tmpl.get_template(template_path)
    content = await template.render_async(context)
    return HTMLResponse(content, status_code=200)