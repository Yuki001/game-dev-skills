---
name: oop-ddd-ai-coding-constraints
description: 为 C# 和 TypeScript 游戏开发实施 OOP 与 DDD 工程约束。用于实现、重构、审查或验证玩法系统、Domain 主导的引擎 View wrapper、领域模型、Aggregate、Application Service、Repository、Public API 或 Context 共享依赖。保持封装，禁止测试专用生产后门，只对引擎无关的叶子逻辑进行单元测试，并通过真实运行引擎验证集成行为。
---

# 游戏开发的 OOP + DDD 工程约束

在 C# 和 TypeScript 游戏项目中，以领域封装和可验证的玩法行为为核心完成开发。

## 一、OOP/DDD 通用模式

### 架构边界

默认采用以下职责划分：

| 层 | 职责 | 不应承担 |
| --- | --- | --- |
| Interface | 输入适配、UI/表现层、引擎回调、Controller 和服务器入口；把输入转换为 use case | 玩法规则、直接持久化 |
| Application | 玩法 use case、command、handler、会话/事务边界、DTO 和跨对象编排 | 核心玩法规则 |
| Domain | 战斗、背包、成长、任务、经济和玩家状态模型；Entity、Aggregate、Value Object、Domain Service/Event 和 port | 原生引擎 API、原生引擎对象、网络、数据库或基础设施细节 |
| Infrastructure | 引擎适配、存档/持久化实现、网络、平台 SDK、资源访问、物理/寻路适配、时钟、随机源和 ID 实现 | 玩法规则 |

保持依赖方向：

```text
Interface -> Application -> Domain
Infrastructure -> Domain/Application ports
Domain -> no framework or infrastructure dependency
```

禁止：

- UI、输入、引擎回调或 Controller 直接访问 Repository，或绕过 Application 编排 use case；
- Domain 暴露或直接操作原生引擎 Component/Node、场景树、渲染或物理 API、网络、ORM、数据库 client、HTTP 或 Infrastructure；
- Entity 主动调用 Repository；

现有项目明确采用不同分层时沿用其结构，同时继续保护领域封装。

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
- 由 Application Service 调用 Repository。

#### Application Service

- 编排 use case、事务、Repository、Domain 对象和外部 port；
- 把核心业务判断委托给领域模型；
- 返回契约所需的 DTO/result，不返回内部可变对象图。

### Public API Gate

把 public API 视为稳定产品契约，而不是测试工具箱。

允许 public surface 表达：

- 真实生产调用方需要的业务能力和具体类；
- 稳定的命令、查询、结果、DTO 或 snapshot；
- 已批准且确有生产变种或策略意义的接口。

禁止 public surface 暴露：

- 内部字段、可变集合、cache、Repository 或仅供内部使用的实现类型；
- 仅供断言使用的中间状态；
- 测试专用 API 或成员。

新增或扩大 public API 前判断：

1. 是否存在真实的生产调用方？
2. 是否表达明确业务能力，而不是实现步骤？
3. 现有契约是否已经能够完成该行为？
4. 是否会暴露内部状态，或只为测试而存在？

如果 API 只为测试方便，拒绝新增并改用允许的验证方式。只为真实生产调用方增加必要的最小业务契约。

### 交付完整性

禁止提交：

- `TODO`、`deferred`、`placeholder`、`stub`、`not implemented`；
- 假成功返回或吞掉失败；
- “稍后接入”的孤立模块；
- 只横向创建类、没有可运行行为的骨架。

## 二、个人偏好的特殊模式

本节是有意采用的项目约束；与前面的通用默认值冲突时，以本节为准，尤其是 View、Context 和接口规则。

### 游戏开发边界

#### 分离 Domain 语义与引擎语义

- 不要把引擎 Entity/Component 或 ECS Component 直接等同于 DDD Entity、Aggregate 或 Value Object。根据身份、不变量、所有权和生命周期确定 DDD 角色。
- 把玩法不变量保留在纯领域代码中。让 View wrapper、帧回调、输入处理器、动画事件、RPC handler 和场景脚本把引擎事件转换为 Application command 或 Domain 行为。

#### 建模运行时输入与引擎服务

- 把 `deltaTime`、输入命令、目标 ID 和技能请求等逐帧或单次命令值作为 method/command 输入传递，不要把瞬时输入变成全局 Context 状态。
- 当玩法结果依赖时间、随机数、物理查询、寻路、资源查找、网络或平台服务时，把它们放入合适的 Context。已有生产抽象则复用；不得为测试新建抽象。

#### 持久化与性能

- 通过 factory 或 Aggregate 行为从存档数据重建模型，不要依靠 public setter 把持久化 DTO 直接变成可变领域模型。
- 在热路径中兼顾性能但不要破坏封装。优先使用所有权安全的操作、稳定 ID、只读视图或预分配结果缓冲区，不要暴露可变集合。

#### Domain 主导的 View Wrapper

该模式用于场景和战斗中的运行时 Domain Object。不要把该模式自动套用到背包、经济、存档数据等非视觉 Aggregate。

