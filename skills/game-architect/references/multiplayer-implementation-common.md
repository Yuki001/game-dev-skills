# Common Server Components And Services Build Playbook

Build guide for shared server infrastructure that appears across most online game backends and multiplayer runtimes.

This document is independent of room server, encounter server, and world server topology. It covers common components such as auth, gateway, connector, database access, cache, service discovery, messaging, and observability.

Use this document together with:

- `multiplayer-server-architecture.md` for ownership and process topology
- `multiplayer-protocol.md` for message design, reconnect, and delivery rules
- scenario playbooks for room, encounter, or world runtime decisions

---

## 1. Scope

Use this document when the question is:

- what common services should exist in most game server stacks
- what responsibilities belong to auth, gateway, connector, db, cache, and discovery
- how to build shared infrastructure without mixing it into gameplay runtime code
- what default operational rules should exist for connection handling, persistence, and observability

This document is about reusable server infrastructure, not gameplay rules.

---

## 2. Core Principle

Treat common server components as infrastructure boundaries, not as places to hide game logic.

Hard rules:

- auth authenticates identity; it does not run combat or room logic
- gateway manages connections and routing; it does not own gameplay state
- database layer persists and reads state; it does not decide game rules
- cache accelerates reads and coordination; it is not the source of truth unless explicitly designed that way
- service discovery tells you where a service or owner is; it does not replace ownership rules

If gameplay rules are leaking into infra components, the architecture is drifting.

---

## 3. Common Component Map

Typical shared components:

- **Auth Service**: identity validation, login, token/session issuance
- **Gateway**: external connection entry, protocol decode, session bind, routing
- **Connector**: internal or external network endpoint for a specific transport or service boundary
- **API Service**: stateless request/response entry for backend features
- **Player Service**: durable player data authority
- **DB Layer**: repository, connection pool, transaction boundary, persistence policy
- **Cache Layer**: hot data cache, distributed lock, ephemeral coordination
- **Service Discovery / Registry**: where a service, room, region, or owner currently lives
- **Message Bus / Queue**: async cross-service events and work dispatch
- **Observability Stack**: logs, metrics, tracing, alerts, admin inspection
- **Config / Secret Service**: environment configuration, rollout controls, credential management

Not every project needs all of them as separate processes. Most small projects start with several of these combined in one process.

---
## 4. Auth Service

Use a concrete auth module like this:

```text
server/
  infra/
    auth/
      AuthController
      AuthApplicationService
      AccountCredentialVerifier
      PlatformTicketVerifier
      BanPolicyService
      TokenIssuer
      TokenVerifier
      RefreshTokenStore
      LoginAuditLogger
  persistence/
    repository/
      AccountRepository
```

### Main Class Responsibilities

- `AuthController`: request entry for login, refresh, logout, and token verify
- `AuthApplicationService`: orchestrates one complete auth operation
- `AccountCredentialVerifier`: username/password or custom account verification
- `PlatformTicketVerifier`: Apple/Google/Steam/platform token verification
- `AccountRepository`: load account record, auth binding, status flags
- `BanPolicyService`: check banned, muted, region-blocked, version-blocked state
- `TokenIssuer`: create access token, refresh token, resume token
- `TokenVerifier`: validate token signature, expiry, audience, environment
- `RefreshTokenStore`: persist or revoke refresh-capable credentials if the design uses them
- `LoginAuditLogger`: audit success/fail login events

### Main Object Relations

- `AuthController` depends on `AuthApplicationService`
- `AuthApplicationService` depends on one verifier, `AccountRepository`, `BanPolicyService`, and `TokenIssuer`
- `GatewayServer` and `ApiServer` depend on `TokenVerifier`
- `RefreshTokenStore` is used only by refresh/logout flows, not every request

### Reference Request Models

```text
LoginRequest
  account
  password or platformTicket
  clientVersion
  deviceId
  platform

LoginResult
  playerId
  accountId
  accessToken
  refreshToken
  resumeToken
  accessExpireAt
```

### Concrete Login Chain

1. `AuthController.Login()` receives `LoginRequest`.
2. `AuthApplicationService.Login()` chooses `AccountCredentialVerifier` or `PlatformTicketVerifier`.
3. verifier resolves `accountId`.
4. `AccountRepository.GetAuthAccount()` loads account status and bound `playerId`.
5. `BanPolicyService.CheckLoginAllowed()` validates version, ban, region, and environment rules.
6. `TokenIssuer.CreateAccessToken()` issues short-lived access token.
7. `TokenIssuer.CreateResumeToken()` issues reconnect or resume credential if needed.
8. `RefreshTokenStore.Save()` persists refresh token metadata if refresh flow exists.
9. `LoginAuditLogger.WriteSuccess()` records login audit.
10. `AuthController` returns `LoginResult`.

