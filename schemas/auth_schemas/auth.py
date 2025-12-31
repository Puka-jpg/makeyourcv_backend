from pydantic import BaseModel, EmailStr


class SignupInputSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class LoginInputSchema(BaseModel):
    email: EmailStr
    password: str


class LoginOutputSchema(BaseModel):
    access: str
    refresh: str


class RefreshTokenSchema(BaseModel):
    refresh: str
