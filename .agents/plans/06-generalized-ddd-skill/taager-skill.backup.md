---
name: taager-backend-architecture
description: Use this skill whenever writing, organizing, reviewing, extending, or modifying backend code that should follow Taager's Domain-Driven Design + Clean Architecture + CQRS conventions ("How We Write Code" internal standard). Trigger this any time the user is scaffolding a new bounded context or module, adding a new use case/feature, changing behavior of existing backend code, deciding where a piece of logic belongs (domain vs application vs infrastructure), naming a class (Request/Query/Handler/Repository/Controller/Dao/Dbo/Gateway), designing an aggregate, or asking "where should this go" / "is this structured correctly" for a backend service. Also trigger for the concrete Kotlin + Spring Boot conventions this standard is implemented with: contract-first OpenAPI-generated APIs, hand-written converters between DTO/application/domain/DBO models, explicit native SQL queries, JPA Specifications as an alternative to native SQL for dynamic filters, Spring Data projections, DBO/DAO persistence, JPA cascade aggregate persistence, gateways wrapping Feign clients, authorization / access policies (Spring Security `@PreAuthorize` gating plus per-context `...ViewPolicy` services), and the MockK/kotest/Testcontainers testing tiers. Applies regardless of programming language — the core is a structural/naming convention, not a framework — but the Kotlin + Spring Boot notes describe how we build it at Taager. Even if the user doesn't say "DDD" or "Taager" explicitly, trigger whenever backend code organization, layering, or CQRS-style command/query separation is relevant.
---

# Taager Backend Architecture (DDD + Clean Architecture + CQRS)

This skill encodes Taager's standard for structuring backend services, based on the "How We Write Code" engineering series. It combines Domain-Driven Design (DDD), Clean Architecture, and CQRS. It is organized as: the core idea → a canonical folder tree → a directory of every artifact type (what it is, where it goes, how it's named) → accepted variations → known wrong ways you may encounter in real codebases.

The core rules are language-agnostic; **Kotlin + Spring Boot** notes describe how Taager services concretely implement them.

## How to apply this skill

Which rules win depends on what you're doing:

1. **Editing or adding a feature in an existing repo** → follow that repo's existing pattern, matched at the narrowest scope: file > package > module > context > service. Even where the repo deviates from the canonical rules below, mirror the surrounding code — consistency within a codebase beats abstract correctness.
2. **Creating a new repo, service, bounded context, or module from scratch** — or when the user explicitly asks for "the right way" — → follow the canonical rules below exactly.
3. **When you notice the repo's pattern deviates from canon and the canonical way is feasible for the change at hand** → **ask the user first** before departing from the repo's existing pattern. Never silently "fix" conventions as a side effect of a feature; never introduce a third pattern.

## The core idea

Every use case is either a **Command** (changes state) or a **Query** (reads state, changes nothing). This split happens at the top of every bounded context, before anything else — it's the first fork in the folder tree. It keeps write-side business rules out of read paths and vice versa.

1. **Split the system into bounded contexts.** Each sub-domain (e.g. `wallet`, `shipping`, `products`) is a top-level package — ideally an independently deployable service, but a folder in a monolith is fine. If it's unclear where a feature belongs, find the closest existing aggregate it touches; don't dump it in whichever context is open.
2. **Split each context into a command side, a query side, and (when both sides share persistence or models) a `common` module.**
3. **Layer each side: `domain` / `application` / `infrastructure`.** Dependencies always point inward: infrastructure → application → domain. Domain depends on nothing — no frameworks, no ORM, no HTTP clients. An ORM or HTTP import in a domain model means the code is in the wrong layer.
4. **The query side has no domain layer.** The domain layer exists to protect invariants when *changing* state; reads change nothing, so a query shapes data straight from infrastructure into response models. Corollary: **query code never imports command domain aggregates** — it works with its own application models and projections.

## Canonical folder tree

