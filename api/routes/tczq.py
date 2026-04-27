# -*- coding: utf-8 -*-
"""
体彩足球数据查询路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from database.db_core import DataDB
from database.data_models.tczq_models import TczqMatch, TczqSpfOdds, TczqHandicapSpfOdds, TczqTotalGoalOdds, TczqScoreOdds, TczqHalfTimeFullTimeOdds, TczqMatchResult
from database.data_models.base_models import League, Team
from core.models import (
    TczqMatchResponse, SpfOddsResponse, HandicapSpfOddsResponse,
    TotalGoalOddsResponse, ScoreOddsResponse, MatchResultResponse, ResponseModel
)
from core.deps import get_current_user

router = APIRouter(prefix="/tczq", tags=["体彩足球"])


@router.get("/matches", response_model=ResponseModel)
async def get_matches(
    issue: Optional[str] = Query(None, description="期数"),
    match_week: Optional[str] = Query(None, description="星期"),
    status: Optional[int] = Query(None, description="状态"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: dict = Depends(get_current_user)
):
    """查询体彩足球比赛列表"""
    db = DataDB()
    try:
        query = db.query(TczqMatch)
        
        # 添加过滤条件
        if issue:
            query = query.filter(TczqMatch.issue == issue)
        if match_week:
            query = query.filter(TczqMatch.match_week == match_week)
        if status is not None:
            query = query.filter(TczqMatch.status == status)
        
        # 分页
        matches = query.order_by(TczqMatch.match_time.desc()).offset(offset).limit(limit).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=[TczqMatchResponse.from_orm(m) for m in matches]
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
        # 查询比赛基本信息
        match = db.query(TczqMatch).filter(TczqMatch.match_id == match_id).first()
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # 查询各种赔率
        spf = db.query(TczqSpfOdds).filter(TczqSpfOdds.match_id == match_id).first()
        hh_spf = db.query(TczqHandicapSpfOdds).filter(TczqHandicapSpfOdds.match_id == match_id).first()
        total_goal = db.query(TczqTotalGoalOdds).filter(TczqTotalGoalOdds.match_id == match_id).first()
        score = db.query(TczqScoreOdds).filter(TczqScoreOdds.match_id == match_id).first()
        ht_ft = db.query(TczqHalfTimeFullTimeOdds).filter(TczqHalfTimeFullTimeOdds.match_id == match_id).first()
        result = db.query(TczqMatchResult).filter(TczqMatchResult.match_id == match_id).first()
        
        return ResponseModel(
            code=200,
            message="success",
            data={
                "match": TczqMatchResponse.from_orm(match),
                "spf": SpfOddsResponse.from_orm(spf) if spf else None,
                "handicap_spf": HandicapSpfOddsResponse.from_orm(hh_spf) if hh_spf else None,
                "total_goal": TotalGoalOddsResponse.from_orm(total_goal) if total_goal else None,
                "score": ScoreOddsResponse.from_orm(score) if score else None,
                "result": MatchResultResponse.from_orm(result) if result else None,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/odds/spf", response_model=ResponseModel)
async def get_spf_odds(
    match_id: Optional[int] = Query(None, description="比赛ID"),
    issue: Optional[str] = Query(None, description="期数"),
    current_user: dict = Depends(get_current_user)
):
    """查询胜平负赔率"""
    db = DataDB()
    try:
        query = db.query(TczqSpfOdds)
        
        if match_id:
            query = query.filter(TczqSpfOdds.match_id == match_id)
        elif issue:
            # 通过期数关联查询
            matches = db.query(TczqMatch).filter(TczqMatch.issue == issue).all()
            match_ids = [m.match_id for m in matches]
            query = query.filter(TczqSpfOdds.match_id.in_(match_ids))
        
        odds = query.all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=[SpfOddsResponse.from_orm(o) for o in odds]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/results", response_model=ResponseModel)
async def get_results(
    issue: Optional[str] = Query(None, description="期数"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    current_user: dict = Depends(get_current_user)
):
    """查询比赛结果"""
    db = DataDB()
    try:
        query = db.query(TczqMatchResult)
        
        if issue:
            # 通过期数关联查询
            matches = db.query(TczqMatch).filter(TczqMatch.issue == issue).all()
            match_ids = [m.match_id for m in matches]
            query = query.filter(TczqMatchResult.match_id.in_(match_ids))
        
        results = query.order_by(TczqMatchResult.id.desc()).limit(limit).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=[MatchResultResponse.from_orm(r) for r in results]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
