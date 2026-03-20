# 拖拉机智能控制平台（阶段1）保守可跑通实施计划（电动履带平台）

## TL;DR

> **Quick Summary**: 以电动履带平台为阶段1唯一锚点，在1个月内交付“触摸中控 + CAN联动 + 安全兜底 + 日志回放”的可演示闭环，并保持后续可维护扩展。
>
> **Deliverables**:
> - 触摸中控界面（可下发行驶指令与模式切换）
> - 单主站 CAN 控制与状态回传（含心跳/超时策略）
> - 安全监督（急停、心跳丢失停机、任务存活检查）
> - 日志记录与回放能力（可复现实验过程）
> - 明确技术债清单与阶段2/3接口路线图
>
> **Estimated Effort**: Large（1人1月可控交付）
> **Parallel Execution**: YES - 3 waves + Final Verification Wave
> **Critical Path**: T1 -> T4 -> T7 -> T8 -> T13 -> T14

---

## Context

### Original Request
- 生成拖拉机智能控制平台详细实践指南并带跑通工程。
- 短期做触摸操作面板；中期做多场景与 CAN 节点控制；远期探索大小脑（Linux + MCU）架构。
- 现有硬件以 STM32F401 为核心，已接入多类传感器/执行器与通信外设。
- 团队仅1人，首要目标是1个月内形成可向领导演示的保守可跑通版本。

### Interview Summary
**Key Discussions**:
- 阶段1锚点确定为“电动履带平台”（成功率最高，联调边界最可控）。
- 阶段1验收线确定为“标准版”：触摸中控 + CAN联动 + 安全兜底 + 日志回放。
- HMI 决策：首月直接上触摸屏，不采用 OLED+EC11 作为主演示路径。
- 测试策略：项目先搭建最小测试脚手架，关键模块采用“实现后补测”；不做全量 TDD。
- 输出语言与交付沟通统一中文。

**Research Findings**:
- 现有仓库已具备三层结构与大量可复用驱动（电机、编码器、IMU、ToF、OLED/LVGL、菜单系统）。
- CAN 业务层和触摸输入链路仍是核心缺口；FreeRTOS 样板存在但未完整接管主流程。
- 历史问题高频出现在 I2C/TOF 初始化链路、模块耦合偏高、命名与类型一致性。

### Metis Review
**Identified Gaps（已纳入计划）**:
- 触摸屏协议、断线重连、事件频率、可脚本注入能力需要前置锁定。
- CAN 物理层与应用层边界、总线异常（bus-off）处理必须明确。
- 安全目标需量化（触发条件、进入 STOP 时延、恢复门槛）。
- 日志回放必须定义格式、时间基准与一致性校验，不可仅靠串口打印。
- 需显式防止范围膨胀：阶段1禁止自动驾驶/路径规划/云端/OTA/复杂多节点拓扑。

---

## Work Objectives

### Core Objective
在既有 STM32F401 工程上，构建“可演示、可停机、可复现、可扩展”的阶段1中控闭环平台，确保单人可在1个月内稳定完成演示交付。

### Concrete Deliverables
- `触摸中控`：完成触摸输入到控制命令的全链路。
- `执行闭环`：命令到电机输出、状态回传到 HMI/CAN。
- `安全兜底`：急停、心跳超时停机、任务存活看门狗。
- `可追溯`：日志记录、导出、回放与一致性校验。
- `可持续`：技术债登记与阶段2/3演进路线。

### Definition of Done
- [ ] 固件可稳定运行 >= 30 分钟，无异常复位。
- [ ] 触摸操作可驱动履带平台前进/后退/停止，并在界面显示状态变化。
- [ ] CAN 心跳、控制、状态三类帧可稳定收发，并有超时安全停机。
- [ ] 任一安全触发（心跳丢失/触摸掉线/任务卡死）可在阈值时延内进入 STOP。
- [ ] 可导出一段完整日志并通过回放脚本复现关键状态轨迹。

### Must Have
- 仅面向“电动履带平台”演示，不跨场景并行开发。
- 控制链路与安全链路分离，安全链路拥有最高优先级。
- CAN 协议具备版本标识与最小向后兼容策略（不兼容时安全拒收）。
- 每个任务均含 Agent 执行型 QA 场景（至少 1 个成功 + 1 个失败/异常）。

