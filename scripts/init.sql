CREATE TABLE IF NOT EXISTS `t_quotes` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `stock_code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `last_done` DECIMAL(10, 3) NOT NULL COMMENT '最新价格',
    `open` DECIMAL(10, 3) NOT NULL COMMENT '开盘价',
    `high` DECIMAL(10, 3) NOT NULL COMMENT '最高价',
    `low` DECIMAL(10, 3) NOT NULL COMMENT '最低价',
    `volume` BIGINT NOT NULL COMMENT '成交量',
    `turnover` DECIMAL(20, 3) NOT NULL COMMENT '成交额',
    `trade_status` VARCHAR(20) NOT NULL COMMENT '交易状态',
    `current_volume` BIGINT NOT NULL COMMENT '当前成交量',
    `current_turnover` DECIMAL(20, 3) NOT NULL COMMENT '当前成交额',
    `timestamp` DATETIME NOT NULL COMMENT '最新价格时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_stock_code` (`stock_code`),
    KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实时行情表';


CREATE TABLE IF NOT EXISTS `t_candlesticks` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `stock_code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `period` VARCHAR(32) NOT NULL COMMENT '周期',
    `is_confirmed` BOOLEAN NOT NULL COMMENT '是否确认',
    `open` DECIMAL(10, 3) NOT NULL COMMENT '开盘价',
    `high` DECIMAL(10, 3) NOT NULL COMMENT '最高价',
    `low` DECIMAL(10, 3) NOT NULL COMMENT '最低价',
    `close` DECIMAL(10, 3) NOT NULL COMMENT '收盘价',
    `volume` BIGINT NOT NULL COMMENT '成交量',
    `turnover` DECIMAL(20, 3) NOT NULL COMMENT '成交额',
    `timestamp` DATETIME NOT NULL COMMENT '最新价格时间',
    PRIMARY KEY (`id`),
    KEY `idx_stock_code` (`stock_code`),
    KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='K线表';


