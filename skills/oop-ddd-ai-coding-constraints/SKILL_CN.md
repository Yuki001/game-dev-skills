---
name: oop-ddd-ai-coding-constraints
description: 为 C# 和 TypeScript 游戏开发实施 OOP 与 DDD 工程约束。用于实现、重构、审查或测试玩法系统、战斗、背包、成长、任务、场景、对局、玩家数据、存档流程、Domain 主导的引擎 View wrapper、领域模型、Aggregate、Application Service、Repository、垂直切片、Public API、Context 共享依赖和确定性测试缝隙。保持封装，让 Domain 隔离引擎细节，禁止测试专用生产后门，并通过公共契约交付完整游戏行为。
---

# 游戏开发的 OOP + DDD 工程约束

在 C# 和 TypeScript 游戏项目中，以领域封装和可验证的玩法行为为核心完成开发。

## 一、OOP/DDD 通用模式

### 执行顺序

对每个实现、重构或测试任务依次执行：

1. **识别契约**：确认面向玩家或策划的行为、现有 public API、模块边界、领域不变量、引擎限制和项目惯例。
2. **选择垂直切片**：把任务收敛为一个可从真实入口——输入、命令、引擎回调或服务器请求——执行并产生可观察游戏结果的最小玩法行为。
3. **设计边界**：把业务规则放入 Domain，把用例编排放入 Application，把外部依赖放到正式 port 后面，并把作用域共享依赖收敛到类型化 Context。
4. **实现闭环**：串通入口、应用服务、领域模型、port 和基础设施实现，不留下未接线模块。
5. **通过契约测试**：从 public boundary 准备状态、触发行为并断言业务结果。
6. **执行封装审计**：检查 public surface、测试缝隙、跨层依赖和未完成标记后再交付。

发生冲突时，按以下优先级处理：

1. 用户明确要求和已批准的 public contract；
2. 领域不变量与封装；
3. 现有项目架构和命名惯例；
4. 本文件的默认模式。

不要借“遵守 DDD”擅自重写用户已确定的架构。发现现有设计与约束冲突时，说明具体冲突及影响；仅在任务授权范围内修改。

### 架构边界

默认采用以下职责划分：

| 层 | 职责 | 不应承担 |
| --- | --- | --- |
| Interface | 输入适配、UI/表现层、引擎回调、Controller 和服务器入口；把输入转换为 use case | 玩法规则、直接持久化 |
| Application | 玩法 use case、command、handler、会话/事务边界、DTO 和跨对象编排 | 核心玩法规则 |
| Domain | 战斗、背包、成长、任务、经济和玩家状态模型；Entity、Aggregate、Value Object、Domain Service/Event 和 port | 引擎、渲染、场景树、网络、数据库或基础设施细节 |
| Infrastructure | 引擎适配、存档/持久化实现、网络、平台 SDK、资源访问、物理/寻路适配、时钟、随机源和 ID 实现 | 玩法规则 |

保持依赖方向：

```text
Interface -> Application -> Domain
Infrastructure -> Domain/Application ports
Domain -> no framework or infrastructure dependency
```

禁止：

- UI、输入、引擎回调或 Controller 直接访问 Repository，或绕过 Application 编排 use case；
- Domain 依赖引擎 Component/Node、场景树、渲染、物理 API、网络、ORM、数据库 client、HTTP 或 Infrastructure；
- Entity 主动调用 Repository；
- 测试绕过公共边界访问内部实现。

只有当现有项目明确采用不同分层时才沿用其结构，同时继续保护依赖方向和领域封装。

### 领域模型与封装

#### Aggregate 与 Entity

- 让 Aggregate Root 维护一致性边界和业务不变量。
- 通过表达玩法意图的方法改变状态，例如 `ApplyDamage`、`EquipItem`、`CompleteQuest`、`GrantReward`。
- 把字段、子实体集合、领域事件集合、缓存和策略对象保持为 private。
- 不要提供 public setter 或可变集合来代替领域行为。
- 只返回稳定值对象或只读 DTO/snapshot；不要返回内部集合本身。
- 让 Entity 保持 identity，并在其生命周期内通过行为维护有效状态。

#### Value Object

- 保持不可变；
- 在创建时校验；
- 按值比较；
- 不暴露可变内部数据。

#### Repository

- 围绕 Aggregate Root 定义 Repository；
- 让 Repository 持久化和重建 Aggregate，不泄露存储细节；
- 由 Application Service 调用 Repository；
- 不要用 Repository 偷看另一个被测对象的内部状态，除非测试对象就是该 Repository。

#### Application Service

