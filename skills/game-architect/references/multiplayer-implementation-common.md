# Common Multiplayer Infrastructure Playbook

Shared implementation playbook for infrastructure used by room, encounter, world, and backend/platform server designs.

Use `multiplayer-server-architecture.md` for architecture decisions. Use runtime-specific playbooks for room, encounter, and world logic. This document covers common infrastructure boundaries, not gameplay rules.

---

## 1. Purpose And Fit

Use this playbook when deciding how shared server infrastructure should be implemented without hiding gameplay authority inside it.

Common infrastructure is grouped by component family:

| Family | Includes | Main Question |
|:---|:---|:---|
| **Entry And Session** | auth, gateway, connector, session, heartbeat, route dispatch | How does traffic enter safely and reach the correct owner? |
| **Application And Data** | API controllers, application services, repositories, DB, cache | How do request handlers use durable data without owning game rules? |
| **Coordination** | discovery, owner location, message bus, outbox, async consumers | How do services find owners and coordinate after durable decisions? |
| **Operations And Safety** | config, secrets, observability, admin, health, abuse protection | How does the server stay operable, debuggable, and safe under public traffic? |

Not every project needs these as separate processes. Small projects should combine them inside one deployable while keeping module boundaries clear.

---

## 2. Core Boundary Rule

Treat common components as infrastructure boundaries, not as places to hide gameplay authority.

Hard rules:

- auth authenticates identity; it does not run combat, room, encounter, or scene logic
- gateway routes and protects connections; it does not own gameplay state
- API controllers validate request shape and call application services; they do not become the domain layer
- persistence stores state; it does not decide game outcomes
- cache accelerates or coordinates; correctness must survive cache miss or outage unless cache is explicitly authoritative
- discovery answers where an owner lives; the owner still validates every request
- message bus is for async follow-up after durable decisions, not for hiding immediate authority

If gameplay rules leak into infrastructure components, the architecture is drifting.

---

## 3. Entry And Session

Use this family for login, token verification, connection lifecycle, heartbeat, reconnect metadata, packet decode, and route dispatch.

| Object | Owns | Talks To | Must Not Do |
|:---|:---|:---|:---|
| `AuthApplicationService` | login, refresh, logout, auth orchestration | credential verifier, account repository, token issuer, audit logger | run gameplay rules |
| `TokenIssuer` / `TokenVerifier` | access token, refresh token, resume token issue/verify | auth service, gateway, API middleware | call DB on every packet unless revocation requires it |
| `GatewayServer` | connectors, request pipeline, heartbeat loop | session manager, packet codec, route dispatcher | own room, encounter, or scene state |
| `ConnectionSession` | connection ID, player ID, heartbeat, reconnect metadata | session manager, gateway | become durable player profile |
| `SessionManager` | session bind, rebind, invalidation, timeout | token verifier, gateway, route dispatcher | decide gameplay ownership |
| `PacketDecoder` / `PacketEncoder` | envelope decode/encode, payload size checks | gateway, protocol layer | let malformed packets reach business handlers |
| `RouteDispatcher` | route request to current owner or backend service | owner locator, RPC connector, gateway | bypass owner validation |
| `ConnectionLimiter` | per-IP/account quotas and send queue limits | gateway, security guard, metrics | allocate unbounded buffers per user |

### Entry Chain

1. connector accepts TCP, WebSocket, HTTP, or RPC request
2. packet/request size and shape are checked
3. token is verified and request context is built
4. session is created, rebound, or rejected
5. rate limit and overload policy run
6. route dispatcher resolves the target owner or service
7. owner still validates authority, state, and permissions

Rules:

- distinguish access token, refresh token, and resume token
- define multi-login policy: replace old session, allow parallel, or reject
- reconnect window and old-session invalidation must be explicit
- slow client policy must be explicit: drop, coalesce, compress, or disconnect

---

## 4. Application And Data

Use this family for stateless API entry, application operations, DB access, transactions, migrations, and caches.