One bounded context, fully populated (`[/pg]`, `usecase[s]` etc. mark accepted variations — see below):

```
<context>/
├── command/                       # or commands/ — uniform per service
│   ├── domain/
│   │   ├── model[s]/              # AggregateRoot, Entities, write-side Value Objects
│   │   ├── contracts/             # ports: ...Repo(sitory), ...Gateway, ...Publisher
│   │   ├── events/                # domain events emitted by aggregates
│   │   ├── services/              # domain services (business logic spanning models)
│   │   └── exceptions/            # (optional) write-side-only exceptions
│   ├── application/
│   │   ├── usecase[s]/            # one class per use case, single execute()
│   │   ├── model[s]/              # ...Command / ...Request params + results
│   │   └── policy/                # (only if a command needs an access policy)
│   └── infrastructure/
│       ├── controllers/           # one controller per endpoint
│       ├── converters/            # or controllers/converters + repositories/converters
│       ├── repositories/          # ...RepoImpl implementing domain contracts
│       ├── gateways/              # ...GatewayImpl wrapping shared HTTP clients
│       ├── publishers/            # message-broker publishers (or producers/)
│       ├── listeners/             # event listeners (or consumers/)
│       ├── jobs/                  # scheduled jobs
│       └── config/                # side-specific framework config
├── query/                         # or queries/ — uniform per service
│   ├── application/               # ← no domain layer on the query side
│   │   ├── usecase[s]/
│   │   ├── model[s]/              # ...Query params + read models / result DTOs
│   │   ├── contracts/             # ports: ...QueryRepo(sitory)
│   │   └── policy/                # ...ViewPolicy (row-level access rules)
│   └── infrastructure/
│       ├── controllers/
│       ├── converters/            # or controllers/converters + repositories/converters
│       └── repositories/          # ...QueryRepoImpl
└── common/                        # shared kernel WITHIN the context
    ├── domain/
    │   └── model[s]/              # shared VOs, enums, statuses, ...Authorities
    ├── application/
    │   ├── services/              # services genuinely used by both sides
    │   ├── policy/                # (only if a policy is genuinely used by both sides)
    │   └── exceptions/            # error-code constants
    ├── exceptions/                # the context's domain exception hierarchy
    └── infrastructure/
        ├── controllers/           # ...ControllerExceptionHandler, filter parsers
        ├── gateways/              # (only if a gateway serves both sides)
        └── db/
            ├── dao[/pg]/          # Spring Data ...Dao interfaces
            │   └── queries/       # extracted native-SQL constants
            │       └── fragments/ # only for genuinely large composed queries
            ├── models[/pg]/       # ...Dbo JPA entities
            ├── projections/       # read projections (sibling of the DBOs)
            └── specifications/    # JPA Specifications for dynamic filters
```

Plus one **`sharedkernel/`** at the service root — code every context may depend on (see the artifact directory).

A **self-contained sub-module** (e.g. an `analytics/` reporting slice) is an allowed escape hatch: its own `application`/`domain`/`infrastructure`, no command/query split, deliberately isolated from the transactional model. It is not a license to skip layering elsewhere.

## Artifact directory — what goes where

### Use case
- **Location**: `<side>/application/usecase[s]/`, one class per use case with a single `execute()` method.
- **Naming**: verb-first names — `CreateShipment`, `ListShipments`. Bare verb-first is preferred (recommended for new repos), but a `...UseCase` suffix (`CreateShipmentUseCase`) is also acceptable and used in some services — follow the repo's existing pattern and stay consistent within a service. Event handlers are suffixed `...Handler` (`OrderConfirmedHandler`).
- Thin orchestration only: coordinate domain calls, control transactions. A business-rule `if` here belongs in the domain model instead.
- **Kotlin/Spring**: extend the shared base interfaces from `sharedkernel/application/BaseUseCases.kt` (`CommandUseCase`, `QueryUseCase`, `EventHandler`, …) when the service defines them.

