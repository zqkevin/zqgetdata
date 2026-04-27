# -*- coding: utf-8 -*-
"""
用户中心路由
提供个人资料、余额查询、等级信息等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from database.db_core import SelfDB
from database.server_models.user_models import User, UserLevelConfig, UserBalanceLog
from core.models import ResponseModel
from core.deps import get_current_user
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/user", tags=["用户中心"])


class UserProfileUpdate(BaseModel):
    """用户资料更新模型"""
    nickname: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None)
    birthday: Optional[datetime] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    external_link: Optional[str] = Field(None, max_length=500)


@router.get("/profile", response_model=ResponseModel)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """获取当前用户个人资料"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 计算下一级所需经验
        next_level = db.query(UserLevelConfig).filter(
            UserLevelConfig.min_experience > user.experience
        ).order_by(UserLevelConfig.min_experience.asc()).first()
        
        profile_data = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "phone": user.phone,
            "avatar_url": user.avatar_url,
            "gender": user.gender,
            "birthday": user.birthday.isoformat() if user.birthday else None,
            
            # 等级信息
            "level": user.level,
            "level_name": _get_level_name(db, user.level),
            "experience": user.experience,
            "next_level_experience": next_level.min_experience if next_level else None,
            "vip_level": user.vip_level,
            "is_vip": user.is_vip,
            
            # 财务信息
            "balance": user.balance,
            "frozen_balance": user.frozen_balance,
            "total_recharge": user.total_recharge,
            "total_withdraw": user.total_withdraw,
            "total_bet": user.total_bet,
            "total_win": user.total_win,
            
            # 积分
            "points": user.points,
            
            # 其他
            "external_link": user.external_link,
            "remark": user.remark,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat(),
        }
        
        return ResponseModel(code=200, message="success", data=profile_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.put("/profile", response_model=ResponseModel)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新用户个人资料"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 更新字段
        if profile_data.nickname is not None:
            user.nickname = profile_data.nickname
        if profile_data.email is not None:
            user.email = profile_data.email
        if profile_data.phone is not None:
            user.phone = profile_data.phone
        if profile_data.gender is not None:
            user.gender = profile_data.gender
        if profile_data.birthday is not None:
            user.birthday = profile_data.birthday
        if profile_data.avatar_url is not None:
            user.avatar_url = profile_data.avatar_url
        if profile_data.external_link is not None:
            user.external_link = profile_data.external_link
        
        db.commit()
        
        return ResponseModel(code=200, message="Profile updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/balance", response_model=ResponseModel)
async def get_user_balance(current_user: dict = Depends(get_current_user)):
    """获取用户余额信息"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        balance_data = {
            "balance": user.balance,
            "frozen_balance": user.frozen_balance,
            "available_balance": user.balance - user.frozen_balance,
            "total_recharge": user.total_recharge,
            "total_withdraw": user.total_withdraw,
            "total_bet": user.total_bet,
            "total_win": user.total_win,
            "net_profit": user.total_win - user.total_bet,
        }
        
        return ResponseModel(code=200, message="success", data=balance_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/balance/logs", response_model=ResponseModel)
async def get_balance_logs(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """获取余额变动日志"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logs = db.query(UserBalanceLog).filter(
            UserBalanceLog.user_id == user.id
        ).order_by(
            UserBalanceLog.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        total = db.query(UserBalanceLog).filter(
            UserBalanceLog.user_id == user.id
        ).count()
        
        log_list = []
        for log in logs:
            log_list.append({
                "id": log.id,
                "change_type": log.change_type,
                "amount": log.amount,
                "balance_before": log.balance_before,
                "balance_after": log.balance_after,
                "description": log.description,
                "related_id": log.related_id,
                "created_at": log.created_at.isoformat(),
            })
        
        return ResponseModel(
            code=200,
            message="success",
            data=log_list,
            total=total
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/level/info", response_model=ResponseModel)
async def get_level_info(current_user: dict = Depends(get_current_user)):
    """获取用户等级详细信息"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 获取当前等级配置
        current_level_config = db.query(UserLevelConfig).filter(
            UserLevelConfig.level == user.level
        ).first()
        
        # 获取下一级配置
        next_level_config = db.query(UserLevelConfig).filter(
            UserLevelConfig.level == user.level + 1
        ).first()
        
        # 计算升级进度
        if current_level_config and next_level_config:
            progress = (user.experience - current_level_config.min_experience) / \
                      (next_level_config.min_experience - current_level_config.min_experience) * 100
        else:
            progress = 100.0
        
        level_info = {
            "current_level": user.level,
            "level_name": current_level_config.level_name if current_level_config else "未知",
            "icon_url": current_level_config.icon_url if current_level_config else None,
            "benefits": current_level_config.benefits if current_level_config else None,
            "experience": user.experience,
            "min_experience": current_level_config.min_experience if current_level_config else 0,
            "max_experience": next_level_config.min_experience if next_level_config else None,
            "progress": round(progress, 2),
            "next_level": user.level + 1 if next_level_config else None,
            "next_level_name": next_level_config.level_name if next_level_config else "已满级",
            "vip_level": user.vip_level,
            "is_vip": user.is_vip,
        }
        
        return ResponseModel(code=200, message="success", data=level_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/stats", response_model=ResponseModel)
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """获取用户统计数据"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == current_user["username"]).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 这里可以扩展更多统计逻辑
        stats = {
            "user_id": user.id,
            "username": user.username,
            "level": user.level,
            "vip_level": user.vip_level,
            "balance": user.balance,
            "points": user.points,
            "total_bet": user.total_bet,
            "total_win": user.total_win,
            "win_rate": round((user.total_win / user.total_bet * 100) if user.total_bet > 0 else 0, 2),
            "account_age_days": (datetime.now() - user.created_at).days,
        }
        
        return ResponseModel(code=200, message="success", data=stats)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


def _get_level_name(db, level: int) -> str:
    """获取等级名称"""
    config = db.query(UserLevelConfig).filter(UserLevelConfig.level == level).first()
    return config.level_name if config else f"等级{level}"