| Object | Owns | Talks To | Must Not Do |
|:---|:---|:---|:---|
| `ApiController` | transport-facing request/response DTOs | auth/rate-limit middleware, application service | call raw DB or contain full domain rules |
| `ApplicationService` | one complete application operation | repositories, domain modules, cache, event publisher | hide runtime authority from room/encounter/scene owner |
| `Repository` | typed durable reads/writes | DB client, unit of work | expose raw storage details to controllers |
| `UnitOfWork` | transaction scope for one durable operation | repositories, outbox publisher | wrap remote service calls by habit |
| `DbClientManager` / `DbConnectionPool` | DB clients, pool config, timeouts, metrics | repositories, health checks | use default pool sizes without capacity reasoning |
| `MigrationRunner` | schema version check and safe migration entry | DB client, deploy/startup process | run large hot-path backfills during gameplay traffic |
| `CacheAdapter` | typed keys, TTL, serialization, fallback behavior | repositories, session/location services | store irreversible business writes only in cache |

### API And Write Chain

1. `ApiController` receives request DTO
2. middleware verifies auth, rate limit, request context, and stable error format
3. application service executes one use case
4. repositories read/write through `UnitOfWork` when durable consistency is needed
5. `UnitOfWork` commits
6. outbox/event publisher emits follow-up events only after durable success
7. controller returns response DTO with request ID when useful

Rules:

- keep handlers thin
- use transactions for durable consistency boundaries, not every request by habit
- keep transactions short and avoid remote calls inside DB transactions
- retry only idempotent writes or writes guarded by unique keys
- cache miss path must be correct, not only fast
- define read replica staleness before using replicas for gameplay-facing reads

---

## 5. Coordination

Use this family for finding owners, service instances, room/region locations, and async work that follows durable decisions.

| Object | Owns | Talks To | Must Not Do |
|:---|:---|:---|:---|
| `ServiceRegistry` | service instance list and health state | bootstrap, health reporter, owner locator | prove gameplay ownership by itself |
| `OwnerLocator` | current room, encounter, region, or service location lookup | registry/cache, gateway, routers | let routing code parse registry storage directly |
| `LocationRegistryWriter` | authoritative location update path | transfer coordinator, room/world owner | reorder owner handoff rules |
| `RegistrySyncJob` / `HealthReporter` | registration heartbeat and readiness | service registry, health checks | mark process alive as owner-ready without service checks |
| `EventPublisher` | domain event publish API | application services, outbox publisher | hide synchronous ownership-critical writes |
| `OutboxPublisher` | durable outbox flush to message bus | DB, queue, metrics | publish important events before durable commit |
| `QueueConsumerHost` | async consumer lifecycle | message bus, consumers, metrics | process messages without idempotency policy |

### Routing And Async Chains

Owner lookup:

1. gateway or API asks `OwnerLocator` for current owner by room ID, encounter ID, region ID, entity ID, or service key
2. locator returns target or stale/missing result
3. route dispatcher sends request or returns redirect/retry failure
4. owner validates it is still authoritative before mutation

Async follow-up:

1. application service completes durable write
2. outbox row or event record is committed
3. outbox publisher sends event to queue or bus
4. consumer handles event idempotently
5. retry/dead-letter policy records unresolved failures

Rules:

- stale location should trigger re-query, redirect, or owner-side rejection
- owner move/update must be ordered with handoff rules
- queue ordering guarantees must be documented per topic or stream
- use async events for follow-up work, not immediate authoritative answers

---

## 6. Operations And Safety

Use this family for config, secrets, logs, metrics, tracing, health, admin inspection, and abuse protection.