### Must NOT Have (Guardrails)
- 禁止在阶段1引入自动驾驶、视觉识别、路径规划、云平台、OTA。
- 禁止重构整仓库历史模块；只做最小必要改动与增量封装。
- 禁止“演示效果优先于安全”：任何异常默认进入 STOP。
- 禁止无文档的临时协议字段/魔法常量。

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — 所有验收标准必须由执行代理通过命令或工具直接完成。

### Test Decision
- **Infrastructure exists**: NO（项目级自动化测试基础设施缺失）
- **Automated tests**: Tests-after（先搭最小脚手架，再补关键模块测试）
- **Framework**: Unity 风格最小化接入（优先复用仓内已存在 Unity 生态认知）
- **TDD**: NO（阶段1不强制 RED-GREEN-REFACTOR）

### QA Policy
- 每个任务必须输出证据到 `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`。
- UI/触摸链路：优先通过串口/协议注入脚本 + 日志断言验证，必要时补截图证据。
- CAN 链路：`Bash(candump/cansend 或脚本)` 验证帧、周期、异常恢复。
- RTOS/CLI：`interactive_bash (tmux)` 观察任务心跳、故障注入与退出码。
- 日志回放：通过离线解析脚本对关键字段做数值断言。

---

## Execution Strategy

### Parallel Execution Waves

> 目标是让共享依赖先落地，再让功能模块并行推进。

```text
Wave 1（基础与边界冻结，可立即并行）
├── T1: 平台合同与故障码基线（协议/状态/阈值） [quick]
├── T2: CAN 底层驱动与中断收发骨架 [unspecified-high]
├── T3: 触摸屏驱动适配与 LVGL 输入绑定 [unspecified-high]
├── T4: 最小 FreeRTOS 启动与任务骨架接管 [deep]
└── T5: 安全监督器基础（看门狗签到 + STOP 状态机） [deep]

Wave 2（核心能力并行开发）
├── T6: 触摸中控页面与事件映射 [visual-engineering]
├── T7: 控制命令分发总线（队列/模式机） [deep]
├── T8: 履带执行器适配（PWM/PPM 限速与斜坡） [unspecified-high]
├── T9: CAN 应用协议（心跳/命令/状态/版本） [deep]
├── T10: 传感状态聚合与发布 [unspecified-high]
└── T11: 最小测试脚手架与关键模块补测 [quick]

Wave 3（集成收口与演示化）
├── T12: 日志记录与回放模块 [deep]
├── T13: 故障矩阵联调（触摸掉线/CAN超时/任务卡死） [unspecified-high]
├── T14: 演示脚本与自动证据采集 [quick]
└── T15: 技术债账本与阶段2/3路线图 [writing]

Wave FINAL（并行审计，全部通过才可收尾）
├── F1: 计划符合性审计（oracle）
├── F2: 代码质量与构建审查（unspecified-high）
├── F3: 全量场景执行型 QA（unspecified-high）
└── F4: 范围一致性与越界检查（deep）

Critical Path: T1 -> T4 -> T7 -> T8 -> T13 -> T14
Parallel Speedup: 约 60%-70%
Max Concurrent: 6（Wave 2）
```

### Dependency Matrix (ALL Tasks)
- **T1**: Blocked By `None` -> Blocks `T6,T7,T9,T12,T15`
- **T2**: Blocked By `None` -> Blocks `T9,T10,T13,T14`
- **T3**: Blocked By `None` -> Blocks `T6,T13,T14`
- **T4**: Blocked By `T1` -> Blocks `T7,T8,T10,T11,T13`
- **T5**: Blocked By `T1,T4` -> Blocks `T8,T9,T13,T14`
- **T6**: Blocked By `T1,T3` -> Blocks `T7,T14`
- **T7**: Blocked By `T1,T4,T6` -> Blocks `T8,T9,T12,T13`
- **T8**: Blocked By `T4,T5,T7` -> Blocks `T10,T13,T14`
- **T9**: Blocked By `T1,T2,T5,T7` -> Blocks `T10,T13,T14`
- **T10**: Blocked By `T2,T4,T8,T9` -> Blocks `T12,T14`
- **T11**: Blocked By `T4` -> Blocks `F2`
- **T12**: Blocked By `T1,T7,T10` -> Blocks `T14,T15,F3`
- **T13**: Blocked By `T2,T3,T4,T5,T7,T8,T9` -> Blocks `T14,F3,F4`
- **T14**: Blocked By `T2,T3,T5,T6,T8,T9,T10,T12,T13` -> Blocks `F1,F3`
- **T15**: Blocked By `T1,T12` -> Blocks `F1,F4`