### Concrete Verify Chain

Use token verification like this in gateway or API:

1. `TokenVerifier.VerifyAccessToken()` validates signature and expiry.
2. result returns `playerId`, `accountId`, `sessionScope`, and token metadata.
3. caller creates or binds runtime session.

Do not call `AccountRepository` on every packet just to verify an access token unless forced logout or revocation design requires it.

### Concrete Method Split

```text
AuthController.Login()
AuthController.Refresh()
AuthController.Logout()
AuthApplicationService.Login()
AuthApplicationService.RefreshToken()
AccountCredentialVerifier.Verify()
PlatformTicketVerifier.Verify()
BanPolicyService.CheckLoginAllowed()
TokenIssuer.CreateAccessToken()
TokenVerifier.VerifyAccessToken()
```

### Build Rules

- keep token payload limited to identity and routing claims
- distinguish access token, refresh token, and resume token clearly
- put expiry, audience, environment, and version scope into token verification rules
- keep auth state changes auditable
- keep auth errors machine-readable and stable

### Failure Rules

- auth outage should fail login, not corrupt active sessions
- token verification should be local and cheap for hot paths
- refresh token revocation policy must be explicit if forced logout matters
- repeated login should have a defined multi-login rule: replace old session, allow parallel, or reject

---

## 5. Gateway And Connector

### Gateway Responsibilities

- accept client connections
- decode protocol and basic envelope
- authenticate and bind session
- maintain heartbeat and timeout state
- rate limit and reject malformed traffic
- route requests to the correct owner or backend service

### Reference Class Split

Use a gateway structure like this:

```text
server/
  infra/
    gateway/
      GatewayServer
      ConnectionSession
      SessionManager
      HeartbeatMonitor
      RouteDispatcher
      PacketDecoder
      PacketEncoder
      ConnectionLimiter
      GatewayAdminService
    connector/
      WsConnector
      TcpConnector
      HttpConnector
      RpcConnector
  infra/
    discovery/
      OwnerLocator
```

- `GatewayServer`: top-level server runtime, owns connectors and request pipeline
- `ConnectionSession`: one live connection, stores `sessionId`, `playerId`, `connectionId`, heartbeat state
- `SessionManager`: create/bind/rebind/remove session objects
- `PacketDecoder`: envelope decode and payload validation
- `RouteDispatcher`: route to `PlayerService`, `RoomService`, `EncounterService`, or `SceneService`
- `HeartbeatMonitor`: ping/pong and timeout tracking
- `ConnectionLimiter`: per-ip, per-account, and send-queue protection
- `GatewayAdminService`: inspect and close sessions

### Concrete Object Relations

- `GatewayServer` -> many `Connector`
- `GatewayServer` -> one `SessionManager`
- `SessionManager` -> many `ConnectionSession`
- `GatewayServer` -> one `PacketDecoder` and one `PacketEncoder`
- `RouteDispatcher` -> `OwnerLocator` + `RpcConnector`
- `HeartbeatMonitor` reads `ConnectionSession` state and notifies `SessionManager`

### Connector Responsibilities

Use `connector` as the network-facing endpoint abstraction for a transport or internal service boundary.

Typical connector types:

- client-facing tcp/ws connector
- http/grpc api connector
- internal service rpc connector
- broker or queue consumer connector

### Hard Rules

- gateway should not own gameplay authority
- connector code should stay close to transport concerns
- routing decision and business execution should remain separate
- malformed or oversized packets should be rejected before business handlers

### Session Rules

- one active session should map to one authenticated identity unless multi-login is explicitly supported
- session should carry player id, connection id, current owner location, and reconnect metadata
- reconnect window must be explicit
- old session invalidation policy must be explicit

### Backpressure Rules

- every connection needs send-queue limits
- slow client policy must be defined: drop packet, compress, coalesce, or disconnect
- gateway should protect backend services from connection floods
- broadcast fan-out should not allocate unbounded buffers per user

### Build Order

1. raw connection accept and close
2. auth and session bind
3. protocol decode and request validation
4. routing to service or owner
5. heartbeat and reconnect
6. rate limit and overload protection