### Application model (use-case params & results)
- **Location**: `<side>/application/model[s]/`.
- **Naming**: command inputs `...Command` or `...Request`; query inputs `...Query`; results `...Result` or a named read model (`ShipmentDetails`). Simple data classes, no business logic.

### Domain model (AggregateRoot / Entity / Value Object)
- **Location**: the write aggregate and its entities/VOs live in **`command/domain/model[s]/`** — this is where business rules and invariants go.
- `common/domain/model[s]/` holds **only** what both sides genuinely share: enums/statuses, simple VOs, `...Authorities`. Never park the whole aggregate in `common` — the query side can (and eventually will) reach it, breaking CQRS.
- Prefer validating factory methods on VOs (`MerchantId.of(...)`); keeping the raw constructor private is the common way to enforce that.
- **Watch for unbounded aggregates**: a root holding an ever-growing list (wallet with all its transactions) gets slow and can OOM. Flag it; consider a narrower boundary or event sourcing.

### Domain service
- **Location**: `command/domain/services/` — business logic that spans models but is still core domain (not orchestration).

### Domain event
- **Location**: **`command/domain/events/`** — events are emitted by aggregates, so they are domain artifacts. Not `application/events`, not `common/domain/events`.

### Contract / port
- **Command-side ports** (repositories guarding the aggregate, gateways, publishers): **`command/domain/contracts/`**.
- **Query-side ports**: **`query/application/contracts/`** (there is no query domain layer to hold them).
- Domain/application code depends only on the port, never on a concrete `...Impl`, `...Dao`, `...Dbo`, or HTTP client.

### Repository implementation
- **Location**: `<side>/infrastructure/repositories/`.
- **Naming**: port `...Repo` or `...Repository` (accepted variation); impl adds `Impl`. The name must distinguish command vs query impls when both exist — both **suffix** style (`ShipmentQueryRepoImpl`) and **prefix** style (`QueryShipmentRepositoryImpl`) are acceptable; pick one and stay consistent within the service.
- One repository per **aggregate root**, never per entity — children are loaded and saved through the root.
- **Kotlin/Spring**: the impl (`@Repository`) delegates to one or more Spring Data `...Dao` interfaces and maps DBO/projection ↔ model via the `to*` converters. Transactions live at this boundary, not in use cases.

### DAO
- **Location**: `common/infrastructure/db/dao[/pg]/` — shared by both sides (the query side normally has no `db` package of its own).
- **Kotlin/Spring**: `...Dao : JpaRepository` (plus `JpaSpecificationExecutor` when Specifications are used). Derived methods (`findBySku`) only for simple lookups, often with `@EntityGraph`.

### DBO (persistence entity)
- **Location**: `common/infrastructure/db/models[/pg]/`, class suffix `Dbo`.
- **Kotlin/Spring**: `@Entity` classes extending the shared base DBOs from `sharedkernel`; may use Hibernate features freely (`@NamedEntityGraph`, `@JdbcTypeCode`). The persistence representation only — the domain model has zero JPA imports.
- **Aggregate persistence via cascade**: relationships declare `cascade = [CascadeType.ALL]` (collections also `orphanRemoval = true`) so one `dao.save(rootDbo)` in a transaction persists the whole aggregate. Save the root, never children individually.

### Projection
- **Location**: sibling of the DBOs — `db/projections/` or `db/models[/pg]/projections/`. Never loose inside `dao/`.
- Read/query paths return projections (getter-per-column interfaces), not full entities. The `...QueryRepoImpl` maps projection → application model via `toApplication`.

### Native SQL query constants
- **Location**: `common/infrastructure/db/dao[/pg]/queries/`, as `const` holder classes.
- Prefer explicit `@Query(..., nativeQuery = true)` with hand-written SQL over ORM-generated queries or lazy-loading graphs — full control over what the DB actually runs.
- `queries/fragments/` (reusable CTE/sub-select composition) **only** for genuinely large queries built from many subqueries/filters — don't reach for fragments by default.