### Agent Dispatch Summary
- **Wave 1**: T1 `quick`, T2 `unspecified-high`, T3 `unspecified-high`, T4 `deep`, T5 `deep`
- **Wave 2**: T6 `visual-engineering`, T7 `deep`, T8 `unspecified-high`, T9 `deep`, T10 `unspecified-high`, T11 `quick`
- **Wave 3**: T12 `deep`, T13 `unspecified-high`, T14 `quick`, T15 `writing`
- **FINAL**: F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [ ] 1. 冻结平台合同与安全阈值基线

  **What to do**:
  - 新增 `App/hsc_Lib/2_Control/platform_contract.h`，定义控制命令、状态、故障码、协议版本、安全状态（OK/DEGRADED/STOP）。
  - 新增 `App/hsc_Lib/2_Control/platform_contract.c`，提供默认阈值（心跳超时、停机时延、限速、日志采样率）。
  - 输出 `docs` 替代物到仓内可执行位置：`App/hsc_Lib/2_Control/platform_contract.md`（字段解释 + 兼容策略）。

  **Must NOT do**:
  - 禁止在此任务实现业务逻辑或硬件读写。
  - 禁止引入自动驾驶相关字段。

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 以结构定义和常量冻结为主，范围清晰且低复杂度。
  - **Skills**: `[]`
    - 无需专项技能，重点是契约一致性。
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: 当前不做界面实现。
    - `playwright`: 当前不涉及浏览器自动化。

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 T2/T3/T5）
  - **Blocks**: T6, T7, T9, T12, T15
  - **Blocked By**: None

  **References**:
  - **Pattern References**:
    - `App/hsc_Lib/2_Control/menu.h` - 复用现有状态/菜单枚举命名风格，避免新旧接口风格冲突。
    - `App/hsc_Lib/2_Control/PID_simple.h` - 参考简洁头文件组织方式（参数 + API）。
  - **API/Type References**:
    - `App/hsc_Lib/1_Task/car_task.h` - 对齐现有控制层对外暴露方式。
    - `App/hsc_Lib/3_Driver/motor_standard.h` - 对齐速度/方向类参数命名习惯。
  - **Test References**:
    - `App/hsc_Lib/1_Task/test.c` - 参考当前工程“测试入口函数”组织方式，后续补测可复用入口模式。
  - **External References**:
    - `https://semver.org/` - 协议版本语义规则。
  - **WHY Each Reference Matters**:
    - 确保新合同文件与既有工程风格兼容，减少后续大面积重命名与接口返工。

  **Acceptance Criteria**:
  - [ ] `platform_contract.h` 中包含：协议版本、心跳超时、故障码、安全状态、命令结构。
  - [ ] `platform_contract.c` 提供可编译的默认配置对象。
  - [ ] `platform_contract.md` 说明版本兼容策略（不兼容时进入 STOP）。

  **QA Scenarios (MANDATORY)**:
  ```text
  Scenario: 合同文件完整性检查（Happy path）
    Tool: Bash
    Preconditions: 已完成 T1 文件创建
    Steps:
      1. 执行 `python tools/contract_check.py --header App/hsc_Lib/2_Control/platform_contract.h`
      2. 断言输出包含字段：PROTOCOL_VERSION、HEARTBEAT_TIMEOUT_MS、SAFETY_STATE_STOP
      3. 执行 `python tools/contract_check.py --doc App/hsc_Lib/2_Control/platform_contract.md`
    Expected Result: 两次命令返回码 0，且报告字段缺失数为 0
    Failure Indicators: 返回码非 0；报告中出现 missing_required_field
    Evidence: .sisyphus/evidence/task-1-contract-check.log

  Scenario: 版本不兼容防护检查（Failure path）
    Tool: Bash
    Preconditions: 准备 fixtures/contract_invalid_version.h
    Steps:
      1. 执行 `python tools/contract_check.py --header fixtures/contract_invalid_version.h`
      2. 断言输出包含 `INCOMPATIBLE_VERSION` 与 `SAFE_REJECT`
    Expected Result: 命令返回码为 1，失败原因明确
    Evidence: .sisyphus/evidence/task-1-contract-invalid.log
  ```

  **Evidence to Capture**:
  - [ ] `task-1-contract-check.log`
  - [ ] `task-1-contract-invalid.log`

  **Commit**: YES
  - Message: `feat(contract): define platform protocol and safety baseline`
  - Files: `App/hsc_Lib/2_Control/platform_contract.*`, `App/hsc_Lib/2_Control/platform_contract.md`
  - Pre-commit: `python tools/contract_check.py --all`