---

## 6. API Service

### Use For

- login-adjacent endpoints
- inventory, quests, shop, mail, social systems
- encounter or battle APIs when the runtime is RPC-first
- admin and ops endpoints

### Reference Class Split

Add API modules like this when the project needs a stateless request/response entry:

```text
server/
  api/
    controller/
      PlayerController
      InventoryController
      MailController
      AdminController
    application/
      PlayerApplicationService
      InventoryApplicationService
      MailApplicationService
    dto/
      request/
      response/
    middleware/
      ApiAuthMiddleware
      ApiRateLimitMiddleware
      RequestContextMiddleware
```

- `PlayerController` / `InventoryController`: transport-facing request handlers
- `PlayerApplicationService` / `InventoryApplicationService`: one complete application operation
- `dto/request` and `dto/response`: transport contract objects
- `ApiAuthMiddleware`: token verification at entry
- `ApiRateLimitMiddleware`: rate limit and overload protection
- `RequestContextMiddleware`: attach trace id, request id, player id, locale, version

### Concrete Object Relations

- controller depends on one application service
- middleware runs before controller
- application service depends on repository, cache, and owned domain services
- controller should not depend on raw DB client or queue client directly

### Concrete Request Chain

1. `HttpConnector` receives request.
2. `ApiAuthMiddleware` verifies token.
3. `ApiRateLimitMiddleware` checks quota.
4. `RequestContextMiddleware` builds request context.
5. controller validates request DTO.
6. application service executes use case.
7. controller returns response DTO.

### Build Rules

- keep handlers thin
- validation, auth, and rate limiting happen at entry
- business logic belongs in domain modules or owned services
- responses should include stable error codes and request ids when useful

Do not let API controllers become the real game logic layer.

---

## 7. Database Layer

### Responsibilities

- own DB connectivity and connection pools
- expose repositories or data-access modules
- define transaction boundaries
- enforce timeout, retry, and write policy
- support schema evolution and migration

### Reference Class Split

Use a DB layer like this:

```text
server/
  persistence/
    db/
      DbClientManager
      DbConnectionPool
      UnitOfWork
      MigrationRunner
      SqlHealthProbe
    repository/
      PlayerRepository
      MailRepository
      AuditLogRepository
```

- `DbClientManager`: owns named database clients and pool configuration
- `DbConnectionPool`: wraps driver pool settings and metrics
- `UnitOfWork`: transaction scope for one application operation
- `PlayerRepository`, `MailRepository`, `AuditLogRepository`: typed repositories
- `MigrationRunner`: startup migration and schema version checks
- `SqlHealthProbe`: readiness/liveness probe for DB availability

### Concrete Call Pattern

Preferred write flow:

1. application service starts `UnitOfWork`
2. repository reads and writes through `DbClientManager`
3. `UnitOfWork` commits
4. `OutboxPublisher` publishes follow-up events if needed

Never let transport handler call raw SQL directly.

### Connection Pool Rules

- pool size must be explicit, not default magic
- pool size should reflect DB capacity, not just application thread count
- set acquire timeout and query timeout separately
- long-running queries must not occupy the whole pool
- monitor pool saturation, wait time, error rate, and slow queries

### Transaction Rules

- use transactions for durable consistency boundaries, not for every request by habit
- keep transactions short
- avoid remote service calls inside DB transactions
- write idempotent settlement and completion records with stable keys

### Read/Write Rules

- player and economy writes should be explicit and auditable
- avoid hidden writes in read paths
- define whether read replicas are allowed and what staleness is acceptable
- separate hot operational queries from analytical/reporting queries

### Schema And Migration Rules

- schema changes need forward-compatible rollout
- do not repurpose existing columns for new meanings
- migrations must be reversible or operationally safe
- large backfills should not run in the same path as hot gameplay traffic

### Failure Rules

- DB timeout must surface as explicit service failure, not silent success
- retry only idempotent writes or writes guarded by unique keys
- connection pool exhaustion must trigger alerting and traffic protection

---

## 8. Cache Layer

### Use For

- hot player/session reads
- room or region location lookup
- reconnect tokens and short-lived reservation data
- rate limit counters
- distributed locks only when truly necessary

### Reference Class Split

Use typed cache wrappers instead of generic stringly-typed access everywhere:

```text
server/
  persistence/
    cache/
      CacheClient
      SessionCache
      PlayerSnapshotCache
      OwnerLocationCache
      RateLimitCache
      ReservationCache
```

