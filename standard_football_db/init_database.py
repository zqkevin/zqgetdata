"""
标准足球数据库 - 数据库初始化和数据导入工具
使用本地 soccer_team_db 数据库
"""
import json
import mysql.connector
from pathlib import Path
from typing import List, Dict, Any

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'soccer_team_db',
    'password': '123456',
    'database': 'soccer_team_db',
    'charset': 'utf8mb4'
}

DATA_DIR = Path(__file__).parent / "data"


def get_connection():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)


def create_tables():
    """创建所有表"""
    print("=" * 80)
    print("📊 创建数据库表")
    print("=" * 80)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 禁用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 删除所有sf_开头的表（如果存在）
        print("\n🗑️  清理旧表...")
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME LIKE 'sf_%'
        """, (DB_CONFIG['database'],))
        old_tables = cursor.fetchall()
        
        for table in old_tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            print(f"   删除: {table_name}")
        
        print("✅ 清理完成\n")
        
        # 1. areas表
        print("\n✅ 创建 sf_areas 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_areas` (
                `id` INT PRIMARY KEY COMMENT '区域ID',
                `name_en` VARCHAR(100) NOT NULL COMMENT '英文名称',
                `name_zh` VARCHAR(100) COMMENT '中文名称',
                `code` VARCHAR(10) COMMENT '国家代码',
                `flag_url` TEXT COMMENT '国旗URL',
                `parent_area_id` INT COMMENT '父区域ID',
                `area_type` ENUM('WORLD','CONTINENT','COUNTRY','REGION') DEFAULT 'COUNTRY' COMMENT '区域类型',
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (`parent_area_id`) REFERENCES `sf_areas`(`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='国家/地区表'
        """)
        cursor.execute("CREATE INDEX `idx_areas_parent` ON `sf_areas`(`parent_area_id`)")
        cursor.execute("CREATE INDEX `idx_areas_code` ON `sf_areas`(`code`)")
        
        # 2. positions表
        print("✅ 创建 sf_positions 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_positions` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `code` VARCHAR(10) NOT NULL UNIQUE,
                `name_en` VARCHAR(50) NOT NULL,
                `name_zh` VARCHAR(50),
                `category` ENUM('GOALKEEPER','DEFENDER','MIDFIELDER','FORWARD') NOT NULL,
                `sort_order` INT DEFAULT 0,
                UNIQUE KEY `uk_code` (`code`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='位置字典表'
        """)
        
        # 插入位置数据
        positions = [
            ('GK', 'Goalkeeper', '守门员', 'GOALKEEPER', 1),
            ('CB', 'Centre-Back', '中后卫', 'DEFENDER', 2),
            ('LB', 'Left-Back', '左后卫', 'DEFENDER', 3),
            ('RB', 'Right-Back', '右后卫', 'DEFENDER', 4),
            ('CDM', 'Defensive Midfield', '防守型中场', 'MIDFIELDER', 5),
            ('CM', 'Central Midfield', '中场', 'MIDFIELDER', 6),
            ('CAM', 'Attacking Midfield', '攻击型中场', 'MIDFIELDER', 7),
            ('LM', 'Left Midfield', '左中场', 'MIDFIELDER', 8),
            ('RM', 'Right Midfield', '右中场', 'MIDFIELDER', 9),
            ('LW', 'Left Winger', '左边锋', 'FORWARD', 10),
            ('RW', 'Right Winger', '右边锋', 'FORWARD', 11),
            ('CF', 'Centre-Forward', '中锋', 'FORWARD', 12),
            ('ST', 'Striker', '前锋', 'FORWARD', 13),
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO `sf_positions` (`code`, `name_en`, `name_zh`, `category`, `sort_order`)
            VALUES (%s, %s, %s, %s, %s)
        """, positions)
        
        # 3. venues表
        print("✅ 创建 sf_venues 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_venues` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `name` VARCHAR(200) NOT NULL,
                `name_zh` VARCHAR(200),
                `city` VARCHAR(100),
                `country` VARCHAR(100),
                `address` TEXT,
                `capacity` INT,
                `surface` VARCHAR(50),
                `image_url` TEXT,
                `latitude` DECIMAL(10, 8),
                `longitude` DECIMAL(11, 8),
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='球场表'
        """)
        
        # 4. leagues表
        print("✅ 创建 sf_leagues 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_leagues` (
                `id` INT PRIMARY KEY,
                `name_en_full` VARCHAR(200) NOT NULL,
                `name_en_short` VARCHAR(100),
                `name_zh_full` VARCHAR(200),
                `name_zh_short` VARCHAR(100),
                `code` VARCHAR(20),
                `type` ENUM('LEAGUE','CUP','SUPER_CUP','OTHER') DEFAULT 'LEAGUE',
                `emblem_url` TEXT,
                `logo_url` TEXT,
                `area_id` INT NOT NULL,
                `current_season_start` DATE,
                `current_season_end` DATE,
                `current_matchday` INT,
                `source_platform` ENUM('FOOTBALL_DATA','API_FOOTBALL','THESPORTSDB') DEFAULT 'THESPORTSDB',
                `source_id` VARCHAR(50),
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (`area_id`) REFERENCES `sf_areas`(`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='联赛表'
        """)
        cursor.execute("CREATE INDEX `idx_leagues_area` ON `sf_leagues`(`area_id`)")
        cursor.execute("CREATE INDEX `idx_leagues_code` ON `sf_leagues`(`code`)")
        
        # 5. teams表
        print("✅ 创建 sf_teams 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_teams` (
                `id` INT PRIMARY KEY,
                `name_en_full` VARCHAR(200) NOT NULL,
                `name_en_short` VARCHAR(100),
                `name_zh_full` VARCHAR(200),
                `name_zh_short` VARCHAR(100),
                `short_code` VARCHAR(10),
                `tla` VARCHAR(10),
                `founded_year` INT,
                `club_colors` VARCHAR(100),
                `website` VARCHAR(500),
                `facebook_url` VARCHAR(500),
                `twitter_url` VARCHAR(500),
                `instagram_url` VARCHAR(500),
                `youtube_url` VARCHAR(500),
                `crest_url` TEXT,
                `badge_url` TEXT,
                `logo_url` TEXT,
                `banner_url` TEXT,
                `equipment_url` TEXT,
                `fanart1_url` TEXT,
                `fanart2_url` TEXT,
                `fanart3_url` TEXT,
                `fanart4_url` TEXT,
                `area_id` INT,
                `venue_id` INT,
                `api_football_id` VARCHAR(50),
                `espn_id` VARCHAR(50),
                `thesportsdb_id` VARCHAR(50),
                `source_platform` ENUM('FOOTBALL_DATA','API_FOOTBALL','THESPORTSDB') DEFAULT 'THESPORTSDB',
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (`area_id`) REFERENCES `sf_areas`(`id`),
                FOREIGN KEY (`venue_id`) REFERENCES `sf_venues`(`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='球队表'
        """)
        cursor.execute("CREATE INDEX `idx_teams_area` ON `sf_teams`(`area_id`)")
        cursor.execute("CREATE INDEX `idx_teams_name_en` ON `sf_teams`(`name_en_full`)")
        cursor.execute("CREATE INDEX `idx_teams_name_zh` ON `sf_teams`(`name_zh_full`)")
        
        # 6. players表
        print("✅ 创建 sf_players 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_players` (
                `id` INT PRIMARY KEY,
                `name_en_full` VARCHAR(200) NOT NULL,
                `first_name_en` VARCHAR(100),
                `last_name_en` VARCHAR(100),
                `name_zh_full` VARCHAR(200),
                `first_name_zh` VARCHAR(100),
                `last_name_zh` VARCHAR(100),
                `date_of_birth` DATE COMMENT '出生日期',
                `age` INT COMMENT '年龄（应用层计算）',
                `nationality` VARCHAR(100),
                `nationality_area_id` INT,
                `position_id` INT,
                `position_detail` VARCHAR(50),
                `height_cm` INT,
                `weight_kg` INT,
                `preferred_foot` ENUM('LEFT','RIGHT','BOTH'),
                `shirt_number` INT,
                `photo_url` TEXT,
                `api_football_id` VARCHAR(50),
                `thesportsdb_id` VARCHAR(50),
                `source_platform` ENUM('FOOTBALL_DATA','API_FOOTBALL','THESPORTSDB') DEFAULT 'THESPORTSDB',
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (`nationality_area_id`) REFERENCES `sf_areas`(`id`),
                FOREIGN KEY (`position_id`) REFERENCES `sf_positions`(`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='球员表'
        """)
        cursor.execute("CREATE INDEX `idx_players_nationality` ON `sf_players`(`nationality_area_id`)")
        cursor.execute("CREATE INDEX `idx_players_position` ON `sf_players`(`position_id`)")
        
        # 7. player_teams表
        print("✅ 创建 sf_player_teams 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_player_teams` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `player_id` INT NOT NULL,
                `team_id` INT NOT NULL,
                `shirt_number` INT,
                `join_date` DATE,
                `leave_date` DATE,
                `is_current` BOOLEAN DEFAULT TRUE,
                `contract_until` DATE,
                `market_value_eur` INT,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (`player_id`) REFERENCES `sf_players`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`team_id`) REFERENCES `sf_teams`(`id`) ON DELETE CASCADE,
                UNIQUE KEY `uk_player_team_current` (`player_id`, `team_id`, `is_current`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='球员-球队关联表'
        """)
        
        # 8. coaches表
        print("✅ 创建 sf_coaches 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_coaches` (
                `id` INT PRIMARY KEY,
                `name_en` VARCHAR(200) NOT NULL,
                `name_zh` VARCHAR(200),
                `date_of_birth` DATE,
                `nationality` VARCHAR(100),
                `nationality_area_id` INT,
                `photo_url` TEXT,
                `api_football_id` VARCHAR(50),
                `thesportsdb_id` VARCHAR(50),
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (`nationality_area_id`) REFERENCES `sf_areas`(`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教练表'
        """)
        
        # 9. team_coaches表
        print("✅ 创建 sf_team_coaches 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_team_coaches` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `team_id` INT NOT NULL,
                `coach_id` INT NOT NULL,
                `start_date` DATE,
                `end_date` DATE,
                `is_current` BOOLEAN DEFAULT TRUE,
                `role` VARCHAR(50) DEFAULT 'HEAD_COACH',
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (`team_id`) REFERENCES `sf_teams`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`coach_id`) REFERENCES `sf_coaches`(`id`) ON DELETE CASCADE,
                UNIQUE KEY `uk_team_coach_current` (`team_id`, `coach_id`, `is_current`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='球队-教练关联表'
        """)
        
        # 10. team_leagues表
        print("✅ 创建 sf_team_leagues 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_team_leagues` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `team_id` INT NOT NULL,
                `league_id` INT NOT NULL,
                `season_year` INT,
                `is_primary` BOOLEAN DEFAULT FALSE,
                `joined_date` DATE,
                `left_date` DATE,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (`team_id`) REFERENCES `sf_teams`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`league_id`) REFERENCES `sf_leagues`(`id`) ON DELETE CASCADE,
                UNIQUE KEY `uk_team_league_season` (`team_id`, `league_id`, `season_year`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='球队-联赛关联表'
        """)
        
        # 11. translations表
        print("✅ 创建 sf_translations 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `sf_translations` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `source_text` VARCHAR(500) NOT NULL,
                `translated_text` VARCHAR(500) NOT NULL,
                `from_lang` CHAR(2) DEFAULT 'en',
                `to_lang` CHAR(2) DEFAULT 'zh',
                `context` VARCHAR(50),
                `md5_hash` CHAR(32) NOT NULL UNIQUE,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_md5` (`md5_hash`),
                INDEX `idx_context` (`context`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='翻译缓存表'
        """)
        
        # 启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.commit()
        print("\n✅ 所有表创建成功！")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 创建表失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def verify_tables():
    """验证表结构"""
    print("\n" + "=" * 80)
    print("🔍 验证表结构")
    print("=" * 80)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SHOW TABLES LIKE 'sf_%'")
        tables = cursor.fetchall()
        
        print(f"\n✅ 已创建的表 ({len(tables)}个):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            count = cursor.fetchone()[0]
            print(f"   • {table_name}: {count} 条记录")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print("=" * 80)
    print("  🚀 标准足球数据库 - 初始化")
    print("=" * 80)
    print(f"\n📊 数据库: {DB_CONFIG['database']}")
    print(f"👤 用户: {DB_CONFIG['user']}")
    print(f"🌐 主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    # 创建表
    create_tables()
    
    # 验证
    verify_tables()
    
    print("\n" + "=" * 80)
    print("  ✅ 数据库初始化完成")
    print("=" * 80)