- 编排 use case、事务、Repository、Domain 对象和外部 port；
- 把核心业务判断委托给领域模型；
- 返回契约所需的 DTO/result，不返回内部可变对象图。

### Public API Gate

把 public API 视为稳定产品契约，而不是测试工具箱。

允许 public surface 表达：

- 真实调用方需要的业务能力；
- 稳定的命令、查询、结果、DTO 或 snapshot；
- 正式的架构 port 和策略接口。

禁止 public surface 暴露：

- 内部字段、可变集合、cache、Repository 或实现类；
- 仅供断言使用的中间状态；
- 测试专用 API 或成员——如 `ForTest`、`TestOnly`、`__test`、`ExposeInternal`、`ResetForTest`、`GetInternalState` 等命名——包括测试专用 getter、setter、delegate、proxy、callback 或 hook。完整的测试后门清单见“测试相关的规范”。

新增或扩大 public API 前，依次判断：

1. 是否存在真实的生产调用方？
2. 是否表达明确业务能力，而不是实现步骤？
3. 现有契约是否已经能够完成该行为？
4. 是否泄露内部表示或引入可变状态？
5. 去掉测试后，该 API 是否仍然成立？

如果答案表明它只是测试便利，拒绝新增并重写测试策略。如果它是任务明确要求的最小业务契约，可以实现；如果会产生未授权且有意义的契约扩张，先说明 API、调用方、必要性和替代方案，再请求确认。

### 垂直切片与完成度

每次交付都形成以下闭环中适用于当前系统的部分：

```text
Player input / gameplay command / engine or server entry
  -> Application service
  -> Domain behavior
  -> Port
  -> Engine/infrastructure adapter
  -> Observable game result through public boundary
```

禁止提交：

- `TODO`、`deferred`、`placeholder`、`stub`、`not implemented`；
- 假成功返回或吞掉失败；
- “稍后接入”的孤立模块；
- 只横向创建类、没有可运行行为的骨架。

依赖缺失但任务允许本地替代时，实现最小真实版本并接入闭环，例如实现正式 port 的内存玩家 Repository、固定时钟或带种子的随机源。不要把 fake 变成生产代码后门。

## 二、个人偏好的特殊模式

### 游戏开发边界

#### 分离 Domain 语义与引擎语义

- 不要把引擎 Entity/Component 或 ECS Component 直接等同于 DDD Entity、Aggregate 或 Value Object。根据身份、不变量、所有权和生命周期确定 DDD 角色。
- 把玩法不变量保留在纯领域代码中。让 View wrapper、帧回调、输入处理器、动画事件、RPC handler 和场景脚本把引擎事件转换为 Application command 或 Domain 行为。

#### 建模运行时输入与引擎服务

- 把 `deltaTime`、输入命令、目标 ID 和技能请求等逐帧或单次命令值作为 method/command 输入传递，不要把瞬时输入变成全局 Context 状态。
- 当玩法结果依赖时间、随机数、物理查询、寻路、资源查找、网络或平台服务时，通过 Context 成员或正式 port 隔离它们，并在测试中提供确定性实现。

#### 限定状态、生命周期与性能边界

- 按游戏进程、世界、场景、对局/会话或玩家档案等有意义的生命周期限定 Context 实例，隔离并行场景、对局、服务器房间和模拟。
- 不要把可变场景对象、活跃 Entity、当前 command 或逐帧状态放进依赖 Context。Context 承载设施，Domain 对象拥有玩法状态。
- 通过 factory 或 Aggregate 行为从存档数据重建模型，不要依靠 public setter 把持久化 DTO 直接变成可变领域模型。
- 在热路径中兼顾性能但不要破坏封装。优先使用所有权安全的操作、稳定 ID、只读视图或预分配结果缓冲区，不要暴露可变集合。

#### Domain 主导的 View Wrapper

优先使用领域对象作为主要对象, 而不是引擎场景框架指定的做法：

- 让 `Actor`、`Player`、`Enemy` 等 Domain Object 保持为普通类，不继承引擎场景类型。
- 使用引擎无关的 View 契约和私有持有原生节点的普通 wrapper。引擎必须继承时，另设最小 Host，把回调转发给 Application、把表现操作转发给 wrapper。

不要采取以下结构 (属于违规)：

**Unity** :
```csharp
public class ActorController : MonoBehaviour {}
```

**Godot** :
```csharp
public partial class ActorNode : Node {}
```

需要采用以下结构：

