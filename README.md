# 长桥证券价格行为监测

## 项目简介

本项目基于长桥证券 API 实现数据采集、量化回测，主要用于记录和分析股票市场的实时数据。

```shell
TradingCandlestick/
├── config/                # 全局重要的配置
├── data_fetcher/          # 数据收集模块
├── db/                    # 数据收集模块， 数据获取模块
├── notifications/         # 邮件通知模块
├── order/                 # 订单管理模块
├── patterns/              # 价格行为模式识别模块
├── quant_analyzer/        # 回撤分析模块
├── scripts/               # 数据库初始化脚本文件，Docker run脚本文件
├── utils/                 # 常用工具
└── main.py                # 入口文件
```

## 主要功能

基本面分析师
情绪分析师
技术分析师
风险管理团队