import httpx
import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from datetime import timedelta
from config import settings
from db.session import get_db
from db import models
from utils import security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from schemas.auth import Token, OAuthProvider, UserOut


router = APIRouter(tags=["Authentication"])

PROVIDERS = {
    "google": {
        "authorize_url": settings.GOOGLE_AUTHORIZE_URL,
        "token_url": settings.GOOGLE_TOKEN_URL,
        "userinfo_url": settings.GOOGLE_USERINFO_URL,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "scopes": "openid profile email"
    },
    "github": {
        "authorize_url": settings.GITHUB_AUTHORIZE_URL,
        "token_url": settings.GITHUB_TOKEN_URL,
        "userinfo_url": settings.GITHUB_USERINFO_URL,
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "scopes": "user:email"
    }
}

@router.get("/providers", response_model=dict)
async def get_oauth_providers():
    return {
        provider: OAuthProvider(
            name=provider,
            authorize_url=details["authorize_url"],
            client_id=details["client_id"]
        )
        for provider, details in PROVIDERS.items()
    }

@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    if provider not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not supported")
    
    # Generate state token to prevent CSRF
    state = security.generate_state_token()
    request.session["oauth_state"] = state
    request.session["oauth_provider"] = provider
    
    # Build authorization URL
    params = {
        "client_id": PROVIDERS[provider]["client_id"],
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": PROVIDERS[provider]["scopes"],
        "state": state,
        "access_type": "offline" if provider == "google" else None
    }
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    auth_url = f"{PROVIDERS[provider]['authorize_url']}?{urlencode(params)}"
    return RedirectResponse(auth_url)

@router.get("/callback")
async def oauth_callback(
    request: Request, 
    code: str, 
    state: str,
    db: Session = Depends(get_db)
):
    # Verify state token to prevent CSRF
    stored_state = request.session.get("oauth_state")
    provider = request.session.get("oauth_provider")
    
    if not stored_state or stored_state != state or not provider:
        raise HTTPException(status_code=400, detail="Invalid state token")
    
    # Exchange code for token
    token_data = await exchange_code_for_token(code, provider)
    
    # Get user info
    user_info = await get_user_info(token_data["access_token"], provider)
    
    # Create or get user
    user = get_or_create_user(db, user_info, provider)
    
    # Create JWT token
    access_token = security.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Redirect to frontend with token
    frontend_redirect = f"{settings.FRONTEND_REDIRECT_URI}/auth/callback?token={access_token}"
    return RedirectResponse(frontend_redirect)

async def exchange_code_for_token(code: str, provider: str):
    details = PROVIDERS[provider]
    data = {
        "client_id": details["client_id"],
        "client_secret": details["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.OAUTH_REDIRECT_URI
    }
    
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(details["token_url"], data=data, headers=headers)
        token_data = response.json()
        if response.status_code != 200 or "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to exchange token")
        return token_data

async def get_user_info(access_token: str, provider: str):
    details = PROVIDERS[provider]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(details["userinfo_url"], headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_info = response.json()
        
        # GitHub doesn't return email by default
        if provider == "github":
            email_response = await client.get("https://api.github.com/user/emails", headers=headers)
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_email = next((e for e in emails if e["primary"]), None)
                if primary_email:
                    user_info["email"] = primary_email["email"]
        
        return user_info

def get_or_create_user(db: Session, user_info: dict, provider: str):
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        # Create new user
        user = models.User(
            id=str(uuid.uuid4()),
            email=email,
            name=user_info.get("name", user_info.get("login", "")),
            provider=provider,
            provider_id=user_info.get("id", "")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real implementation, you would verify credentials against your database
    if form_data.username == "test" and form_data.password == "test":
        access_token = security.create_access_token(
            data={"sub": "test-user"},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )