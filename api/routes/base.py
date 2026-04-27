# -*- coding: utf-8 -*-
"""
基础数据查询路由（联赛、球队）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from database.db_core import DataDB
from database.data_models.base_models import League, Team, TeamAlias
from core.models import LeagueResponse, TeamResponse, ResponseModel
from core.deps import get_current_user

router = APIRouter(prefix="/base", tags=["基础数据"])


@router.get("/leagues", response_model=ResponseModel)
async def get_leagues(
    league_name: Optional[str] = Query(None, description="联赛名称（模糊搜索）"),
    region: Optional[str] = Query(None, description="地区"),
    country: Optional[str] = Query(None, description="国家"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    current_user: dict = Depends(get_current_user)
):
    """查询联赛列表"""
    db = DataDB()
    try:
        query = db.query(League)
        
        if league_name:
            query = query.filter(League.league_name.like(f"%{league_name}%"))
        if region:
            query = query.filter(League.region == region)
        if country:
            query = query.filter(League.country == country)
        
        leagues = query.order_by(League.id).limit(limit).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=[LeagueResponse.from_orm(l) for l in leagues]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/teams", response_model=ResponseModel)
async def get_teams(
    team_name: Optional[str] = Query(None, description="球队名称（模糊搜索）"),
    team_code: Optional[str] = Query(None, description="球队代码"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    current_user: dict = Depends(get_current_user)
):
    """查询球队列表"""
    db = DataDB()
    try:
        query = db.query(Team)
        
        if team_name:
            query = query.filter(
                (Team.team_full_name.like(f"%{team_name}%")) |
                (Team.team_short_name.like(f"%{team_name}%"))
            )
        if team_code:
            query = query.filter(Team.team_code == team_code)
        
        teams = query.order_by(Team.id).limit(limit).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=[TeamResponse.from_orm(t) for t in teams]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/team/{team_id}/aliases", response_model=ResponseModel)
async def get_team_aliases(team_id: int, current_user: dict = Depends(get_current_user)):
    """查询球队别名"""
    db = DataDB()
    try:
        team = db.query(Team).filter(Team.team_id == team_id).first()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        aliases = db.query(TeamAlias).filter(TeamAlias.team_id == team.id).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data={
                "team": TeamResponse.from_orm(team),
                "aliases": [{"id": a.id, "alias_name": a.alias_name, "source_type": a.source_type} for a in aliases]
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