**Unity** :
```csharp
public class Actor
{
    private ActorView _view = null;
    public Initialize() {
        // 使用合适的方法创建 _view，例如factory
        _view = _context.ViewFactory.CreateActor(configID);
    }
}

public class ActorView
{
    private GameObject _node = null;

    void Initialize(string prefabPath);
    void SetPosition(WorldPosition position);
    void PlayAnimation(AnimationId animation);
    void Destroy();
    // 把 ActorView 操作转换为对所封装 GameObject 的操作。
}
```

**Godot** :
```csharp
public class Actor
{
    private ActorView _view = null;
    public Initialize() {
        // 使用合适的方法创建 _view，例如factory
        _view = _context.ViewFactory.CreateActor(configID);
    }
}

public class ActorView
{
    private Node _node = null;

    void Initialize(string prefabPath);
    void SetPosition(WorldPosition position);
    void PlayAnimation(AnimationId animation);
    void Destroy();
    // 把 ActorView 操作转换为对所封装 Node 的操作。
}
```

- 使用位置、朝向、动画、可见性或特效等游戏语义表达 View 操作，绝不暴露原始引擎 handle。
- 把节点查找、Component 访问和表现 API 保留在 wrapper 内；继承式 Host 不含 Domain 状态或玩法规则。
- 让 scene bootstrap、factory 或 composition root 创建并拥有原生节点、wrapper、注入以及 spawn/despawn 和 dispose 顺序。
- 让 Domain Object 驱动窄 View 契约；引擎回调通过 Application command 或显式 Domain 方法返回。
- 不要为了测试暴露 wrapper 或原生节点；只为正式可见的 View 行为使用 fake View。

### Context 模式与构造函数门禁

使用 Context 模式收敛架构层、大领域边界或运行实例内共享的依赖。这里的“全局依赖”是相对于某个作用域共享的设施，不要求它是进程级 singleton。

默认选择稳定、粗粒度的 Context 边界：

1. 按整体架构层组织，例如 `GameApplicationContext`、`GameInfrastructureContext`；
2. 按大领域或 Bounded Context 组织，例如 `CombatContext`、`PlayerContext`、`EconomyContext`；
3. 需要多实例隔离时，为同一种大 Context 创建不同运行实例，而不是为每个 use case 定义新类型。

不要因为某个 Handler 只使用其中少量依赖，就创建 `ResolveCombatTurnContext`、`GrantRewardContext` 等微型 UseCase Context。Context 的边界应反映稳定的架构或游戏领域边界，而不是单个调用方当前的参数列表。

#### 识别全局依赖

如果一个依赖满足任一条件，就把它视为全局依赖并放入某个 Context：

- 被同一作用域内的多个对象或 use case 复用；
- 生命周期通常长于单个业务对象或单次调用；
- 代表 Repository、应用/领域 Service、Gateway、Clock、随机数/ID 生成器、EventBus、物理/寻路查询、资源服务、网络 Gateway、配置源或资源注册表等共享设施；
- 需要在测试、运行实例或场景之间成组替换或隔离。

不要把“全局”等同于静态变量。同一种 `CombatContext`、`PlayerContext` 可以为不同场景、玩家会话或测试创建独立实例。

#### 收敛构造函数

审查每个构造函数参数并强制分类：

1. **全局依赖**：必须成为相关 Context 的显式、强类型成员；构造函数只接收 Context，不再单独接收该依赖。
2. **非全局依赖**：只有具备对象实例专属的身份、所有权、配置或生命周期时，才允许作为 Context 之外的构造函数参数。
3. **单次 use case 输入**：优先作为 public method/command 参数传入，不要长期保存在 service 构造函数中。

以下构造函数属于违规：

```text
Handler(context, repository, clock)       // repository、clock 泄漏在 Context 外
Handler(repository, clock, eventBus)      // 全局依赖未收敛
Handler(globalContextWithEverything)      // 无边界的万能 Context
```

以下形态符合要求：

```text
Handler(playerContext)
BattleSession(combatContext, encounterSpec) // encounterSpec 仅属于该实例
```

如果无法说明某个额外参数为何是实例专属，就把它移入合适的 Context，或把一次性输入移到方法/command。

#### 设计 Context

