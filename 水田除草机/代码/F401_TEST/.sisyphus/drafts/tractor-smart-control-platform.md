# Draft: Tractor Smart Control Platform

## Requirements (confirmed)
- Build a practical guide to deliver a runnable tractor intelligent control platform.
- Team size is one engineer; strong AI-assisted development preference.
- Need a conservative, demo-first outcome in about 1 month for leadership review.
- Short-term: touch panel (OSD-like) control for tractor functions.
- Mid-term: multi-scenario panel control and node coordination over CAN (and possibly ETH).
- Long-term: evaluate big-brain/small-brain architecture (Linux high-performance brain + MCU real-time brain).
- Current hardware includes STM32 board, IMU over UART, quadrature encoder, keys, OLED (I2C), EC11 knob, PS2 controller, 433 receiver, PWM motor outputs, TB6612, ToF (I2C), CAN controller, spare UARTs.
- Candidate use cases:
  - Paddy weeding mini robot (float platform, dual-motor propulsion, obstacle handling).
  - Retrofit diesel tractor for auto rotary tiller lift/balance (gyro + depth sensor to valve outputs).
  - Electric crawler platform (300kg), PWM/PPM control with HOTRC radio.
- 用户偏好：后续沟通与交付说明统一使用中文。

## Technical Decisions
- Requested approach: most conservative runnable path first; production compliance is not a phase-1 priority.
- Requested output: detailed step-by-step practice guide plus technical debt labeling.
- Phase-1 锚点场景已确认：电动履带平台（1个月演示主线）。
- 交流与后续交付语言：中文（用户再次明确要求“永远用中文回答”）。
- HMI 决策：首月直接上触摸屏，不采用 OLED+EC11 过渡。
- 首月演示验收线：标准版（触摸中控 + CAN 联动 + 安全兜底 + 日志回放）。
- 调度策略：首月采用“最小 RTOS 分层”落地（控制/通信/传感/UI），不做复杂中间件。

## Research Findings
- Workspace appears to be STM32F401 firmware project with existing app modules and historical planning docs.
- Existing code artifacts suggest already-integrated modules: motor/control task, gyro, ToF, encoder, PS2, and app main flow.

### 代码现状（explore）
- 现有工程已形成 `1_Task -> 2_Control -> 3_Driver` 三层结构，可复用度较高。
- 已具备：电机驱动（TB6612）、编码器、IMU、ToF、PS2、OLED/LVGL、舵机 PWM 等基础能力。
- 关键缺口：
  - 缺少可用于多节点联调的 CAN 应用层驱动与协议层。
  - 缺少触摸屏输入驱动（当前主要是 EC11/OLED 交互，不是触控面板）。
  - FreeRTOS 模板存在但未真正接管主循环调度。

### 历史文档结论（explore）
- 已有多份文档沉淀（菜单系统、PID、电机驱动、I2C/TOF 修复、代码审计）。
- 反复出现的问题集中在：I2C 配置细节、TOF 初始化/标定链路、菜单模块耦合偏高、类型与命名一致性。
- 建议保留的约定：三层目录组织、驱动单一职责、参数约束与 AI 协作规则。

### 外部最佳实践（librarian + oracle）
- 大小脑路线建议采用“Linux 负责规划/感知，MCU 负责实时执行与安全兜底”的职责分割。
- 中长期链路建议：控制闭环走 CAN（或 CAN-FD），大带宽感知/日志逐步引入以太网。
- 一人一月演示优先级排序：
  1) 电动履带平台（成功率最高，闭环最可控）
  2) 柴油机改装（集成风险较高）
  3) 水田除草机器人（环境与机械不确定性最高）

### 近期实施建议（librarian）
- 最小 RTOS 分工建议（保守版 4 任务）：
  - ControlTask（高优先级，执行/安全控制）
  - CANTask（中高优先级，收发与路由）
  - SensorTask（中优先级，传感采集）
  - UITask（低优先级，显示与交互）
- CAN 建议采用“低 ID 高优先级”的分区：安全 > 控制 > 状态 > 诊断。
- 必做安全兜底：任务级看门狗签到、心跳超时停机、硬件急停直通断使能。
- 一个月推进顺序：先硬件与环路通，再上 RTOS，再上 CAN 节点，再做联调演示。

### 代码侧快速核对（grep）
- 工程内已有关于电机/CAN 的规范文档与占位说明，但缺少完整 CAN 业务驱动落地痕迹。
- `gyro_collision.c` 中存在“用户钩子用于发 CAN/断油电”等注释，说明接口预留但仍需系统化实现。

### 测试基础设施评估（explore）
- 结论：项目级自动化测试基础设施基本为“无”。
- 现状：
  - 工程主线是 Keil/CubeMX；未看到面向项目代码的单元测试框架接入。
  - 目录中有 `test.c`/`i2c_test.c` 等硬件手工测试例程，但不是自动化单测。
  - LVGL 子目录内有 Unity/CTest 测试样例，但属于第三方库自身，不覆盖本项目业务代码。
- 规划含义：若选择 TDD 或“实现后补测”，需先纳入最小测试脚手架搭建任务；若不搭建，则必须靠 Agent 执行型 QA 场景兜底。

## Test Strategy Decision
- **Infrastructure exists**: NO（项目级）
- **Automated tests**: YES（最小脚手架 + 关键模块补测）
- **If setting up**: 倾向沿用 Unity 风格（与仓库内 LVGL 生态一致）
- **Agent-Executed QA**: ALWAYS（无论是否做自动化测试都强制执行）

## Open Questions
- 关键问题已闭环（阶段锚点、测试策略、HMI形态、验收线已确认）。

## Current Recommendation Snapshot
- Phase-1（1个月）保守可跑通方案：以“电动履带平台演示机”作为唯一锚点，先打通控制面板->控制命令->执行机构->状态回传闭环。
- Phase-1 关键技术策略：先做可维护分层与安全兜底，再逐步引入 RTOS/CAN 多节点，不在首月追求量产与合规。
- 必须显式登记的技术债方向：触摸 UI 正式化、CAN 协议治理、RTOS 全面迁移、故障注入测试、大小脑接口版本化。

## Scope Boundaries
- INCLUDE: conservative one-month demo plan, architecture runway for medium/long term, explicit technical debt register.
- EXCLUDE: immediate mass-production readiness, full compliance certification, advanced autonomous driving in phase-1.