- `Actor`、`Player`、`Enemy` 等运行时 Domain Object 必须是普通类，不继承引擎场景类型。
- 玩法需要时，由 Domain Object 持有并驱动窄化的具体 View wrapper；原生节点必须封装在 wrapper 的 private 内部，不得仅为测试抽取 View 接口。

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
- 不要为了测试暴露或替换 wrapper、原生节点。

### Context 模式与构造函数门禁

把 Context 视为稳定作用域内的强类型依赖集合和生命周期 owner。“全局”只表示在该作用域内共享，不是 static 或进程级。

#### Context 边界

- 按大架构层或游戏领域组织 Context，例如 `GameApplicationContext`、`CombatContext`、`PlayerContext`。
- 不同场景、对局、房间或玩家会话使用同一种 Context 类型的不同实例。
- 当一个设施被多个对象复用，或生命周期长于单个对象/单次调用时，把它放入 Context。例如 Repository、Service、Gateway、Clock、随机数/ID 生成器、EventBus、物理/寻路查询、资源服务、网络 Gateway、配置源和资源注册表。
- 活跃 Entity、当前 command、逐帧状态和对象专属配置必须留在 Context 外。
- 不要为单个 Handler 创建微型 Context，也不要仅为了缩短一个构造函数创建 Context。

#### 构造函数门禁

强制分类每个构造函数参数：

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

如果无法说明某个额外参数为何是实例专属，就把它移入合适的 Context。一次性输入通过方法或 command 传递，不保存在构造函数依赖中。

#### Context 设计

- Context 使用普通类：private field 持有 system，public 只读属性提供访问。
- Context 负责作用域内的组装，以及有序的 `Initialize`、`Update`、`Destroy`。允许空构造函数或稳定的作用域配置。
- 禁止 `Get<T>()`、字符串 key、字典查找和运行时注册；依赖必须是可见的强类型成员。
- 禁止在 Context 中存放活跃 Entity、command、任意玩法数据或 use case 逻辑。
- Domain Context 不得暴露数据库 client、HTTP client、原生引擎对象或其他 Infrastructure 实现。
- 禁止创建跨系统 `AppContext`/`GlobalContext`；Context 过大时按领域、层或生命周期拆分。

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

### 只有真实生产变种才抽接口

只有产品确实需要多个生产实现时，才新增 interface、port 或 provider。单一实现直接使用具体类；“未来灵活性”和“方便测试”都不是充分理由。delegate 只用于真实生产回调或事件，绝不能为了测试而镜像一个类。

- 判断标准：该类型是否会有 ≥2 个真实生产实现？没有 → 具体类。
- working directory、ID、路径、阈值等稳定配置直接传值或 Value Object；不得包装成 Provider 或无参数函数。
- 若单元测试必须依赖一个没有真实生产变种的可替换抽象，就不要写该单元测试。
- 禁止擅自新增未经授权的 interface、port、delegate 或 provider。

### 语言专项检查

#### TypeScript

- 优先使用 ECMAScript `#private` 或项目既有的 `private` 约定；
- 对外 DTO 使用 `Readonly` 和只读集合；
- 只从 public barrel 导出契约，不导出 internal 实现或 Domain 内部类型；
- 不在 public Domain 契约中暴露引擎/运行时对象；在模块边界进行适配。

#### C#

- 领域状态使用 private field 和受控的 `private set`；
- 引擎支持时使用 `[SerializeField] private` 完成编辑器绑定；不要仅为 Inspector 访问把玩法状态设为 public。

## 三、测试与验证

### 自动化测试只允许叶子单元

禁止使用 TDD 或 test-first；先实现行为。之后只允许为确定性、引擎无关的叶子逻辑编写自动化测试；被测对象不得涉及 Context 接线、View、原生节点、视觉行为或引擎生命周期。允许的例子包括值对象、公式、调度器、计数器，以及小型集合或数学工具。

- 只通过单元既有的 public 行为测试。
- 禁止访问 private 状态、扩大可见性，以及使用 reflection、`InternalsVisibleTo`、`as any`、property descriptor 或内部集合断言。
- 禁止为测试新增 `ForTest`/`TestOnly` 成员、interface、delegate、provider、proxy、observer、setter、hook、reset 方法、fake 或第二套入口。
- 禁止仅为了在测试中代理所有行为，把一个类替换成镜像其方法的 delegate 或 interface。
- 禁止为了让非叶子关注点可单元测试而修改生产架构。
- 未经用户明确授权，禁止修改既有预期结果。若测试疑似错误或与产品行为冲突，只报告冲突，不得自行改写测试。

### 禁止自动化集成测试

禁止创建自动化 integration、acceptance、end-to-end、headless engine、scene 或 visual regression test。“集成”在本技能中是一种验证分类，不代表编写测试代码。

Context、Bootstrap、GameFlow、View wrapper、原生节点、场景装配、资源加载、动画、特效、UI、骨骼挂点、引擎生命周期和多 system 接线，必须通过正常游戏入口运行真实引擎验证。根据实际行为观察渲染结果与交互，并使用截图或录像、场景树检查、Debug Draw、运行时状态和引擎日志。

禁止 fake 视觉或节点承载类型。禁止为了自动化集成行为而创建 test runner、测试场景、测试专用 Context、fixture 或可注入替换结构。
