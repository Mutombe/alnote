import sys
import asyncio
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from db import models
from db.session import engine, get_db
from routers import auth, notes, ai, exports, sync
from utils import security
from config import settings
from datetime import timedelta

# Fix for Windows event loop policy
#f sys.platform == "win32":
  #  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Create database tables

app = FastAPI(
    title="Cognitive Amplification Platform",
    description="AI-powered knowledge management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=3600  # 1 hour session
)

# Include routers - this is the correct way to integrate them
app.include_router(auth.router, prefix="/auth")
app.include_router(notes.router, prefix="/api/v1/notes")
app.include_router(ai.router, prefix="/api/v1/ai")
app.include_router(exports.router, prefix="/api/v1/exports")
app.include_router(sync.router, prefix="/api/v1/sync")

# Root endpoint
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    return """
    <html>
        <head>
            <title>Cognitive Amplification Platform</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                       margin: 0; padding: 0; background: linear-gradient(135deg, #1a2a6c, #b21f1f, #1a2a6c); 
                       color: white; min-height: 100vh; }
                .container { max-width: 900px; margin: 0 auto; padding: 2rem; }
                .header { text-align: center; margin-bottom: 2rem; }
                .card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); 
                        border-radius: 15px; padding: 2rem; margin-bottom: 2rem; 
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.18); }
                h1 { font-size: 2.5rem; margin-bottom: 1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
                p { font-size: 1.1rem; line-height: 1.6; }
                .btn { display: inline-block; background: #4e54c8; color: white; 
                       padding: 12px 24px; border-radius: 50px; text-decoration: none; 
                       font-weight: 600; margin: 10px 5px; transition: all 0.3s ease; 
                       box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
                .btn:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); 
                            background: #6a71e6; }
                .endpoints { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
                            gap: 1rem; margin: 1.5rem 0; }
                .endpoint-card { background: rgba(255, 255, 255, 0.15); border-radius: 10px; 
                                padding: 1.2rem; transition: transform 0.3s ease; }
                .endpoint-card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.2); }
                .endpoint-card h3 { margin-top: 0; border-bottom: 2px solid rgba(255,255,255,0.3); 
                                   padding-bottom: 0.5rem; }
                .features { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; }
                .feature { flex: 1; min-width: 200px; text-align: center; padding: 1rem; }
                .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
                footer { text-align: center; margin-top: 2rem; opacity: 0.8; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Cognitive Amplification Platform</h1>
                    <p>Your AI-powered knowledge management backend is running successfully!</p>
                </div>
                
                <div class="card">
                    <h2>🚀 Quick Start</h2>
                    <div class="features">
                        <div class="feature">
                            <div class="feature-icon">📚</div>
                            <h3>Explore API</h3>
                            <a href="/docs" class="btn">Interactive Docs</a>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">🔐</div>
                            <h3>Authentication</h3>
                            <a href="/auth/providers" class="btn">OAuth Providers</a>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">💡</div>
                            <h3>Health Check</h3>
                            <a href="/health" class="btn">System Status</a>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🔌 API Endpoints</h2>
                    <div class="endpoints">
                        <div class="endpoint-card">
                            <h3>📝 Notes</h3>
                            <p>Create, read, update and delete your knowledge notes</p>
                            <code>/api/v1/notes</code>
                        </div>
                        <div class="endpoint-card">
                            <h3>🧠 AI Services</h3>
                            <p>Semantic linking, knowledge graphs, and content processing</p>
                            <code>/api/v1/ai</code>
                        </div>
                        <div class="endpoint-card">
                            <h3>📤 Exports</h3>
                            <p>Export notes in multiple formats (PDF, Markdown, HTML)</p>
                            <code>/api/v1/exports</code>
                        </div>
                        <div class="endpoint-card">
                            <h3>🔄 Real-time Sync</h3>
                            <p>Collaborative editing with WebSocket support</p>
                            <code>/api/v1/sync</code>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🔍 Next Steps</h2>
                    <p>Connect your frontend application to start building your cognitive workspace:</p>
                    <ul>
                        <li>Implement OAuth login flow using <code>/auth/login</code> endpoints</li>
                        <li>Use JWT tokens for authenticated API requests</li>
                        <li>Explore the interactive API documentation for endpoint details</li>
                    </ul>
                </div>
                
                <footer>
                    <p>Need help? Check the project documentation or open an issue on GitHub</p>
                </footer>
            </div>
        </body>
    </html>
    """


#@app.post("/token", response_model=security.Token, include_in_schema=False)

#async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Dummy authentication for testing
    #if form_data.username == "test" and form_data.password == "test":
     #   access_token = security.create_access_token(
      #      data={"sub": "test-user"},
       #     expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        #)
        #return {"access_token": access_token, "token_type": "bearer"}
    
    #raise HTTPException(
     #   status_code=status.HTTP_401_UNAUTHORIZED,
      #  detail="Incorrect username or password",
       # headers={"WWW-Authenticate": "Bearer"},
    #)

#@app.get("/health", include_in_schema=False)
#async def health_check():
    #return {
        #"status": "healthy",
        #"version": "1.0.0",
       # "services": {
            #"database": "connected" if engine else "disconnected",
            #"ai": "ready",
            #"auth": "enabled"
        #}
    #}

# Error handlers
#@app.exception_handler(StarletteHTTPException)
#async def http_exception_handler(request, exc):
    #if exc.status_code == 404:
        #return RedirectResponse("/")
    #return JSONResponse(
        #status_code=exc.status_code,
        #content={"detail": exc.detail},
    #)

#@app.exception_handler(RequestValidationError)
#async def validation_exception_handler(request, exc):
    """
    Handles FastAPI request validation errors.

    Parameters:
    - request: The incoming HTTP request.
    - exc: The exception instance containing validation error details.

    Returns:
    - JSONResponse: A response with a 422 status code and details about the validation errors.
    """
    # Return a JSON response with status code 422 and error details
 #   return JSONResponse(
  #      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
   #     content={"detail": exc.errors(), "body": exc.body},
    #)

#@app.exception_handler(500)
#async def server_error_handler(request, exc):
 #   return JSONResponse(
  #      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
   #     content={"detail": "Internal server error"},
   # )