- [ ] 2. 打通 CAN 底层驱动骨架（中断 + 队列 + 收发 API）

  **What to do**:
  - 新增 `App/hsc_Lib/3_Driver/can_bus.h/.c`，封装 CAN 初始化、发送、接收缓冲、bus-off 状态查询。
  - 在 `Core/Src/stm32f4xx_it.c` 接入 CAN RX 中断回调到统一入口（仅投递，不做重逻辑）。
  - 在 `App/hsc_Lib/1_Task/app_main.c` 增加 CAN 驱动初始化调用与启动日志。

  **Must NOT do**:
  - 禁止在本任务实现应用层协议字段解析。
  - 禁止在中断中做阻塞调用或大量日志打印。

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 涉及 HAL 中断、并发边界和驱动稳定性，复杂度中高。
  - **Skills**: `[]`
    - 主要依赖嵌入式驱动经验，不需外部技能。
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: 非 UI 任务。

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 T1/T3/T5）
  - **Blocks**: T9, T10, T13, T14
  - **Blocked By**: None

  **References**:
  - **Pattern References**:
    - `Core/Src/usart.c` - 参考现有外设初始化与 MSP 调用风格。
    - `Core/Src/stm32f4xx_it.c` - 参考中断入口组织与回调转发方式。
  - **API/Type References**:
    - `Core/Inc/main.h` - 外设句柄声明风格。
    - `App/hsc_Lib/3_Driver/encoder.h` - 驱动头文件 API 命名风格。
  - **Test References**:
    - `App/hsc_Lib/1_Task/test.c` - 参考硬件验证入口组织。
  - **External References**:
    - `https://www.st.com/resource/en/user_manual/um1725-description-of-stm32f4-hal-and-lowlayer-drivers-stmicroelectronics.pdf` - STM32 HAL/CAN 驱动约束。
  - **WHY Each Reference Matters**:
    - 统一风格可降低后续调试成本，避免在中断/任务边界引入不可控行为。

  **Acceptance Criteria**:
  - [ ] `can_bus_init()` 成功后输出统一启动日志。
  - [ ] 回环或双节点测试中，发送帧可被接收缓冲读取。
  - [ ] bus-off 触发时可检测并上报状态。

  **QA Scenarios (MANDATORY)**:
  ```text
  Scenario: CAN 收发冒烟测试（Happy path）
    Tool: Bash
    Preconditions: 开发板上电，CAN 线束与终端电阻正确
    Steps:
      1. 执行 `python tools/can_smoke_test.py --mode loopback --duration 30`
      2. 断言脚本输出 `tx_count > 0` 且 `rx_count == tx_count`
      3. 断言 `bus_off_count == 0`
    Expected Result: 返回码 0，收发计数一致
    Failure Indicators: 发送成功但接收为 0；出现 bus_off_count > 0
    Evidence: .sisyphus/evidence/task-2-can-smoke.log

  Scenario: CAN 异常总线处理（Failure path）
    Tool: Bash
    Preconditions: 可注入异常帧或断开总线
    Steps:
      1. 执行 `python tools/can_fault_inject.py --case bus_off`
      2. 断言固件日志出现 `CAN_BUS_OFF` 与 `SAFE_STOP_PENDING`
    Expected Result: 系统进入受控降级，不死机
    Evidence: .sisyphus/evidence/task-2-can-busoff.log
  ```

  **Evidence to Capture**:
  - [ ] `task-2-can-smoke.log`
  - [ ] `task-2-can-busoff.log`

  **Commit**: YES
  - Message: `feat(can): add can bus driver skeleton with irq dispatch`
  - Files: `App/hsc_Lib/3_Driver/can_bus.*`, `Core/Src/stm32f4xx_it.c`, `App/hsc_Lib/1_Task/app_main.c`
  - Pre-commit: `python tools/can_smoke_test.py --mode loopback --duration 10`

