CREATE TABLE IF NOT EXISTS `t_candlesticks` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `stock_code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `period` VARCHAR(10) NOT NULL COMMENT '周期',
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


