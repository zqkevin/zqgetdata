# -*- coding: utf-8 -*-
"""
认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from core.security import create_access_token, verify_password, get_password_hash
from core.models import Token, UserLogin, UserCreate
from config import settings
from database.db_core import SelfDB
from database.server_models.user_models import User

router = APIRouter(prefix="/auth", tags=["认证"])


def get_or_create_default_admin():
    """获取或创建默认管理员用户"""
    db = SelfDB()
    try:
        # 查询是否已有 admin 用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            # 创建默认管理员
            hashed_password = get_password_hash("admin123")
            new_admin = User(
                username="admin",
                hashed_password=hashed_password,
                is_active=True,
                is_admin=True,
                remark="默认管理员账户"
            )
            db.add(new_admin)
            print("✅ 已创建默认管理员账户: admin / admin123")
        
        return True
    except Exception as e:
        print(f"⚠️ 创建管理员账户失败: {e}")
        return False
    finally:
        db.close()


# 启动时创建默认管理员
get_or_create_default_admin()


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """用户登录获取令牌"""
    db = SelfDB()
    try:
        user = db.query(User).filter(User.username == user_data.username).first()
        
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/register")
async def register(user_data: UserCreate):
    """用户注册"""
    db = SelfDB()
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )
        db.add(new_user)
        
        return {"message": "User created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