### JPA Specification
- **Location**: `common/infrastructure/db/specifications/`.
- **Scope**: an accepted alternative to native SQL **only** for list queries that are several *optional* equality/range/`IN` predicates on a single table — the impl collects predicates into a list, `cb.and(...)`, `dao.findAll(spec, pageable)`. Anything with joins, aggregation, or CTEs stays native SQL.

### Converter
- **Layer**: infrastructure only — never in `application/`, never in the domain.
- **Location**: flat `<side>/infrastructure/converters/` for small contexts; once a side has both edge-converters and persistence-converters, nest them next to their consumer: `controllers/converters/` and `repositories/converters/`. Both layouts are accepted — pick per module, don't mix within one.
- **Direction & naming**: hand-written and direction-specific — `toModel` (DTO → application model), `toDto` (application/domain → DTO), `toDomain` (DBO → domain), `toDbo` (domain → DBO), `toApplication` (DBO/projection → application read model). Prefer `to<Target>` names; avoid `toDTO` casing and reflection-based auto-mappers (MapStruct/ModelMapper) unless the module already commits to them.
- **Implementation style — loose**: two hand-written styles are both acceptable — (a) **extension functions** on the model being converted (`fun ProductDbo.toDomain(): Product`), and (b) a **mapper/converter class** with static or instance methods (`object ProductMapper { fun toDomain(dbo): Product }`, or a `@Component` converter). A bounded context may even use different styles on its two sides — e.g. a mapper class on the command side, extension functions on the query side. This is **tolerated but not recommended**: consistency within a context (ideally the whole service) is always preferred. When adding to existing code, match the surrounding style rather than introducing the other one.

### Controller
- **Granularity — two accepted shapes**: (a) **one controller per use case/endpoint** (`CreateShipmentController`, `ListShipmentsController`), or (b) **one controller grouping several related handlers/endpoints** for a resource (as in some services, e.g. a wallet service). The grouped shape is fine and often recommended when the endpoints are closely related; the per-endpoint shape suits contexts that keep one class per use case. Follow whichever the repo uses. Regardless of shape, a controller only converts + delegates (receive → convert in → call the use case → convert out) — no business logic.
- **Location**: `<side>/infrastructure/controllers/`.
- **Kotlin/Spring — contract-first**: the API is defined in `src/main/resources/openapi/openapi.yaml`; the OpenAPI generator (`kotlin-spring`, `interfaceOnly`) produces `...Api` interfaces + DTOs at build time. A controller **implements** the generated interface(s) for its endpoint(s) (`class ListShipmentsController(...) : ListShipmentsApi`). To change an endpoint: edit the YAML first, regenerate, then implement. Never hand-write DTOs/controller interfaces; never edit `build/generated/**`.
- **Never query on the command side to build a response**: a command controller must not call a query repository (or otherwise re-read state) just to return the mutated resource. If the response genuinely needs the updated resource, the **use case returns it** (from the aggregate it already loaded/persisted) and the controller converts that to a DTO — the controller never reaches into the read side. When the response body isn't genuinely needed, return no body (e.g. `ResponseEntity<Unit>` with 200/201), like the request-withdrawal endpoints. Returning a body "just because" is not a reason to add a read to a write path.

### Exception handler & exceptions
- The context's domain exception hierarchy (sealed classes preferred): **`common/exceptions/`**. Error-code constants: `common/application/exceptions/`. Never two same-named exception classes in different packages of one context.
- Per-context `...ControllerExceptionHandler` mapping domain exceptions → HTTP statuses: `common/infrastructure/controllers/`.

