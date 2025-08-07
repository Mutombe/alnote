from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class OAuthProvider(BaseModel):
    name: str
    authorize_url: str
    client_id: str

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: str
    provider: str
    
    # Updated configuration for Pydantic V2
    model_config = ConfigDict(from_attributes=True)

class OAuthCallback(BaseModel):
    code: str
    state: str