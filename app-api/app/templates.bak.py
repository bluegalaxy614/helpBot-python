import httpx
import jinja2
from starlette.routing import Mount
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.exceptions import HTTPException


async def load_json(url):
    async with httpx.AsyncClient(verify=False) as ahttpx:
        resp = await ahttpx.get(url)
        data = resp.json()
    return data


class TemplatesApp:

    def __init__(self, templates_dir, fallback_lang='en', debug=False):

        self.fallback_lang = fallback_lang

        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            auto_reload=True,
            autoescape=jinja2.select_autoescape(['html',]),
            enable_async=True,
        )
        self.env.globals['load_json'] = load_json

        if debug:
            self.env.add_extension('jinja2.ext.debug')

        self.paths = set([f'/{path}' for path in self.env.list_templates()])

    def get_template_path(self, path):

        if path.endswith('/'):
            path += 'index.html'

        _, lang, path_ext = path.split('/', 2)

        if path not in self.paths and lang != self.fallback_lang:
            path = f'/{self.fallback_lang}/' + path_ext

        return path if path in self.paths else None

    def get_template(self, template_path):
        return self.env.get_template(template_path)

    async def get_response(self, template, context):
        content = await template.render_async(context)
        return HTMLResponse(content, status_code=200)

    async def __call__(self, scope, receive, send):
        assert scope['type'] == 'http'

        if scope['method'] not in ('GET', 'HEAD'):
            raise HTTPException(status_code=405)

        raw_path = str(scope['path'])
        template_path = self.get_template_path(raw_path)

        if not template_path:
            raise HTTPException(status_code=404)

        request = Request(scope=scope)
        context = {
            'request': request,
        }
        template = self.get_template(template_path)
        response = await self.get_response(template, context)

        await response(scope, receive, send)