- `SessionCache`
- `PlayerSnapshotCache`
- `OwnerLocationCache`
- `RateLimitCache`
- `ReservationCache`

Make each wrapper own key format, ttl, serialization, and fallback behavior.

### Hard Rules

- cache is not source of truth unless designed that way
- every cached item needs ttl or invalidation policy
- cache miss path must be correct, not only fast path
- do not put irreversible business writes only in cache

### Good Defaults

- use cache-aside for hot reads
- use short ttl for location or session hints
- use explicit invalidation after durable writes when needed
- keep payload small and serialization cheap

### Failure Rules

- cache outage should degrade performance first, not correctness
- if cache is used for coordination, failure mode must be documented
- distributed lock failure should fail safe, not create double settlement

---

## 9. Service Discovery And Registry

### Use For

- find which node owns a room
- find which region owns a player or entity
- locate service instances for internal calls
- track live process presence and health

### Reference Class Split

```text
server/
  infra/
    discovery/
      ServiceRegistry
      OwnerLocator
      LocationRegistryWriter
      RegistrySyncJob
      HealthReporter
```

- `ServiceRegistry`: service instance list and health state
- `OwnerLocator`: room, encounter, or region current owner lookup
- `LocationRegistryWriter`: authoritative location update path
- `RegistrySyncJob`: refresh or heartbeat registration

Use `OwnerLocator` from routing code. Do not let routing code parse registry storage directly.

### Hard Rules

- discovery answers location questions; it does not create authority
- the owner must still validate requests it receives
- stale registry entries are expected and must be handled

### Good Defaults

- small system: static config or simple registry
- dynamic multi-node system: central registry or shared discovery backend
- ownership-heavy system: dedicated location registry for rooms, players, or regions

### Failure Rules

- stale location should trigger re-query or redirect, not blind failure loops
- owner move/update must be ordered with handoff rules
- health checks must distinguish process alive from service actually ready

---

## 10. Message Bus And Async Work

### Use For

- non-blocking domain events
- settlement follow-up work
- analytics and audit pipelines
- email, mail, notification, and out-of-band jobs

### Reference Class Split

```text
server/
  infra/
    messaging/
      EventPublisher
      OutboxPublisher
      QueueConsumerHost
      SettlementRetryConsumer
      AuditEventConsumer
```

- `EventPublisher`: publish domain events from application layer
- `OutboxPublisher`: flush durable outbox rows to message bus
- `QueueConsumerHost`: host process for async consumers
- `SettlementRetryConsumer`: retry terminal writes or notifications
- `AuditEventConsumer`: write analytics or audit sinks

### Non-Use Cases

- do not hide synchronous ownership boundaries behind an event bus
- do not use async queue when caller needs immediate authoritative answer

### Build Rules

- message schema must be versioned
- every consumer needs idempotency rules
- retry and dead-letter policy must be explicit
- ordering guarantees must be documented per topic or stream

### Good Defaults

- synchronous call for ownership-critical write
- async event only after durable success
- outbox pattern for important cross-service event publication

---

## 11. Config, Secrets, And Feature Flags

### Config Rules

### Reference Class Split

Add config-related modules like this when the project has multiple environments, runtime flags, or operational tuning:

```text
server/
  bootstrap/
    ConfigLoader
    ConfigValidator
  infra/
    config/
      ServerConfig
      DbConfig
      GatewayConfig
      FeatureFlagProvider
      SecretProvider
      RuntimeConfigRefresher
```

- `ConfigLoader`: load config files, env vars, and startup arguments
- `ConfigValidator`: fail fast on invalid or incomplete startup config
- `ServerConfig` / `DbConfig` / `GatewayConfig`: typed config objects
- `FeatureFlagProvider`: runtime read for rollout switches
- `SecretProvider`: access tokens, DB passwords, signing keys
- `RuntimeConfigRefresher`: refresh safe runtime config where supported

### Concrete Object Relations

- `AppHost` depends on `ConfigLoader` and `ConfigValidator` during startup
- services depend on typed config objects, not on raw global maps
- `FeatureFlagProvider` is read by application services or middleware
- `SecretProvider` is used by bootstrap and sensitive infra modules only

### Concrete Startup Chain

1. `ConfigLoader` loads base config and environment overrides.
2. `ConfigValidator` validates required keys and value ranges.
3. `SecretProvider` resolves secret values.
4. `AppHost` constructs DB, gateway, cache, and service dependencies from typed config.
5. readiness starts only after config validation succeeds.

