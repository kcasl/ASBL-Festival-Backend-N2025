from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import secrets
import crud
import schemas
import models
from datetime import datetime, timedelta
from database import engine, get_db
from stock_price_management import *
from starlette.middleware.cors import CORSMiddleware

# 모델 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_time = None
timer_duration = timedelta(minutes=10)

# 사용자 생성
@app.post("/register",
          tags=["계정 관리"],
          summary="고유학번, 비밀번호로 계정 생성 - 프롬프트에서 따로 처리할 예정.")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db, user)
        return db_user

    except Exception as e:
        return f"이미 존재하는 계정입니다. 관리자에게 문의해주세요. err : {e}"

# 사용자 정보 조회
@app.post("/login",
          tags=["계정 관리"],
          summary="등록한 정보를 기반으로 로그인. -> DB에서의 쿼리값과 같다면 true 반환.")
def read_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user(db, user.std_id)

        if user.password == db_user.password:
            token = secrets.token_urlsafe(16)
            info = crud.update_user(db, user.std_id)
            return [crud.save_token(db, user.std_id, token),info]
        else:
            return "비밀번호가 틀립니다. 다시 시도해주세요."
    except Exception as e:
        return f"계정 정보가 존재하지 않습니다. 회원가입 후 이용해주세요. err : {e}"

# 사용자 정보 업데이트

@app.post("/put_money")
def put_moeny(user: schemas.Money, db: Session = Depends(get_db)):
    try:
        dt = db.query(models.User).filter(models.User.std_id == user.std_id).first()
        dt.capital += user.capital
        db.commit()
        db.refresh(dt)
        return dt.capital
    except Exception as e:
        return f"계정 정보가 존재하지 않습니다. 관리자에게 문의해주세요. err : {e}"


@app.post("/update_capital",
         tags=["계정 관리"],
         summary="자본 정보 업데이트. -> 주식 수 * 해당 주식 가격")
def update_user(user: schemas.Info, db: Session = Depends(get_db)):
    try:
        info = crud.update_user(db, user.std_id)
        return info
    except Exception as e:
        return f"계정 정보가 존재하지 않습니다. 관리자에게 문의해주세요. err : {e}"

@app.get("/stock_init",
         tags=["주가 변동 관리"],
         summary="매 라운드 시작할 때 호출할 것. 주식 정보 초기화.")
def stock_init():
    stock_price_init(r.randint(300,400), r.randint(400, 500), r.randint(600,700), r.randint(300, 500))
    root_update()
    return "초기화 및 그래프 시작 성공."

@app.get("/get_news")
def get_news():
    return news_return[-1]

@app.post("/stock_trade", tags=["매도 / 매수"])
def stock_trade(user: schemas.Stocks, db: Session = Depends(get_db)):
    return crud.stock_trade(db, user)

@app.get("/stock_price_change", tags=["주가 변동 관리"])
def stock_price_change():
    return price_list_update()

@app.get("/start-timer")
def start_timer():
    global start_time
    if start_time is None:
        start_time = datetime.now()
        return {"message": "Timer started", "remaining_time": timer_duration.total_seconds()}
    else:
        raise HTTPException(status_code=400, detail="Timer is already running")

@app.get("/check-timer")
def check_timer():
    global start_time
    if start_time is None:
        raise HTTPException(status_code=400, detail="Timer has not been started yet")

    elapsed_time = datetime.now() - start_time
    remaining_time = timer_duration - elapsed_time

    if remaining_time.total_seconds() <= 0:
        return {"message": "종료.", "remaining_time": 0}

    return int(remaining_time.total_seconds())

@app.get("/reset-timer")
def reset_timer():
    global start_time
    start_time = None
    return {"message": "Timer reset"}