- 每个 Context 都实现为围绕大架构层或大领域边界组织的普通类，并由相关 use case 复用；不要为每个调用方的最小依赖集创建 record、data-only DTO 或微型 Context。
- 让 Context 成为其作用域的组装与生命周期 owner：用 private field 持有 systems，并通过 public 只读属性提供访问。
- 使用 `Initialize`、`Update`、`Destroy` 保持明确的创建、更新和销毁顺序；不要求把每个 system 都从 Context 构造函数传入。
- 允许空构造函数或稳定的作用域配置；一次性玩法 command 和实例专属 Entity 不要进入 Context 构造函数。
- 禁止 `Get<T>()`、字符串 key、字典查找或运行时注册，把 Context 退化为 Service Locator。
- 让所拥有的 systems 管理作用域运行时状态和玩法规则；Context 自身不要成为 Entity、command、任意玩法数据或 use case 逻辑的松散容器。
- 让 Context 只暴露当前层允许依赖的 port。Domain Context 不得暴露数据库、HTTP client 或其他 Infrastructure 实现。
- 不要用一个跨全系统的 `AppContext`/`GlobalContext` 聚合所有模块；Context 变大时按领域、层或生命周期继续拆分。

只有当某个 use case 具有稳定的生命周期、事务、安全、隔离或资源边界，并且无法归入现有大 Context、否则会产生真实的跨层或跨领域污染时，才创建专用 UseCase Context。其他情况继续使用所属的大 Context；仅为了缩短构造函数不构成理由。

TypeScript 示例：

```ts
export class SceneContext {
  #random!: RandomService;
  #collision!: CollisionSystem;
  #pool!: ObjectPool;

  get random(): RandomService { return this.#random; }
  get collision(): CollisionSystem { return this.#collision; }
  get pool(): ObjectPool { return this.#pool; }

  initialize(): void {
    this.#random = new RandomService();
    this.#pool = new ObjectPool();
    this.#collision = new CollisionSystem(this.#random, this.#pool);
  }

  update(deltaTime: number): void {
    this.#collision.update(deltaTime);
    this.#pool.update(deltaTime);
  }

  destroy(): void {
    this.#collision.destroy();
    this.#pool.destroy();
    this.#random.destroy();
  }
}
```

C# 示例：

```csharp
public sealed class SceneContext
{
    private RandomService _random = null!;
    private CollisionSystem _collision = null!;
    private ObjectPool _pool = null!;

    public RandomService Random => _random;
    public CollisionSystem Collision => _collision;
    public ObjectPool Pool => _pool;

    public void Initialize()
    {
        _random = new RandomService();
        _pool = new ObjectPool();
        _collision = new CollisionSystem(_random, _pool);
    }

    public void Update(float deltaTime)
    {
        _collision.Update(deltaTime);
        _pool.Update(deltaTime);
    }

    public void Destroy()
    {
        _collision.Destroy();
        _pool.Destroy();
        _random.Destroy();
    }
}
```

### 非必要不抽接口

只有当某类型在生产中确有多个实现变种时，才为其新增 interface/port。单一实现的类一律使用具体类——不抽接口、不建 port、不为"未来灵活性"预先抽象。预先抽象属于过度设计，只会无意义地扩大契约面。

- 判断标准：该类型是否会有 ≥2 个真实生产实现？没有 → 具体类。
- 不要仅为可测性而新增 port。若一个没有真实变种的类型无法在不 fake 的情况下写单元测试，该测试应归入集成（见“测试相关的规范”），而不是单元测试。
- 衍生规则：执行任务时不得擅自新增未授权接口。若确需偏离，先询问用户。

### 语言专项检查

#### TypeScript

- 优先使用 ECMAScript `#private` 或项目既有的 `private` 约定；
- 对外 DTO 使用 `Readonly` 和只读集合；
- 只从 public barrel 导出契约，不导出 internal 实现或 Domain 内部类型；
- 不在 public Domain 契约中暴露引擎/运行时对象；在模块边界进行适配。

#### C#

- 领域状态使用 private field 和受控的 `private set`；
- 引擎支持时使用 `[SerializeField] private` 完成编辑器绑定；不要仅为 Inspector 访问把玩法状态设为 public。

跨语言的封装规则在各自的权威小节：不返回内部可变集合（见“领域模型与封装”）、不为测试绕过私有访问（见“测试相关的规范”）、View wrapper 保持普通类并私有持有原生节点（见“Domain 主导的 View Wrapper”）。

## 三、测试相关的规范

公共表面不得新增测试专用成员，该 API 侧原则见“Public API Gate”。本部分覆盖测试侧：可替换缝隙、黑盒行为，以及单元/集成划分。

### 测试缝隙与外部依赖

仅为真实边界建立可替换的 port/interface。合理边界包括：

- Repository、存档系统、平台 SDK 和外部服务；
- 时间、随机数、物理查询、寻路、UUID 等非确定性或引擎提供的来源；
- 伤害计算、掉落选择、生成、匹配和权限等正式玩法策略；
- 生产环境确实可能有多个实现的组件。

