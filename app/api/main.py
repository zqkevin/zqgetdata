# -*- coding: utf-8 -*-
"""
体育数据API接口
基于FastAPI框架开发
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from pydantic import BaseModel
import datetime

from app.database import localdb, TczqMatch, TcbkMatch, DigitalLotteryDraw

# 创建FastAPI应用实例
app = FastAPI(
    title="体育数据API",
    description="提供足球、篮球和数字彩票数据的API接口",
    version="1.0.0"
)

# API密钥配置
API_KEY = "your_api_key_here"  # 实际部署时应从配置文件读取
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# 依赖项：验证API密钥
def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    验证API密钥
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    return api_key

# 响应模型
class FootballMatch(BaseModel):
    match_id: str
    league_id: int
    league_name: str
    home_team: str
    away_team: str
    match_time: datetime.datetime
    status: str
    home_score: int = None
    away_score: int = None

class BasketballMatch(BaseModel):
    match_id: str
    league_id: int
    league_name: str
    home_team: str
    away_team: str
    match_time: datetime.datetime
    status: str
    home_score: int = None
    away_score: int = None

class DigitalLottery(BaseModel):
    lottery_id: str
    draw_date: datetime.date
    draw_number: str
    red_balls: list
    blue_ball: str
    sales_amount: float
    prize_pool_amount: float

# 通用响应模型
class ResponseModel(BaseModel):
    code: int
    data: list
    msg: str

# API路由
@app.get("/api/v1/football/match", dependencies=[Depends(verify_api_key)])
async def get_football_matches(
    league_id: int = None,
    date: str = None,
    page: int = 1,
    size: int = 10
) -> ResponseModel:
    """
    获取足球比赛列表
    """
    try:
        query = localdb.query(TczqMatch)
        
        # 筛选条件
        if league_id:
            query = query.filter(TczqMatch.league_id == league_id)
        
        if date:
            query_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(TczqMatch.match_time >= query_date)
            query = query.filter(TczqMatch.match_time < query_date + datetime.timedelta(days=1))
        
        # 分页
        total = query.count()
        offset = (page - 1) * size
        matches = query.offset(offset).limit(size).all()
        
        # 转换为响应模型
        data = []
        for match in matches:
            data.append({
                "match_id": match.match_id,
                "league_id": match.league_id,
                "league_name": match.league_name,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "match_time": match.match_time,
                "status": match.status,
                "home_score": match.home_score,
                "away_score": match.away_score
            })
        
        return ResponseModel(code=200, data=data, msg="success")
        
    except Exception as e:
        return ResponseModel(code=500, data=[], msg=str(e))

@app.get("/api/v1/basketball/match", dependencies=[Depends(verify_api_key)])
async def get_basketball_matches(
    league_id: int = None,
    date: str = None,
    page: int = 1,
    size: int = 10
) -> ResponseModel:
    """
    获取篮球比赛列表
    """
    try:
        query = localdb.query(TcbkMatch)
        
        # 筛选条件
        if league_id:
            query = query.filter(TcbkMatch.league_id == league_id)
        
        if date:
            query_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(TcbkMatch.match_time >= query_date)
            query = query.filter(TcbkMatch.match_time < query_date + datetime.timedelta(days=1))
        
        # 分页
        total = query.count()
        offset = (page - 1) * size
        matches = query.offset(offset).limit(size).all()
        
        # 转换为响应模型
        data = []
        for match in matches:
            data.append({
                "match_id": match.match_id,
                "league_id": match.league_id,
                "league_name": match.league_name,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "match_time": match.match_time,
                "status": match.status,
                "home_score": match.home_score,
                "away_score": match.away_score
            })
        
        return ResponseModel(code=200, data=data, msg="success")
        
    except Exception as e:
        return ResponseModel(code=500, data=[], msg=str(e))

@app.get("/api/v1/lottery/digital", dependencies=[Depends(verify_api_key)])
async def get_digital_lottery(
    lottery_id: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    size: int = 10
) -> ResponseModel:
    """
    获取数字彩票开奖结果
    """
    try:
        query = localdb.query(DigitalLotteryDraw)
        
        # 筛选条件
        if lottery_id:
            query = query.filter(DigitalLotteryDraw.lottery_code == lottery_id)
        
        if start_date:
            start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(DigitalLotteryDraw.draw_time >= start)
        
        if end_date:
            end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(DigitalLotteryDraw.draw_time <= end)
        
        # 按日期倒序排序
        query = query.order_by(DigitalLotteryDraw.draw_time.desc())
        
        # 分页
        total = query.count()
        offset = (page - 1) * size
        results = query.offset(offset).limit(size).all()
        
        # 转换为响应模型
        data = []
        for result in results:
            data.append({
                "lottery_id": result.lottery_id,
                "draw_date": result.draw_date,
                "draw_number": result.draw_number,
                "red_balls": result.red_balls,
                "blue_ball": result.blue_ball,
                "sales_amount": result.sales_amount,
                "prize_pool_amount": result.prize_pool_amount
            })
        
        return ResponseModel(code=200, data=data, msg="success")
        
    except Exception as e:
        return ResponseModel(code=500, data=[], msg=str(e))

@app.get("/api/v1/lottery/result", dependencies=[Depends(verify_api_key)])
async def get_lottery_result(
    lottery_id: str,
    draw_number: str = None,
    draw_date: str = None
) -> ResponseModel:
    """
    获取指定彩票的最新开奖结果
    """
    try:
        query = localdb.query(DigitalLotteryDraw)
        query = query.filter(DigitalLotteryDraw.lottery_code == lottery_id)
        
        # 筛选条件
        if draw_number:
            query = query.filter(DigitalLotteryDraw.draw_num == draw_number)
        
        if draw_date:
            draw_date_obj = datetime.datetime.strptime(draw_date, "%Y-%m-%d").date()
            query = query.filter(DigitalLotteryDraw.draw_time >= draw_date_obj)
            query = query.filter(DigitalLotteryDraw.draw_time < draw_date_obj + datetime.timedelta(days=1))
        
        # 按日期倒序排序，取最新结果
        query = query.order_by(DigitalLotteryDraw.draw_time.desc(), DigitalLotteryDraw.draw_num.desc())
        result = query.first()
        
        if not result:
            return ResponseModel(code=404, data=[], msg="未找到开奖结果")
        
        # 转换为响应模型
        data = [{
            "lottery_id": result.lottery_id,
            "draw_date": result.draw_date,
            "draw_number": result.draw_number,
            "red_balls": result.red_balls,
            "blue_ball": result.blue_ball,
            "sales_amount": result.sales_amount,
            "prize_pool_amount": result.prize_pool_amount
        }]
        
        return ResponseModel(code=200, data=data, msg="success")
        
    except Exception as e:
        return ResponseModel(code=500, data=[], msg=str(e))

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.now()}

# 启动命令
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)