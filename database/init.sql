-- 运动健康系统数据库初始化脚本

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS bs_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE bs_system;

-- 创建用户（如果不存在）并授权
-- MySQL 8.0+ 语法
CREATE USER IF NOT EXISTS 'bs_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON bs_system.* TO 'bs_user'@'%';
FLUSH PRIVILEGES;

-- 注意：表结构将由SQLAlchemy Migrate自动创建
-- 此文件仅用于参考