让测试 fake 实现同一个正式 port，例如 `InMemoryPlayerRepository`、`FixedClock`、`SeededRandom` 或 `FakeGameEventPublisher`。不要为测试新增第二套入口或控制通道。

完整作用域测试应执行同一套 Context 生命周期：构造 Context、调用 `Initialize`、按需驱动 `Update`，最后执行 `Destroy`。独立 system 测试在 system 边界使用正式 port/fake；不要增加测试专用 Context setter，也不要恢复多个独立的全局依赖构造参数。

拒绝以下伪装成“依赖注入”的测试后门：

- 仅用于确认内部步骤的 observer/delegate；
- 运行时替换私有实现的 `SetXxxForTest`；
- 暴露缓存、集合或调用次数的 proxy；
- 没有生产语义的 hook。

### 行为测试规则

默认执行黑盒测试：

- 通过 public 玩法方法、Application Service、输入/服务器入口、Domain Event 或正式 DTO/snapshot 观察结果；
- 通过 public contract 或正式 port fake 准备状态；
- 断言业务结果、领域错误和可见副作用；
- 优先为主流程提供 acceptance/integration coverage，再补充必要的单元测试。

禁止：

- 访问 private、protected 或 internal 字段和集合；
- 为测试修改生产成员的可见性；
- TypeScript 中使用 `as any`、`obj["privateField"]` 或 descriptor 绕过 private；
- C# 中使用 reflection 或 `InternalsVisibleTo` 绕过封装；
- 断言私有方法是否调用、内部集合长度或缓存布局等实现细节。

测试失败时先分类，再修改：

| 类型 | 处理方式 |
| --- | --- |
| implementation bug | 修复实现，使其满足既有契约 |
| test bug | 改为从公共边界断言行为 |
| contract gap | 设计最小、具有业务语义的 public contract；必要时请求确认 |
| architecture gap | 增加正式 port/interface，而非测试 hook |
| setup issue | 修复 fixture、配置或环境 |

不要把扩大 public API 作为测试失败的默认解决方案。

#### 单元测试只测单元；集成走真实引擎

自动化的单元测试只覆盖单元类——引擎无关、不依赖引擎/可视化、不涉及 Context 级组装的叶子逻辑。任何需要真实引擎运行时、持有引擎节点、挂载 View 或跨 scope 组装的内容（Context、Bootstrap、GameFlow、View 挂载、场景组装）都属于集成，应通过真实运行引擎来验证，而不是单元测试。

- 单元测试：仅测引擎无关的叶子逻辑（调度器、tick 计数、值对象、数学/集合工具、不含引擎节点的单一领域行为）。
- 不要单元测试：Context、Bootstrap/流程控制器、View wrapper、任何构造 View 或触碰引擎节点的对象。
- 视觉/节点承载类型绝不在单元测试中 fake。通过真实运行场景在引擎中验证（截图、场景树检查、输出/错误日志、运行时断言）。
- 绝不为让某个集成关注点变得可单元测试而修改设计（新增接口、缝隙、setter 或测试专用 hook）。若无法诚实地写单元测试，该行为属于引擎集成，不属于单元测试。
- Context 属于整体集成；其生命周期通过运行真实入口验证，而不是 fake 注入其依赖。

## 四、检查列表

完成任务前逐项检查：

- [ ] 功能可从真实 public boundary 运行，并具有与风险相称的行为测试；
- [ ] Domain 维护玩法不变量，Application 负责编排，引擎回调/adapter 不承载玩法规则；
- [ ] Domain Object 和 View wrapper 避免引擎继承，原生节点保持 private，必要的继承式 Host 保持最小；
- [ ] 影响结果的引擎服务可用于确定性测试，Context 生命周期保持多实例隔离；
- [ ] 共享 systems 位于按大边界组织的普通 Context 类中，使用 private field、只读属性和有序 `Initialize`/`Update`/`Destroy`；
- [ ] Context 不是 Service Locator、状态袋或上帝对象；Context 外的参数具有实例专属语义；
- [ ] 没有 public mutable state、内部集合泄露或可见性扩大；
- [ ] 没有 test-only API、hook、delegate、proxy、reset 方法或内部状态断言；
- [ ] fake 实现正式 port/interface，依赖方向符合项目架构；
- [ ] 没有 TODO、deferred、placeholder、stub 或假成功。

在最终交付中简要报告：

1. 完成的业务闭环；
2. 新增或变更的 public contract（没有则明确说明没有）；
3. 使用的正式 ports/fakes；
4. 验证命令与结果；
5. 任何仍需用户决策的架构问题。
