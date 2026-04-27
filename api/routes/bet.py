# -*- coding: utf-8 -*-
"""
投注相关路由
提供下注、查询投注记录等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from database.db_core import SelfDB, DataDB
from database.server_models.bet_models import BetRecord, BetOrder
from database.server_models.user_models import User, UserBalanceLog
from database.data_models.tczq_models import TczqMatch
from core.models import ResponseModel
from core.deps import get_current_user
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter(prefix="/bet", tags=["投注"])


class PlaceBetRequest(BaseModel):
    """下注请求模型"""
    match_id: int = Field(..., description="比赛ID")
    bet_type: str = Field(..., description="投注类型 (spf/handicap_spf/total_goal/score)")
    bet_option: str = Field(..., description="投注选项 (3/1/0等)")
    odds: float = Field(..., gt=0, description="赔率")
    amount: float = Field(..., gt=0, description="投注金额")
    handicap: Optional[str] = Field(None, description="让球数")


class PlaceMultipleBetRequest(BaseModel):
    """串关下注请求模型"""
    bets: list = Field(..., min_items=2, description="投注列表")
    total_amount: float = Field(..., gt=0, description="总投注金额")


@router.post("/place", response_model=ResponseModel)
async def place_bet(
    bet_data: PlaceBetRequest,
    current_user: dict = Depends(get_current_user)
):
    """单注下注"""
    db_self = SelfDB()
    db_data = DataDB()
    
    try:
        # 获取用户信息
        user = db_self.query(User).filter(User.username == current_user["username"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 检查余额
        if user.balance < bet_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # 验证比赛是否存在
        match = db_data.query(TczqMatch).filter(TczqMatch.match_id == bet_data.match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # 计算预期奖金
        potential_win = bet_data.amount * bet_data.odds
        
        # 扣除余额
        balance_before = user.balance
        user.balance -= bet_data.amount
        user.total_bet += bet_data.amount
        
        # 创建投注记录
        bet_record = BetRecord(
            user_id=user.id,
            username=user.username,
            match_id=bet_data.match_id,
            match_num_str=match.match_num_str,
            league_name=match.league_name,
            home_team=match.home_team_name,
            away_team=match.away_team_name,
            match_time=match.match_time,
            bet_type=bet_data.bet_type,
            bet_option=bet_data.bet_option,
            odds=bet_data.odds,
            handicap=bet_data.handicap,
            bet_amount=bet_data.amount,
            potential_win=potential_win,
            status='pending'
        )
        db_self.add(bet_record)
        
        # 记录余额变动
        balance_log = UserBalanceLog(
            user_id=user.id,
            change_type='bet',
            amount=-bet_data.amount,
            balance_before=balance_before,
            balance_after=user.balance,
            description=f"投注 {match.match_num_str}",
            related_id=bet_record.id
        )
        db_self.add(balance_log)
        
        db_self.commit()
        
        return ResponseModel(
            code=200,
            message="Bet placed successfully",
            data={
                "bet_id": bet_record.id,
                "potential_win": potential_win,
                "balance": user.balance
            }
        )
    except HTTPException:
        db_self.rollback()
        raise
    except Exception as e:
        db_self.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db_self.close()
        db_data.close()


@router.post("/place/multiple", response_model=ResponseModel)
async def place_multiple_bet(
    bet_data: PlaceMultipleBetRequest,
    current_user: dict = Depends(get_current_user)
):
    """串关下注"""
    db_self = SelfDB()
    db_data = DataDB()
    
    try:
        # 获取用户信息
        user = db_self.query(User).filter(User.username == current_user["username"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 检查余额
        if user.balance < bet_data.total_amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # 生成订单号
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}"
        
        # 计算总赔率
        total_odds = 1.0
        bet_details = []
        
        for bet in bet_data.bets:
            total_odds *= bet['odds']
            bet_details.append(bet)
        
        potential_win = bet_data.total_amount * total_odds
        
        # 扣除余额
        balance_before = user.balance
        user.balance -= bet_data.total_amount
        user.total_bet += bet_data.total_amount
        
        # 创建订单
        import json
        order = BetOrder(
            order_no=order_no,
            user_id=user.id,
            username=user.username,
            bet_type='multiple',
            multiple_count=len(bet_data.bets),
            total_amount=bet_data.total_amount,
            total_odds=total_odds,
            potential_win=potential_win,
            bet_details=json.dumps(bet_details, ensure_ascii=False),
            status='pending'
        )
        db_self.add(order)
        
        # 为每个注项创建投注记录
        for bet in bet_data.bets:
            match = db_data.query(TczqMatch).filter(TczqMatch.match_id == bet['match_id']).first()
            
            bet_record = BetRecord(
                user_id=user.id,
                username=user.username,
                match_id=bet['match_id'],
                match_num_str=match.match_num_str if match else None,
                league_name=match.league_name if match else None,
                home_team=match.home_team_name if match else None,
                away_team=match.away_team_name if match else None,
                match_time=match.match_time if match else None,
                bet_type=bet['bet_type'],
                bet_option=bet['bet_option'],
                odds=bet['odds'],
                handicap=bet.get('handicap'),
                bet_amount=bet_data.total_amount / len(bet_data.bets),  # 平均分配
                potential_win=potential_win / len(bet_data.bets),
                status='pending'
            )
            db_self.add(bet_record)
        
        # 记录余额变动
        balance_log = UserBalanceLog(
            user_id=user.id,
            change_type='bet',
            amount=-bet_data.total_amount,
            balance_before=balance_before,
            balance_after=user.balance,
            description=f"串关投注 {len(bet_data.bets)}场",
            related_id=order.id
        )
        db_self.add(balance_log)
        
        db_self.commit()
        
        return ResponseModel(
            code=200,
            message="Multiple bet placed successfully",
            data={
                "order_no": order_no,
                "total_odds": total_odds,
                "potential_win": potential_win,
                "balance": user.balance
            }
        )
    except HTTPException:
        db_self.rollback()
        raise
    except Exception as e:
        db_self.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db_self.close()
        db_data.close()


@router.get("/records", response_model=ResponseModel)
async def get_bet_records(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """查询投注记录"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = db.query(BetRecord).filter(BetRecord.user_id == user.id)
        
        if status_filter:
            query = query.filter(BetRecord.status == status_filter)
        
        records = query.order_by(BetRecord.created_at.desc()).offset(offset).limit(limit).all()
        
        total = db.query(BetRecord).filter(BetRecord.user_id == user.id).count()
        if status_filter:
            total = db.query(BetRecord).filter(
                BetRecord.user_id == user.id,
                BetRecord.status == status_filter
            ).count()
        
        record_list = []
        for record in records:
            record_list.append({
                "id": record.id,
                "match_id": record.match_id,
                "match_num_str": record.match_num_str,
                "league_name": record.league_name,
                "home_team": record.home_team,
                "away_team": record.away_team,
                "match_time": record.match_time.isoformat() if record.match_time else None,
                "bet_type": record.bet_type,
                "bet_option": record.bet_option,
                "odds": record.odds,
                "handicap": record.handicap,
                "bet_amount": record.bet_amount,
                "potential_win": record.potential_win,
                "actual_win": record.actual_win,
                "status": record.status,
                "result": record.result,
                "created_at": record.created_at.isoformat(),
                "settled_at": record.settled_at.isoformat() if record.settled_at else None,
            })
        
        return ResponseModel(
            code=200,
            message="success",
            data=record_list,
            total=total
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/orders", response_model=ResponseModel)
async def get_bet_orders(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """查询投注订单（串关）"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = db.query(BetOrder).filter(BetOrder.user_id == user.id)
        
        if status_filter:
            query = query.filter(BetOrder.status == status_filter)
        
        orders = query.order_by(BetOrder.created_at.desc()).offset(offset).limit(limit).all()
        
        total = db.query(BetOrder).filter(BetOrder.user_id == user.id).count()
        if status_filter:
            total = db.query(BetOrder).filter(
                BetOrder.user_id == user.id,
                BetOrder.status == status_filter
            ).count()
        
        order_list = []
        for order in orders:
            order_list.append({
                "id": order.id,
                "order_no": order.order_no,
                "bet_type": order.bet_type,
                "multiple_count": order.multiple_count,
                "total_amount": order.total_amount,
                "total_odds": order.total_odds,
                "potential_win": order.potential_win,
                "actual_win": order.actual_win,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "settled_at": order.settled_at.isoformat() if order.settled_at else None,
            })
        
        return ResponseModel(
            code=200,
            message="success",
            data=order_list,
            total=total
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