- [ ] 3. 接入触摸屏驱动并绑定 LVGL 输入设备

  **What to do**:
  - 在 `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_touch_stub.c/.h` 基础上接入真实触摸读数路径。
  - 新增 `App/hsc_Lib/3_Driver/OLED/lvgl_mode/touch_panel_uart.c/.h`（或与硬件一致的接口文件）。
  - 在 `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_port.c` 完成 indev 注册与坐标映射。

  **Must NOT do**:
  - 禁止在该任务加入复杂 UI 页面逻辑。
  - 禁止把触摸协议解析写入中断重逻辑。

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 硬件协议解析 + LVGL 绑定 + 稳定性边界，属于中高复杂度。
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: 负责触摸交互流畅性和坐标映射可用性。
  - **Skills Evaluated but Omitted**:
    - `playwright`: 非浏览器页面，不适用。

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 T1/T2/T5）
  - **Blocks**: T6, T13, T14
  - **Blocked By**: None

  **References**:
  - **Pattern References**:
    - `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_touch_stub.h` - 当前触摸占位接口约定。
    - `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_port.h` - LVGL 端口层初始化入口。
  - **API/Type References**:
    - `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.h` - UI 层调用边界。
    - `App/hsc_Lib/3_Driver/encoder_knob.h` - 参考输入设备抽象风格。
  - **Test References**:
    - `App/hsc_Lib/2_Control/menu_uimenlvg.c` - 现有 LVGL 运行循环节奏。
  - **External References**:
    - `https://docs.lvgl.io/8/porting/indev.html` - LVGL 输入设备驱动规范。
  - **WHY Each Reference Matters**:
    - 保证触摸驱动与现有 LVGL 运行节奏一致，避免“可点击但不稳定”问题。

  **Acceptance Criteria**:
  - [ ] 触摸坐标可正确映射到屏幕范围。
  - [ ] 连续点击/滑动时无明显卡顿或错触（日志无异常风暴）。
  - [ ] 触摸掉线可被检测并上报状态。

  **QA Scenarios (MANDATORY)**:
  ```text
  Scenario: 触摸输入有效性（Happy path）
    Tool: Bash
    Preconditions: 触摸屏与串口链路连接正常
    Steps:
      1. 执行 `python tools/touch_inject_test.py --points "40,60;120,60;120,120"`
      2. 断言日志出现 `TOUCH_DOWN x=40 y=60` 等精确坐标事件
      3. 断言 UI 状态字段 `touch_event_count >= 3`
    Expected Result: 返回码 0，注入坐标与固件记录一致
    Failure Indicators: 坐标越界、事件丢失、触发无响应
    Evidence: .sisyphus/evidence/task-3-touch-happy.log

  Scenario: 触摸链路掉线处理（Failure path）
    Tool: Bash
    Preconditions: 可断开触摸通信线
    Steps:
      1. 执行 `python tools/touch_inject_test.py --case disconnect_midway`
      2. 断言日志包含 `TOUCH_LINK_LOST` 与 `INPUT_DEGRADED`
    Expected Result: 系统不崩溃，进入降级输入状态
    Evidence: .sisyphus/evidence/task-3-touch-disconnect.log
  ```

  **Evidence to Capture**:
  - [ ] `task-3-touch-happy.log`
  - [ ] `task-3-touch-disconnect.log`

  **Commit**: YES
  - Message: `feat(touch): wire touch panel input into lvgl indev path`
  - Files: `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_touch_stub.*`, `App/hsc_Lib/3_Driver/OLED/lvgl_mode/touch_panel_uart.*`, `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_port.c`
  - Pre-commit: `python tools/touch_inject_test.py --points "20,20;60,60"`

