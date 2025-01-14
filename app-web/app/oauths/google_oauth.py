import bcrypt
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app import settings

oauth = OAuth()

google = oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params={'prompt': 'consent'},
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': settings.GOOGLE_AUTH_SCOPE
    },
)

async def handle_google_oauth(request: Request):
    """
    Start the Google OAuth flow by redirecting
    the user to Google's OAuth consent screen.
    """
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await google.authorize_redirect(request, redirect_uri)


async def handle_google_callback(request: Request, users_collection):
    token = await google.authorize_access_token(request)
    resp = await google.get('userinfo', token=token)
    user_info = resp.json()

    email = user_info.get("email")
    user = await request.app.state.db[settings.USER_COLLECTION_NAME].users_collection.find_one(
        {"email": email}
    )

    if not user:
        user = {
            "email": email,
            "username" : email.strip("@")[0],
            "auth_provider": "google",
        }
        try:
            result = await request.app.state.db[settings.USER_COLLECTION_NAME].insert_one(new_user)
        except Exception as error:
            request.session['errors'] = ["Unable to register user using google oauth!"]
            return RedirectResponse(url="/en/user/sign-in.html", code=302)
        
    request.session['users_email'] = email
    return RedirectResponse(url="/en/user/profile.html", status_code=302)
