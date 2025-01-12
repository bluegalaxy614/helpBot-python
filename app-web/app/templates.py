import httpx
import jinja2
from jinja2.utils import Namespace
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.exceptions import HTTPException
from app import settings
from app.utils import get_create_csrf_token



class Templates:

    def __init__(self, templates_dir, fallback_lang='en', debug=False):

        self.fallback_lang = fallback_lang

        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            auto_reload=True,
            autoescape=jinja2.select_autoescape(['html',]),
            enable_async=True,
        )

        if debug:
            self.env.add_extension('jinja2.ext.debug')

        self._state_defaults = {
            'project_name': settings.PROJECT_NAME,
            'project_domain': settings.PROJECT_DOMAIN,
            'project_title': settings.PROJECT_TITLE,
            'project_description': settings.PROJECT_DESCRIPTION,
            'lang': '',
            'theme': '',

            'static_url': settings.STATIC_URL,
            'auth_required': False,

            'page_title': '',
            'page_keywords': '',
            'page_description': '',

            'show_navbar': True,
            'show_sidebar': False,
            'show_downbar': True,

            'template_base': self.env.get_template('base/base.html'),
            'template_navbar': self.env.get_template('base/navbar.html'),
            'template_downbar': self.env.get_template('base/downbar.html'),
        }

        self.paths = set([f'/{path}' for path in self.env.list_templates()])
        self.auth_required_paths = set()

        for path in self.paths:
            with open(f'{templates_dir}{path}', 'rb') as fp:
                text = fp.read()
                if 'set state.auth_required = True' in str(text):
                    self.auth_required_paths.add(path)

    def get_template_path(self, request):
        tmpl_path = request.url.path
        if tmpl_path.endswith('/'):
            tmpl_path += 'index.html'

        _, lang, path_ext = tmpl_path.split('/', 2)

        if tmpl_path not in self.paths and lang != self.fallback_lang:
            tmpl_path = f'/{self.fallback_lang}/' + path_ext

        return tmpl_path

    async def handler(self, request):
        tmpl_path = self.get_template_path(request)

        if tmpl_path not in self.paths:
            raise HTTPException(status_code=404)

        if tmpl_path in self.auth_required_paths and not request.user.is_authenticated:
            _, lang, _ = request.url.path.split('/', 2)
            
            return RedirectResponse(
                url=f'/{lang}/user/sign-in.html?rd={request.url.path}',
                status_code=302
            )

        template = self.env.get_template(tmpl_path)

        state = dict(self._state_defaults)
        _, state['lang'], _ = request.url.path.split('/', 2)
        context = {
            'state': Namespace(**state),
            'request': request,
            'internal_api': request.app.state.internal_api,
            'errors' : request.session.get('errors'),
            'messages' : request.session.get('messages')
            #'csrf_token' : request.session.get("csrf_token")
        }

        self.clean_session(request)

        html_content = await template.render_async(context)
        return HTMLResponse(html_content, status_code=200)
   
    
    def clean_session(self, request):
        if request.session.get("errors") is not None:
            request.session.pop("errors")

        if request.session.get("messages") is not None:
            request.session.pop("messages")