### Gateway & HTTP client
- A **gateway** is the outbound anti-corruption layer for another service: a `...Gateway` port (in the side's `contracts/`) plus a `...GatewayImpl` adapter in `<side>/infrastructure/gateways/` (plural) — `common/infrastructure/gateways/` only when both sides use it.
- **Kotlin/Spring**: raw `@FeignClient ...Client` interfaces are **centralized in `sharedkernel`**; the `...GatewayImpl` (`@Service`) wraps the client and maps responses into our models. Application code injects the gateway, never a client.

### Publisher / Listener
- **Location**: `command/infrastructure/publishers/` + `listeners/` (or `producers/` + `consumers/` — one pair per service). The port (`...Publisher`) lives in `command/domain/contracts/`; the impl wraps the broker (e.g. Pulsar).

### Job
- **Location**: `<side>/infrastructure/jobs/` — scheduled entry points that call use cases, as thin as controllers.

### Security policy (`...ViewPolicy`) & Authorities
Authorization has two levels, in two different places:

- **Coarse** — "can this actor invoke this operation at all?" — at the controller: `@PreAuthorize("hasAuthority(...)")` against a per-context **`...Authorities`** constants class in `common/domain/model[s]/`.
- **Fine-grained / row-level** — "which rows may they see, what may they do to this one?" — an explicit, testable **`<Context>ViewPolicy`** component in **`query/application/policy/`** (a policy lives on the side that calls it; `command/application/policy/` if a command needs one; `common/application/policy/` only when genuinely shared). Typical methods: derive allowed filter sets (`deriveAllowedStatuses(authorities)`), validate visibility of one resource (throws access-denied), derive a permissions DTO (`canEdit`, `canSubmit`, …) attached to the response.
- The use case *calls* the policy; the rules are never inlined in the use case, controller, or domain. Plain injected bean — no shared interface, no registry, no strategy lookup.

### `common/` module (within a context)
Holds what command and query genuinely share — and nothing else:
- **Belongs**: DBOs, DAOs, projections, specifications, extracted SQL; shared VOs/enums/`...Authorities`; the domain exception hierarchy + error codes; the controller exception handler + filter parsers; shared application services; gateways used by both sides.
- **Does NOT belong**: the write aggregate (→ `command/domain`), converters (→ each side's infrastructure), policies used by one side (→ that side), use cases, controllers with endpoints.

### `sharedkernel/` (service root)
Code every context may depend on: cross-cutting ports and shared VOs (`domain/`), base use-case interfaces (`application/`), base DBO classes, centralized HTTP/Feign clients + their config, the global exception handler, feature-flag plumbing, framework config (`infrastructure/`, `config/`). Reusable-across-contexts → `sharedkernel`; context-specific → the context. Don't let one context's persistence sneak into `sharedkernel`.

## Accepted variations

These differ between services without breaking the standard. **Meta-rule: uniform within one service (and especially within one context) — match the module you're editing.**

- `command`/`query` vs `commands`/`queries` folder names.
- `model` vs `models`, `usecase` vs `usecases` (singular/plural package names generally).
- Use-case class naming: bare verb-first (`CreateShipment`) vs `...UseCase` suffix (`CreateShipmentUseCase`) — bare verb-first preferred for new code; keep the repo's pattern.
- Controller granularity: one-per-endpoint vs one grouping related handlers for a resource — match the repo.
- DB-vendor segment: `db/dao` + `db/models` vs `db/dao/pg` + `db/models/pg`.
- Repository naming: `...Repo`/`...RepoImpl` vs `...Repository`/`...RepositoryImpl`, and suffix (`ShipmentQueryRepoImpl`) vs prefix (`QueryShipmentRepositoryImpl`) placement.
- Flat `infrastructure/converters/` vs nested `controllers/converters` + `repositories/converters`.
- Converter implementation style: extension functions vs a mapper/converter class with methods — and, though discouraged, the two sides of a context may even differ (mapper class on one, extension functions on the other).
- `publishers`/`listeners` vs `producers`/`consumers`.
- Where `sharedkernel` keeps its HTTP clients (`infrastructure/api/` vs `infrastructure/integrations/apis/`).

## Inconsistencies you may encounter (the wrong way)

Real Taager codebases contain drift. When extending such code, rule 1 of "How to apply this skill" holds — mirror the module you're in — but recognize these as deviations, never carry them into new modules, and ask before "fixing" them in place:

- **Command contracts in `application/contracts` or `common/domain/contracts`** → canon: `command/domain/contracts`.
- **The whole aggregate in `common/domain`** → canon: `command/domain/model[s]`; common keeps only shared VOs/enums/Authorities.
- **A `query/domain` package, or query code importing command domain models** → queries have no domain layer.
- **Domain events under `command/application/events` or `common/domain/events`** → canon: `command/domain/events`.
- **Converters in `application/`, in `db/converters/`, or a lowercase `converters.kt` function bag** → converters are named files in infrastructure. (The *style* — extension functions vs a mapper class — is loose; the *placement* is not.)
- **`toDTO` casing, `toApplicationModel`, reflection-based auto-mappers** → direction-specific `to<Target>` names with `Dto` casing, hand-written.
- **Projections loose in `dao/` or under `db/dao/projections`** → projections sit beside the DBOs.
- **Mixing prefix and suffix repo-impl styles within one service, or doubled words (`...CommandsCommandsRepositoryImpl`)** → pick one placement (prefix or suffix), use it consistently; no typos.
- **`gateway` (singular) folders** → `gateways`, matching `controllers`/`repositories`.
- **Singular `producer` folder, or mixing `publishers` with `consumers`** → one consistent pair.
- **Same exception class name declared in two packages of one context** → one hierarchy in `common/exceptions`.
- **`fragments/` used for routine queries** → fragments only for genuinely large composed SQL.
- **A context declaring its own raw HTTP/Feign client, or persistence for one context living in `sharedkernel`** → clients centralized in sharedkernel behind context gateways; context data stays in the context.
- **No authorization layer, or access rules inlined ad-hoc** → `@PreAuthorize` + `...ViewPolicy`.
- **Folder/class typos** (`infrastucture`, misspelled class names) exist in the wild — never copy them; spelling mistakes in package names are still the pattern-matching trap that spreads them.

## Flow reference

**Command:** Controller (implements generated `...Api`) → `dto.toModel()` → use case `execute()` → repository port loads aggregate (`dbo.toDomain()`) → aggregate enforces invariants and mutates → `aggregate.toDbo()` → single root `dao.save()` cascades children in one transaction → domain events published.

**Query:** Controller → `toModel()` → use case `execute()` (calls the `...ViewPolicy` to filter/validate when authorization applies) → query repository port → DAO native SQL/Specification → **projection** → `toApplication()` → use case returns read model → `toDto()` → response.

## Adding a new feature — order of operations

1. **Command or query?** Decides the folder and whether a domain layer is involved.
2. **Which bounded context?** Closest existing aggregate; don't create a context for an extension of an existing one.
3. **Contract-first**: change `openapi.yaml`, regenerate, get the new `...Api` signature.
4. **Domain** (commands only): new/changed invariants go in the aggregate or a domain service; consider a domain event.
5. **Application**: the use case + its `...Command`/`...Query` model; wire in the policy if access rules apply.
6. **Infrastructure last**: controller implementing the generated interface, repository/DAO/DBO/projection changes, converters.
7. **Tests at each layer** (below).

When *changing behavior*, first locate which layer owns the logic: business rule → domain; coordination/transactions → application; how data is fetched/stored/exposed → infrastructure. Needing to touch several layers for one rule usually means the logic sits in the wrong layer — consider moving it rather than patching around it.

## Testing

Three tiers, two source sets (`src/test/` unit, `src/test-integration/` integration; Gradle tasks `test` / `integrationTest`). Libraries: **MockK** + **kotest** assertions, **springmockk** (`@MockkBean`), **Testcontainers**.

- **Unit — use cases, domain models, converters, policies.** Plain JUnit in `src/test/`, colocated by package; construct the class by hand with `mockk()` collaborators, stub `every { } returns`, assert `shouldBe`, check `verify(exactly = n) { }`.
- **Controller — `@WebMvcTest` + MockMvc.** Slice-load one controller, `@MockkBean` the use case (springmockk, not Mockito's `@MockBean`), assert status + JSON.
- **DAO / integration — Testcontainers Postgres.** Extend the service's shared base test class (singleton container started once); wipe via the shared cleanup service (TRUNCATE … CASCADE); seed per class with `@TestInstance(PER_CLASS)` + `@BeforeAll`; `@AutoConfigureTestDatabase(replace = NONE)`.
- **Seeding**: direct DBO construction + root `save()` (cascade), or an object-mother fixture builder when the context provides one — prefer the fixture for readability.
- **Naming**: unit `...Test`, integration `...IntegrationTest` is the norm; some repos suffix impl integration tests `...ImplTest` / `...RepoImplIntegrationTest` — acceptable if consistent within the service.

## Review checklist

- [ ] Commands and queries in separate top-level folders; query side has **no** domain layer and imports no command domain models
- [ ] Domain layer has zero framework/ORM/HTTP imports
- [ ] One use case per file, single `execute()`, consistent use-case naming (bare verb-first preferred)
- [ ] Application layer is orchestration only — business rules live in the aggregate/domain services
- [ ] Command ports in `command/domain/contracts`; query ports in `query/application/contracts`; code depends on ports, never on `...Dao`/`...Dbo`/clients
- [ ] Aggregate in `command/domain/model[s]`; `common/domain` holds only shared VOs/enums/Authorities; one repository per aggregate root; no unbounded child lists
- [ ] Domain events in `command/domain/events`
- [ ] Endpoint/DTO changes made in `openapi.yaml` first; controllers implement generated `...Api`; nothing under `build/generated/**` edited; controllers only convert + delegate (no business logic), granularity matching the repo (per-endpoint or grouped-by-resource)
- [ ] DTO ≠ application model ≠ domain model ≠ DBO; conversions are hand-written in infrastructure (extension functions or a mapper class — consistent within the context), not reflection-based auto-mappers
- [ ] Non-trivial SQL is native and extracted into `db/dao[/pg]/queries/` constants; `fragments/` only when genuinely large; Specifications only for simple optional-filter single-table lists
- [ ] Read paths return projections (located beside the DBOs), not entities
- [ ] Aggregate persisted via a single root `save()` cascade
- [ ] External calls go through `...Gateway` ports wrapping sharedkernel clients
- [ ] Coarse auth via `@PreAuthorize` + `...Authorities`; row-level visibility/permissions via a `...ViewPolicy` in `<side>/application/policy`, called by the use case
- [ ] New code follows the surrounding module's accepted variations (singular/plural, `pg` segment, `Repo` vs `Repository`, converter layout) — no third pattern introduced
- [ ] Use case has a unit test; new controller a `@WebMvcTest`; new DAO query a Testcontainers integration test

## Notes

- The standard is language-agnostic at its core — layering and naming apply in any backend language; adapt idioms (interfaces vs abstract classes for ports, extension functions vs mapper classes) to the project's language. The Kotlin + Spring Boot notes are how Taager services implement it.
- `src/main/resources/openapi/openapi.yaml` is the API source of truth — it drives the generated interfaces and DTOs.
- Spring profiles: profile-agnostic `application.yaml` base + `application-local` / `application-dev` / `application-prod` overrides, and `application-test` for integration tests (DB supplied by Testcontainers).

## Source

Taager Tech Blog, "How We Write Code — Part 1" (Clean Architecture + DDD → CQRS), plus conventions observed across Taager's Kotlin + Spring Boot services.