- [ ] 4. 最小 FreeRTOS 任务骨架接管主流程

  **What to do**:
  - 基于 `App/hsc_Lib/2_Control/menu_freertos.c` 改造成阶段1任务拓扑：Control/CAN/Sensor/UI（4任务）。
  - 在 `App/hsc_Lib/1_Task/app_main.c` 中增加 RTOS 启动路径和裸机回退开关。
  - 保持 `Core/Src/main.c` 初始化顺序稳定，避免破坏现有 HAL 初始化。

  **Must NOT do**:
  - 禁止在本任务实现具体业务算法。
  - 禁止引入动态任务创建/频繁 malloc。

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 涉及调度结构、任务优先级和并发边界，影响全局稳定性。
  - **Skills**: `[]`
    - 重点在 RTOS 架构整理，不依赖专项技能。
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: 不涉及界面设计。

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 T1/T2/T3/T5）
  - **Blocks**: T7, T8, T10, T11, T13
  - **Blocked By**: T1

  **References**:
  - **Pattern References**:
    - `App/hsc_Lib/2_Control/menu_freertos.c` - 现有 FreeRTOS 任务和队列样板。
    - `App/hsc_Lib/1_Task/app_main.c` - 当前业务初始化与循环入口。
  - **API/Type References**:
    - `App/hsc_Lib/2_Control/menu_freertos.h` - 任务入口声明风格。
    - `Core/Src/main.c` - `App_Init/App_Loop` 调用时机。
  - **Test References**:
    - `App/hsc_Lib/1_Task/test.c` - 参考任务内最小硬件动作验证。
  - **External References**:
    - `https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/01-Tasks-and-co-routines/01-Tasks`
  - **WHY Each Reference Matters**:
    - 确保 RTOS 接管是“最小侵入式”而不是重写主流程。

  **Acceptance Criteria**:
  - [ ] 系统进入 FreeRTOS 后 4 个任务均可周期性输出心跳计数。
  - [ ] UI 任务不阻塞 Control 任务周期。
  - [ ] 在配置关闭 RTOS 时仍可回到现有裸机流程。

  **QA Scenarios (MANDATORY)**:
  ```text
  Scenario: 任务存活检查（Happy path）
    Tool: interactive_bash
    Preconditions: 固件刷写成功并接入串口日志
    Steps:
      1. 打开串口监视并执行 `python tools/task_heartbeat_watch.py --duration 60`
      2. 断言输出包含 Control/CAN/Sensor/UI 四个任务计数
      3. 断言 60 秒内无任务计数停滞
    Expected Result: 返回码 0，四任务持续增长
    Failure Indicators: 任一任务计数冻结超过 2 个周期
    Evidence: .sisyphus/evidence/task-4-rtos-heartbeat.log

  Scenario: UI 负载压力下控制任务保持周期（Failure path）
    Tool: Bash
    Preconditions: 可执行 UI 压测脚本
    Steps:
      1. 执行 `python tools/ui_stress_test.py --duration 30 --event-rate 50`
      2. 同时执行 `python tools/control_period_check.py --threshold-ms 20`
    Expected Result: 控制任务周期 P95 不超过 20ms
    Evidence: .sisyphus/evidence/task-4-rtos-stress.log
  ```

  **Evidence to Capture**:
  - [ ] `task-4-rtos-heartbeat.log`
  - [ ] `task-4-rtos-stress.log`

  **Commit**: YES
  - Message: `feat(rtos): bootstrap minimal 4-task scheduler topology`
  - Files: `App/hsc_Lib/2_Control/menu_freertos.c`, `App/hsc_Lib/1_Task/app_main.c`, `App/hsc_Lib/2_Control/menu_freertos.h`
  - Pre-commit: `python tools/task_heartbeat_watch.py --duration 10`

