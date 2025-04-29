from pydantic import BaseModel

class APIKeyBase(BaseModel):
    exchange: str
    api_name: str
    api_key: str
    api_secret: str | None = None

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyOut(APIKeyBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True