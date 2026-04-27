# -*- coding: utf-8 -*-
"""
收藏/关注路由
提供收藏比赛、联赛、球队，关注专家等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from database.db_core import SelfDB
from database.server_models.favorite_models import UserFavorite, UserFollow
from database.server_models.user_models import User
from core.models import ResponseModel
from core.deps import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/favorite", tags=["收藏/关注"])


class AddFavoriteRequest(BaseModel):
    """添加收藏请求"""
    favorite_type: str = Field(..., description="类型 (match/league/team)")
    target_id: int = Field(..., description="目标ID")
    target_name: Optional[str] = Field(None, description="目标名称")


class AddFollowRequest(BaseModel):
    """添加关注请求"""
    follow_type: str = Field(..., description="类型 (expert/analyst/user)")
    target_id: int = Field(..., description="目标ID")
    target_name: Optional[str] = Field(None, description="目标名称")


@router.post("/add", response_model=ResponseModel)
async def add_favorite(
    data: AddFavoriteRequest,
    current_user: dict = Depends(get_current_user)
):
    """添加收藏"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 检查是否已收藏
        existing = db.query(UserFavorite).filter(
            UserFavorite.user_id == user.id,
            UserFavorite.target_id == data.target_id,
            UserFavorite.favorite_type == data.favorite_type
        ).first()
        
        if existing:
            return ResponseModel(code=200, message="Already favorited")
        
        # 添加收藏
        favorite = UserFavorite(
            user_id=user.id,
            favorite_type=data.favorite_type,
            target_id=data.target_id,
            target_name=data.target_name
        )
        db.add(favorite)
        
        return ResponseModel(code=200, message="Added to favorites successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/remove/{favorite_id}", response_model=ResponseModel)
async def remove_favorite(
    favorite_id: int,
    current_user: dict = Depends(get_current_user)
):
    """取消收藏"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        favorite = db.query(UserFavorite).filter(
            UserFavorite.id == favorite_id,
            UserFavorite.user_id == user.id
        ).first()
        
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        db.delete(favorite)
        db.commit()
        
        return ResponseModel(code=200, message="Removed from favorites successfully")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/list", response_model=ResponseModel)
async def get_favorites(
    favorite_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """获取收藏列表"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = db.query(UserFavorite).filter(UserFavorite.user_id == user.id)
        
        if favorite_type:
            query = query.filter(UserFavorite.favorite_type == favorite_type)
        
        favorites = query.order_by(UserFavorite.created_at.desc()).offset(offset).limit(limit).all()
        
        total = db.query(UserFavorite).filter(UserFavorite.user_id == user.id).count()
        if favorite_type:
            total = db.query(UserFavorite).filter(
                UserFavorite.user_id == user.id,
                UserFavorite.favorite_type == favorite_type
            ).count()
        
        favorite_list = []
        for fav in favorites:
            favorite_list.append({
                "id": fav.id,
                "favorite_type": fav.favorite_type,
                "target_id": fav.target_id,
                "target_name": fav.target_name,
                "created_at": fav.created_at.isoformat(),
            })
        
        return ResponseModel(
            code=200,
            message="success",
            data=favorite_list,
            total=total
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/follow/add", response_model=ResponseModel)
async def add_follow(
    data: AddFollowRequest,
    current_user: dict = Depends(get_current_user)
):
    """添加关注"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 检查是否已关注
        existing = db.query(UserFollow).filter(
            UserFollow.user_id == user.id,
            UserFollow.target_id == data.target_id,
            UserFollow.follow_type == data.follow_type
        ).first()
        
        if existing:
            return ResponseModel(code=200, message="Already following")
        
        # 添加关注
        follow = UserFollow(
            user_id=user.id,
            follow_type=data.follow_type,
            target_id=data.target_id,
            target_name=data.target_name
        )
        db.add(follow)
        
        return ResponseModel(code=200, message="Followed successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/follow/remove/{follow_id}", response_model=ResponseModel)
async def remove_follow(
    follow_id: int,
    current_user: dict = Depends(get_current_user)
):
    """取消关注"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        follow = db.query(UserFollow).filter(
            UserFollow.id == follow_id,
            UserFollow.user_id == user.id
        ).first()
        
        if not follow:
            raise HTTPException(status_code=404, detail="Follow not found")
        
        db.delete(follow)
        db.commit()
        
        return ResponseModel(code=200, message="Unfollowed successfully")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/follow/list", response_model=ResponseModel)
async def get_follows(
    follow_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """获取关注列表"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = db.query(UserFollow).filter(UserFollow.user_id == user.id)
        
        if follow_type:
            query = query.filter(UserFollow.follow_type == follow_type)
        
        follows = query.order_by(UserFollow.created_at.desc()).offset(offset).limit(limit).all()
        
        total = db.query(UserFollow).filter(UserFollow.user_id == user.id).count()
        if follow_type:
            total = db.query(UserFollow).filter(
                UserFollow.user_id == user.id,
                UserFollow.follow_type == follow_type
            ).count()
        
        follow_list = []
        for follow in follows:
            follow_list.append({
                "id": follow.id,
                "follow_type": follow.follow_type,
                "target_id": follow.target_id,
                "target_name": follow.target_name,
                "created_at": follow.created_at.isoformat(),
            })
        
        return ResponseModel(
            code=200,
            message="success",
            data=follow_list,
            total=total
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