| Object | Owns | Talks To | Must Not Do |
|:---|:---|:---|:---|
| `ConfigLoader` / `ConfigValidator` | typed config load and startup validation | bootstrap, app host, secret provider | scatter magic numbers through handlers |
| `SecretProvider` | DB passwords, signing keys, external credentials | bootstrap, auth, DB clients | leak secrets into logs or normal config |
| `FeatureFlagProvider` | rollout switches and kill switches | application services, middleware | create permanent architecture forks |
| `RequestLogger` | structured request and business logs | gateway, API, runtime owners | log full sensitive payloads by default |
| `MetricsCollector` | rate, latency, error, dependency, runtime counters | gateway, DB/cache clients, runtimes | replace explicit health checks |
| `TraceContextPropagator` | request ID and trace propagation | connector, gateway, API, RPC clients | break trace across service boundaries |
| `AdminQueryService` | session, owner, room, encounter, region inspection | admin auth guard, session manager, owner locator | mutate runtime state without explicit admin command rules |
| `HealthCheckController` | readiness and liveness views | DB/cache clients, registry, app host | treat process alive as ready |
| `SecurityGuard` | rate limit, packet size, replay guard, admin auth | gateway/API middleware, audit logger | trust only official clients will call endpoints correctly |

### Protection And Observation Chain

1. connector creates request context and trace ID
2. payload guard rejects malformed or oversized input
3. IP/account rate limit runs
4. auth and replay/duplicate guard run for risky mutations
5. request logger records start
6. handler executes through owner/application service
7. metrics record latency, result code, dependency timings, and queue/pool pressure
8. request logger records end and errors with redaction

Minimum required signals:

- request rate, error rate, latency
- active connections and disconnect rate
- room, encounter, region, or instance count where relevant
- DB pool usage, wait time, slow queries
- cache hit rate and error rate
- queue depth, retry count, dead-letter count
- process CPU, memory, GC, restart count

Rules:

- readiness starts only after config, DB/cache dependencies, and required registries are ready
- admin endpoints require stronger auth and audit logs
- trace critical chains such as login, join, settlement, transfer, and durable reward commit
- secrets should not live in code or ordinary config files

---

## 7. Suggested Code Roots

Use code organization as a composition rule, not as one giant fixed tree.

```text
server/
  bootstrap/
  infra/
  persistence/
  api/
  services/
```

| Root | Use For |
|:---|:---|
| `bootstrap/` | startup, dependency building, config load, process host |
| `infra/` | auth, gateway, connector, discovery, messaging, observability, security |
| `persistence/` | DB, cache, repositories, migrations |
| `api/` | request/response controller layer, DTOs, middleware |
| `services/` | owned business or gameplay modules such as player, room, encounter, scene |

Placement rules:

- put `TokenIssuer` under `infra/auth/`, not `services/player/`
- put `DbConnectionPool` under `persistence/db/`, not controllers
- put `OwnerLocator` under `infra/discovery/`, not raw gateway routing code
- put `RequestLogger` under `infra/observability/`, not duplicated per service
- choose `api/application/` or `services/player/` for player operations based on whether the code is transport orchestration or domain authority

Dependency direction:

1. `bootstrap` wires everything
2. `api` and gateway entry use `infra`, `persistence`, and `services`
3. `services` use repositories and selected infra abstractions
4. `persistence` does not depend on `api`

If services depend on controller code, or repositories depend on gateway code, the organization is already wrong.

---

## 8. Minimal Build Order

Recommended order:

1. bootstrap with typed config and startup validation
2. persistence baseline with one durable read/write path
3. auth, connector, gateway/API entry, and session bind
4. basic request chain with stable error codes and request IDs
5. logs, metrics, health checks, and minimum admin inspection
6. route to one runtime owner or backend service
7. cache/discovery only when hot lookup or multi-owner routing exists
8. async messaging only after a durable producer path exists
9. abuse protection and operational tooling before public scale

Do not add queue, distributed registry, or advanced security plumbing before one authenticated request can go end to end with logging and durable storage.

---

## 9. Review Checklist

Before calling common infrastructure ready, verify:

- entry/session, application/data, coordination, and operations/safety boundaries are distinct
- no gameplay rules are hidden inside infrastructure components
- gateway rejects malformed, oversized, unauthenticated, and overloaded traffic
- DB transaction, timeout, retry, pool, and migration rules are declared
- cache correctness does not depend on perfect hit rate
- stale discovery and owner-move behavior are defined
- async events are published after durable success and consumed idempotently
- logs, metrics, traces, health checks, and admin inspection cover critical request chains
- secrets, admin endpoints, and abuse controls have explicit protection rules