- [ ] 5. 实现安全监督器基础（看门狗签到 + STOP 状态机）

  **What to do**:
  - 新增 `App/hsc_Lib/2_Control/safety_supervisor.h/.c`，实现任务签到、故障锁存、状态迁移。
  - 在 `App/hsc_Lib/1_Task/app_main.c` 中接入安全周期调用。
  - 与驱动层对齐“安全停机接口”（电机使能断开/输出归零）。

  **Must NOT do**:
  - 禁止将安全逻辑分散到各模块私有分支。
  - 禁止出现“故障后自动恢复不经确认”的隐式行为。

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 涉及系统安全边界、状态机一致性和故障处置策略。
  - **Skills**: `[]`
    - 无需外部技能，重点是一致性设计。
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: 非界面任务。

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 T1/T2/T3/T4）
  - **Blocks**: T8, T9, T13, T14
  - **Blocked By**: T1, T4

  **References**:
  - **Pattern References**:
    - `App/hsc_Lib/2_Control/gyro_collision.c` - 参考异常检测钩子与处理入口组织。
    - `App/hsc_Lib/1_Task/car_task.c` - 参考控制任务中的执行入口。
  - **API/Type References**:
    - `App/hsc_Lib/2_Control/platform_contract.h` - 复用统一故障码与安全状态。
    - `App/hsc_Lib/3_Driver/motor-m.h` - 安全停机输出边界。
  - **Test References**:
    - `CODE_AUDIT_REPORT.md` - 历史关键风险，避免重犯。
  - **External References**:
    - `https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/09-Software-timers-and-watchdogs`
  - **WHY Each Reference Matters**:
    - 安全逻辑必须单点收敛，保证故障可预测、可复盘。

  **Acceptance Criteria**:
  - [ ] 任务签到超时可触发 STOP 且锁存故障码。
  - [ ] 心跳丢失后在阈值时延内执行安全停机。
  - [ ] 故障恢复需要显式解锁动作。

  **QA Scenarios (MANDATORY)**:
  ```text
  Scenario: 心跳超时触发 STOP（Happy path）
    Tool: Bash
    Preconditions: 安全监督器已接入主循环
    Steps:
      1. 执行 `python tools/fault_inject_test.py --case heartbeat_lost`
      2. 断言日志包含 `SAFETY_STATE=STOP` 与故障码 `FAULT_HEARTBEAT_TIMEOUT`
      3. 断言输出归零日志 `ACTUATOR_ZERO_OUTPUT`
    Expected Result: STOP 触发时延 <= 200ms
    Failure Indicators: 超时后仍有非零输出
    Evidence: .sisyphus/evidence/task-5-safety-heartbeat.log

  Scenario: 未解锁禁止恢复（Failure path）
    Tool: Bash
    Preconditions: 系统已处于 STOP 锁存
    Steps:
      1. 执行 `python tools/fault_inject_test.py --case recover_without_unlock`
      2. 断言状态保持 STOP，且返回 `RECOVERY_DENIED`
    Expected Result: 无显式解锁时不能恢复输出
    Evidence: .sisyphus/evidence/task-5-safety-lock.log
  ```

  **Evidence to Capture**:
  - [ ] `task-5-safety-heartbeat.log`
  - [ ] `task-5-safety-lock.log`

  **Commit**: YES
  - Message: `feat(safety): add watchdog check-in and stop-state machine`
  - Files: `App/hsc_Lib/2_Control/safety_supervisor.*`, `App/hsc_Lib/1_Task/app_main.c`
  - Pre-commit: `python tools/fault_inject_test.py --case heartbeat_lost`

