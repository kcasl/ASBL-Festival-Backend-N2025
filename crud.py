from sqlalchemy.orm import Session
import models
import schemas

from stock_price_management import *



# 새로운 사용자 생성
def create_user(db: Session, user: schemas.UserCreate):

    db_user = models.User(std_id=user.std_id, username=user.username, password=user.password, capital=user.capital)
    db_stock = models.User_Stock(std_id=user.std_id,stock1=0, stock2=0, stock3=0, stock4=0)

    db.add(db_user)
    db.add(db_stock)

    db.commit()

    db.refresh(db_user)
    db.refresh(db_stock)

    return db_user

# 사용자 정보 업데이트
def update_user(db: Session, std_id: str):
    db_user = db.query(models.User).filter(models.User.std_id == std_id).first()
    db_stock = db.query(models.User_Stock).filter(models.User_Stock.std_id == std_id).first()
    if db_user and db_stock:
        if len(stock1_price_list) > 0:
            total_capital = (
                db_user.capital + #기본 자금
                db_stock.stock1 * stock1_price_list[-1] + # 주식 1 가격 합
                db_stock.stock2 * stock2_price_list[-1] + # 주식 2 가격 합
                db_stock.stock3 * stock3_price_list[-1] + # 주식 3 가격 합
                db_stock.stock4 * stock4_price_list[-1]   # 주식 4 가격 합
            )
        else:
            total_capital = db_user.capital
        now_capital = db_user.capital
        total_stock1 = db_stock.stock1
        total_stock2 = db_stock.stock2
        total_stock3 = db_stock.stock3
        total_stock4 = db_stock.stock4

        info = {
            'total_capital': total_capital,
            'capital': now_capital,
            'stock1': total_stock1,
            'stock2': total_stock2,
            'stock3': total_stock3,
            'stock4': total_stock4
        }

    return info

# 사용자 조회
def get_user(db: Session, std_id: str):
    return db.query(models.User).filter(models.User.std_id == std_id).first()

def save_token(db: Session, std_id: str, token: str):
    db_user = db.query(models.User).filter(models.User.std_id == std_id).first()
    db_user.token = token
    db.commit()
    db.refresh(db_user)
    return db_user

def stock_trade(db: Session, user: schemas.Stocks):
    db_user = db.query(models.User).filter(models.User.std_id == user.std_id).first()
    db_stock = db.query(models.User_Stock).filter(models.User_Stock.std_id == user.std_id).first()

    # code : int
    # 매수 / 매도할 주식 개수
    # stock_num: int
    # 매수 : 0 / 매도 : 1
    # mode: int

    if db_user and db_stock and (user.token == db_user.token):
        if user.mode == 0:
            update_capital = db_user.capital - (price_list_update()[user.code] * user.stock_num)

            if update_capital < 0:
                return "매수를 위한 자금이 부족합니다. 게임머니를 충전해주세요."
            else:
                db_user.capital = update_capital

                if user.code == 0:
                    db_stock.stock1 += user.stock_num
                elif user.code == 1:
                    db_stock.stock2 += user.stock_num
                elif user.code == 2:
                    db_stock.stock3 += user.stock_num
                elif user.code == 3:
                    db_stock.stock4 += user.stock_num

                db.commit()

                db.refresh(db_user)
                db.refresh(db_stock)
                return db_stock

        elif user.mode == 1:
            update_capital = db_user.capital + (price_list_update()[user.code] * user.stock_num)

            db_stocks = [db_stock.stock1, db_stock.stock2, db_stock.stock3, db_stock.stock4]

            if db_stocks[user.code] - user.stock_num < 0:
                return "주식의 보유량이 매도량보다 적습니다. 다시 시도해주세요."
            else:
                db_user.capital = update_capital

                if user.code == 0:
                    db_stock.stock1 -= user.stock_num
                elif user.code == 1:
                    db_stock.stock2 -= user.stock_num
                elif user.code == 2:
                    db_stock.stock3 -= user.stock_num
                elif user.code == 3:
                    db_stock.stock4 -= user.stock_num

                db.commit()

                db.refresh(db_user)
                db.refresh(db_stock)
                return db_stock
    else:
        return "잘못된 접근입니다. 관리자에게 문의해주세요."