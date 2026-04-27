# -*- coding: utf-8 -*-
"""
北京单场数据查询路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from database.db_core import DataDB
from database.data_models.bjdc_models import BjdcMatch, BjdcSpfOdds, BjdcHandicapSpfOdds, BjdcTotalGoalOdds, BjdcScoreOdds, BjdcHalfTimeFullTimeOdds, BjdcUpDownOdds, BjdcMatchResult
from core.models import (
    BjdcMatchResponse, SpfOddsResponse, HandicapSpfOddsResponse,
    TotalGoalOddsResponse, MatchResultResponse, ResponseModel
)
from core.deps import get_current_user

router = APIRouter(prefix="/bjdc", tags=["北京单场"])


@router.get("/matches", response_model=ResponseModel)
async def get_matches(
    issue: Optional[str] = Query(None, description="期数"),
    match_week: Optional[str] = Query(None, description="星期"),
    status: Optional[int] = Query(None, description="状态"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: dict = Depends(get_current_user)
):
    """查询北京单场比赛列表"""
    db = DataDB()
    try:
        query = db.query(BjdcMatch)
        
        if issue:
            query = query.filter(BjdcMatch.issue == issue)
        if match_week:
            query = query.filter(BjdcMatch.match_week == match_week)
        if status is not None:
            query = query.filter(BjdcMatch.status == status)
        
        matches = query.order_by(BjdcMatch.match_time.desc()).offset(offset).limit(limit).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=[BjdcMatchResponse.from_orm(m) for m in matches]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/match/{match_id}", response_model=ResponseModel)
async def get_match_detail(match_id: int, current_user: dict = Depends(get_current_user)):
    """查询单场比赛详情（包含赔率）"""
    db = DataDB()
    try:
        match = db.query(BjdcMatch).filter(BjdcMatch.match_id == match_id).first()
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        spf = db.query(BjdcSpfOdds).filter(BjdcSpfOdds.match_id == match_id).first()
        hh_spf = db.query(BjdcHandicapSpfOdds).filter(BjdcHandicapSpfOdds.match_id == match_id).first()
        total_goal = db.query(BjdcTotalGoalOdds).filter(BjdcTotalGoalOdds.match_id == match_id).first()
        score = db.query(BjdcScoreOdds).filter(BjdcScoreOdds.match_id == match_id).first()
        ht_ft = db.query(BjdcHalfTimeFullTimeOdds).filter(BjdcHalfTimeFullTimeOdds.match_id == match_id).first()
        up_down = db.query(BjdcUpDownOdds).filter(BjdcUpDownOdds.match_id == match_id).first()
        result = db.query(BjdcMatchResult).filter(BjdcMatchResult.match_id == match_id).first()
        
        return ResponseModel(
            code=200,
            message="success",
            data={
                "match": BjdcMatchResponse.from_orm(match),
                "spf": SpfOddsResponse.from_orm(spf) if spf else None,
                "handicap_spf": HandicapSpfOddsResponse.from_orm(hh_spf) if hh_spf else None,
                "total_goal": TotalGoalOddsResponse.from_orm(total_goal) if total_goal else None,
                "result": MatchResultResponse.from_orm(result) if result else None,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/results", response_model=ResponseModel)
async def get_results(
    issue: Optional[str] = Query(None, description="期数"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    current_user: dict = Depends(get_current_user)
):
    """查询比赛结果"""
    db = DataDB()
    try:
        query = db.query(BjdcMatchResult)
        
        if issue:
            matches = db.query(BjdcMatch).filter(BjdcMatch.issue == issue).all()
            match_ids = [m.match_id for m in matches]
            query = query.filter(BjdcMatchResult.match_id.in_(match_ids))
        
        results = query.order_by(BjdcMatchResult.id.desc()).limit(limit).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=[MatchResultResponse.from_orm(r) for r in results]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