- separate static config from runtime-editable config
- define environment-specific config explicitly
- validate config on startup
- do not scatter magic numbers across handlers

### Secret Rules

- secrets should not live in code or normal config files
- rotation policy must be possible without code rewrite
- access should be least-privilege

### Feature Flag Rules

- use flags for rollout and kill switches, not for permanent architecture forks
- flag ownership and cleanup policy must be explicit

---

## 12. Observability And Operations

### Minimum Required Signals

- request rate, error rate, latency
- active connections and disconnect rate
- room/encounter/region count and occupancy
- DB pool usage and slow queries
- cache hit rate and error rate
- queue depth and retry count
- process cpu, memory, gc, and restart count

### Reference Utility Classes

```text
server/
  infra/
    observability/
      RequestLogger
      MetricsCollector
      TraceContextPropagator
      SlowQueryLogger
      AdminQueryService
      HealthCheckController
```

- `RequestLogger`
- `MetricsCollector`
- `TraceContextPropagator`
- `SlowQueryLogger`
- `AdminQueryService`
- `HealthCheckController`

### Suggested Module Layout

Add observability modules like this when the project reaches shared-service operation stage:

```text
server/
  infra/
    observability/
      logging/
        RequestLogger
        SecurityEventLogger
        SlowQueryLogger
      metrics/
        MetricsCollector
        GatewayMetrics
        DbMetrics
        CacheMetrics
      tracing/
        TraceContextPropagator
        TraceSpanFactory
      admin/
        AdminQueryService
        RuntimeInspector
      health/
        HealthCheckController
        ReadinessProbe
        LivenessProbe
```

### Concrete Object Relations

- `GatewayServer`, controllers, and application services emit metrics through `MetricsCollector`
- DB and cache clients report pool and error signals through `DbMetrics` and `CacheMetrics`
- `TraceContextPropagator` attaches trace ids to request context before business handlers run
- `AdminQueryService` reads from session manager, owner locator, repositories, and runtime inspectors
- `HealthCheckController` queries `ReadinessProbe` and `LivenessProbe`

### Concrete Observation Chain

Use a real request instrumentation chain like this:

1. connector creates request context and trace id
2. `TraceContextPropagator` attaches trace metadata
3. `RequestLogger` records request start
4. business handler executes
5. `MetricsCollector` records latency, result code, and dependency timings
6. `RequestLogger` records request end
7. if DB is slow, `SlowQueryLogger` records query warning

### Concrete Admin Query Chain

1. admin request enters `AdminQueryService`
2. service checks `AdminAuthGuard`
3. service queries `SessionManager`, `OwnerLocator`, and target runtime inspector
4. service returns one inspection payload such as session info, room info, encounter info, or region ownership

### Logging Rules

- log with request id, player id, room or encounter id, and node id when available
- separate business warnings from infrastructure errors
- avoid logging full payloads by default on hot paths
- sensitive data must be redacted

### Tracing Rules

- trace critical cross-service chains such as login, join, settlement, and transfer
- trace ids should flow across gateway, owner service, db, and queue publish paths

### Admin Tools

Strongly recommended:

- session lookup
- room or encounter inspection
- player state inspection
- location lookup
- forced disconnect or room close
- replay or audit lookup when available

---

## 13. Security And Abuse Protection

Minimum baseline:

- per-ip and per-account rate limiting
- payload size limits
- malformed packet rejection
- replay or duplicate request protection where needed
- auth expiry and signature validation
- admin endpoint isolation

### Reference Class Split

Add security modules like this when the server is exposed to public traffic:

```text
server/
  infra/
    security/
      IpRateLimiter
      AccountRateLimiter
      PacketSizeGuard
      ReplayProtectionService
      AdminAuthGuard
      SignatureValidator
      AbuseAuditLogger
```

- `IpRateLimiter`: connection and request quota by IP
- `AccountRateLimiter`: quota by account or player id
- `PacketSizeGuard`: payload size and malformed packet rejection
- `ReplayProtectionService`: reject duplicate or replayed high-risk requests
- `AdminAuthGuard`: stronger auth for admin endpoints
- `SignatureValidator`: signature, nonce, timestamp validation where required
- `AbuseAuditLogger`: security event logging

### Concrete Object Relations

- gateway and API middleware depend on rate limiters and packet guards
- high-risk mutation handlers depend on `ReplayProtectionService`
- admin controllers depend on `AdminAuthGuard`
- all security incidents should flow into `AbuseAuditLogger`

