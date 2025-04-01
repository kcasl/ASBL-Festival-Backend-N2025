from pydantic import BaseModel

class UserCreate(BaseModel):
    std_id: str
    username: str
    password: str
    capital: float

class UserLogin(BaseModel):
    std_id: str
    password: str

class Info(BaseModel):
    std_id: str

class Money(BaseModel):
    std_id: str
    capital: float

class Stocks(BaseModel):
    std_id: str
    token: str
    #주식 code => 삼성 양성자 : 0 / 에스게이 : 1 / GL : 2 / 오이 : 3
    code : int
    #매수 / 매도할 주식 개수
    stock_num: int
    #매수 : 0 / 매도 : 1
    mode: int

# class UserUpdate(BaseModel):
#     capital: float = None

# class UserResponse(BaseModel):
#     std_id: str
#     username: str
#     password: str
#     capital: float

    class Config:
        orm_mode = True