- [ ] 6. 完成触摸中控主页面与控制事件映射

  **What to do**:
  - 在 `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.c` 增加阶段1主控页面（使能、速度、方向、急停、故障提示）。
  - 在 `App/hsc_Lib/2_Control/menu_uimenlvg.c` 中完成 UI 运行循环与事件上报桥接。
  - 输出页面控件 ID 与触摸坐标映射表，供自动注入脚本复用。

  **Must NOT do**:
  - 禁止加入动画、复杂皮肤与非必要页面。
  - 禁止在 UI 层直接驱动电机硬件。

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: 主要是 HMI 交互结构与状态可视化。
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: 确保操作路径明确、状态展示清晰。
  - **Skills Evaluated but Omitted**:
    - `dev-browser`: 当前不是浏览器页面。

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2（与 T7/T8/T9/T10/T11）
  - **Blocks**: T7, T14
  - **Blocked By**: T1, T3

  **References**:
  - **Pattern References**:
    - `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.c` - 现有 LVGL 组件组织方式。
    - `App/hsc_Lib/2_Control/menu.c` - 参考现有页面切换逻辑与状态显示思路。
  - **API/Type References**:
    - `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.h` - UI 对外函数边界。
    - `App/hsc_Lib/2_Control/platform_contract.h` - 控制命令与状态字段来源。
  - **Test References**:
    - `App/hsc_Lib/2_Control/menu_uimenlvg.c` - UI 运行循环节奏。
  - **External References**:
    - `https://docs.lvgl.io/8/widgets/index.html` - 控件选型与事件处理规范。
  - **WHY Each Reference Matters**:
    - 保证 UI 与控制接口一一对应，避免“界面显示与真实状态脱节”。

  **Acceptance Criteria**:
  - [ ] 页面具备最小控件集：使能、速度、方向、急停、状态灯、故障码。
  - [ ] 每个控件事件均可上报统一事件总线（不直连硬件）。
  - [ ] 控件 ID/坐标映射文档可被注入脚本读取。

  **QA Scenarios (MANDATORY)**:
  ```text
  Scenario: 主页面触发控制事件（Happy path）
    Tool: Bash
    Preconditions: UI 页面已加载到运行状态
    Steps:
      1. 执行 `python tools/touch_inject_test.py --profile main_panel_enable_forward`
      2. 断言日志顺序包含 `UI_EVT_ENABLE` -> `UI_EVT_SPEED_SET` -> `UI_EVT_DIR_FORWARD`
      3. 断言状态区文本包含 `MODE:MANUAL` 与 `ARMED:1`
    Expected Result: 事件顺序正确，状态显示同步
    Failure Indicators: 事件乱序、状态未刷新
    Evidence: .sisyphus/evidence/task-6-ui-mainpanel.log

  Scenario: 非法触摸坐标处理（Failure path）
    Tool: Bash
    Preconditions: 支持注入越界坐标
    Steps:
      1. 执行 `python tools/touch_inject_test.py --points "-10,300;999,999"`
      2. 断言日志包含 `UI_EVT_REJECT_OUT_OF_RANGE`
    Expected Result: 非法事件被拒绝，不改变控制状态
    Evidence: .sisyphus/evidence/task-6-ui-invalid-touch.log
  ```

  **Evidence to Capture**:
  - [ ] `task-6-ui-mainpanel.log`
  - [ ] `task-6-ui-invalid-touch.log`

  **Commit**: YES
  - Message: `feat(hmi): implement touch control panel and event mapping`
  - Files: `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.c`, `App/hsc_Lib/2_Control/menu_uimenlvg.c`, `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.h`
  - Pre-commit: `python tools/touch_inject_test.py --profile main_panel_enable_forward`

---

## Final Verification Wave (MANDATORY)

> 4 个复核任务必须并行执行，且全部 `APPROVE` 才允许结束。

- [ ] F1. **计划符合性审计** — `oracle`
  - 逐条核对 `Must Have / Must NOT Have` 与实际实现、证据文件。
  - 输出：`Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT`

- [ ] F2. **代码质量审查** — `unspecified-high`
  - 执行构建与关键测试；检查 `as any`、空 catch、调试残留、未使用符号。
  - 输出：`Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N/N] | VERDICT`

- [ ] F3. **全量执行型 QA** — `unspecified-high`
  - 严格按每个任务的 QA 场景跑通，补齐证据到 `.sisyphus/evidence/final-qa/`。
  - 输出：`Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N] | VERDICT`

- [ ] F4. **范围一致性检查** — `deep`
  - 对照每个任务的 `What to do / Must NOT do` 检查越界与遗漏。
  - 输出：`Tasks [N/N compliant] | Scope Creep [YES/NO] | VERDICT`

---

## Commit Strategy

- **Commit Group 1 (Wave 1)**: `feat(platform): add contracts, can/touch/rtos/safety foundations`
- **Commit Group 2 (Wave 2)**: `feat(control): implement hmi-command-actuation-can-state pipeline`
- **Commit Group 3 (Wave 3)**: `feat(integration): add log-replay fault-matrix demo automation and debt register`
- **Commit Group 4 (Verification fixes)**: `fix(stability): close verification findings and harden safety edges`

---

## Success Criteria

### Verification Commands
```bash
# 构建（按实际工具链替换）
python tools/build_check.py

# CAN 链路验证
python tools/can_smoke_test.py --duration 60

# 触摸事件注入与响应验证
python tools/touch_inject_test.py --profile demo_standard

# 故障注入验证
python tools/fault_inject_test.py --cases heartbeat_lost,touch_disconnect,task_hang

# 日志回放一致性
python tools/log_replay_check.py --input .sisyphus/evidence/task-12-log.bin
```

### Final Checklist
- [ ] 所有 Must Have 已实现且有证据文件
- [ ] 所有 Must NOT Have 未出现
- [ ] 全部安全触发能在阈值内进入 STOP
- [ ] CAN 与触摸链路的异常路径已验证
- [ ] 日志可导出、可回放、可校验
- [ ] 技术债清单与阶段2/3路线图已落档