### Concrete Protection Chain

1. connector receives packet or request.
2. `PacketSizeGuard` rejects malformed or oversized payload.
3. `IpRateLimiter` checks source quota.
4. `AccountRateLimiter` checks authenticated identity quota if available.
5. `SignatureValidator` verifies signed requests where needed.
6. `ReplayProtectionService` rejects duplicate mutation token or nonce.
7. handler executes only after all checks pass.

Never assume only game clients will call your endpoints correctly.

---

## 14. Code Organization

Use code organization as a composition rule, not as one giant fixed tree.

### Composition Pattern

When a project adds one common component, place it in one of these roots:

```text
server/
  bootstrap/
  infra/
  persistence/
  api/
  services/
```

Use the roots like this:

- `bootstrap/`: startup, dependency building, config load, process host
- `infra/`: auth, gateway, connector, discovery, messaging, observability, security
- `persistence/`: db, cache, repositories, migration
- `api/`: request/response controller layer and middleware
- `services/`: owned business or gameplay modules such as player, room, encounter, scene

### Concrete Placement Rules

- add `TokenIssuer` under `infra/auth/`, not under `services/player/`
- add `DbConnectionPool` under `persistence/db/`, not inside repository or controller folders
- add `OwnerLocator` under `infra/discovery/`, not inside gateway routing code
- add `RequestLogger` under `infra/observability/`, not duplicated per service
- add `InventoryApplicationService` under `api/application/` or `services/player/` depending on whether it is transport orchestration or owned domain logic

### Concrete Dependency Direction

Keep dependencies one-way:

1. `bootstrap` can depend on everything needed for startup wiring
2. `infra` can depend on config and low-level utilities
3. `api` can depend on `infra`, `persistence`, and `services`
4. `services` can depend on `persistence` and selected `infra` abstractions
5. `persistence` should not depend on `api`

If `services` depend on controller code, or repositories depend on gateway code, the organization is already wrong.

---

## 15. Concrete Integration Example

Use a real shared request chain like this for a normal player API:

1. `HttpConnector` accepts request.
2. `GatewayServer` or `ApiServer` creates request context and trace id.
3. `TokenVerifier` validates token.
4. `SessionManager` resolves player identity.
5. `ConnectionLimiter` or request limiter checks quota.
6. controller calls application service.
7. application service uses repositories and optional cache.
8. `UnitOfWork` commits.
9. `RequestLogger` writes structured log.
10. `MetricsCollector` records latency and result code.

If a document cannot be mapped onto a chain like this, it is still too abstract.

---

## 16. Build Order

Use a staged build order like this:

### Stage 1: Process Bootstrap

Add:

```text
bootstrap/
  AppHost
  ConfigLoader
  ConfigValidator
```

Goal:

- process can start with validated config
- readiness can fail fast on broken config

### Stage 2: Persistence Baseline

Add:

```text
persistence/
  db/
    DbClientManager
    DbConnectionPool
    MigrationRunner
  repository/
    PlayerRepository
```

Goal:

- one service can read and write durable state safely
- DB pool, timeout, and migration behavior are visible

### Stage 3: Auth And Session Entry

Add:

```text
infra/auth/
infra/gateway/
infra/connector/
```

Goal:

- client or API request can authenticate and bind session

### Stage 4: Basic Observability

Add:

```text
infra/observability/
  logging/
  metrics/
```

Goal:

- every critical request has logs and latency metrics

### Stage 5: Performance And Routing Helpers

Add:

```text
persistence/cache/
infra/discovery/
```

Goal:

- hot session or owner lookups stop hammering DB
- routing can find current owner or service location

### Stage 6: Async And Ops Tooling

Add:

```text
infra/messaging/
infra/observability/admin/
infra/security/
```

Goal:

- async follow-up work is decoupled
- admin inspection and abuse protection are available

### Build Order Rule

Do not add queue, distributed registry, or advanced security plumbing before one authenticated request can go end to end with logging and durable storage.

---

## 17. Review Checklist

Before calling the infrastructure design ready, verify:

- auth, gateway, db, cache, and discovery each have explicit boundaries
- no gameplay rules are hidden inside infra components
- db pool size, timeouts, and retry rules are declared
- cache correctness does not depend on perfect hit rate
- gateway backpressure and malformed traffic handling are defined
- discovery staleness and retry behavior are defined
- logs, metrics, and traces are present for critical request chains
