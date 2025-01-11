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
    """
    Handle the OAuth callback from Google. 
    Exchange code for token, and retrieve user info.
    """
    token = await google.authorize_access_token(request)
    resp = await google.get('userinfo', token=token)
    user_info = resp.json()

    # user_info might contain { 'email': 'xxx', 'name': 'xxx', 'picture': 'xxx', ... }

    # Store or update user in DB
    email = user_info.get("email")
    existing_user = await users_collection.find_one({"email": email})

    if not existing_user:
        # Create a new user doc
        new_user = {
            "email": email,
            "name": user_info.get("name"),
            "auth_provider": "google",
        }
        result = await users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
    else:
        user_id = str(existing_user["_id"])

    # Save user info in session
    request.session.update({
        "user_id": user_id,
        "email": email,
        "is_authenticated": True
    })

    return RedirectResponse(url="/profile", status_code=302)
