# Kotlin + Spring Boot implementation notes

How the layering in `SKILL.md` is built with Kotlin, Spring Boot, JPA, and an
OpenAPI-generated API. Read alongside `SKILL.md`; this file only covers the
mechanics, not where things go.

## Contract-first API

The API is defined in a spec (typically `src/main/resources/openapi/openapi.yaml`)
and the OpenAPI generator (`kotlin-spring`, `interfaceOnly`) produces `...Api`
interfaces plus request/response DTOs at build time.

- A controller **implements** the generated interface for its endpoints:
  `class ListShipmentsController(...) : ListShipmentsApi`.
- To change an endpoint: **edit the YAML first**, regenerate, then implement the
  new signature.
- Never hand-write DTOs or controller interfaces that the generator owns, and
  never edit anything under `build/generated/**` — it is overwritten.

The generated DTOs are wire types. They are converted to application models at
the controller boundary and never travel further in.

## Use cases

Extend the service's shared base interfaces from `sharedkernel/application/`
(`CommandUseCase`, `QueryUseCase`, `EventHandler`, …) when the service defines
them. One class, one `execute()`.

## Persistence

**DBO (persistence entity)** — `@Entity` classes suffixed `Dbo`, extending the
shared base DBOs from `sharedkernel`. Hibernate features are fine here
(`@NamedEntityGraph`, `@JdbcTypeCode`). This is the persistence representation
only; the domain model has zero JPA imports.

**DAO** — `...Dao : JpaRepository<...>` Spring Data interfaces (plus
`JpaSpecificationExecutor` when specifications are used). Derived methods
(`findBySku`) for simple lookups only, often with `@EntityGraph`.

**Repository impl** — a `@Repository` component implementing the domain port. It
delegates to one or more DAOs and maps DBO/projection ↔ domain model via the
`to*` converters. **The transaction boundary lives here**, not in the use case.

**Aggregate persistence via cascade** — relationships declare
`cascade = [CascadeType.ALL]`, collections also `orphanRemoval = true`, so a
single `dao.save(rootDbo)` inside one transaction persists the whole aggregate.
Save the root; never save children individually.

**Projections** — getter-per-column interfaces returned by read queries instead of
full entities. The query repository impl maps projection → application model via
`toApplication`.

## SQL

Prefer explicit `@Query(..., nativeQuery = true)` with hand-written SQL over
ORM-generated queries and lazy-loading graphs — you keep full control of what the
database actually runs.

- Non-trivial SQL is extracted into `const` holder classes under
  `db/dao[/pg]/queries/`, not inlined in the DAO.
- `queries/fragments/` (reusable CTE / sub-select composition) is for genuinely
  large queries built from many subqueries and optional filters. Don't reach for
  fragments by default.

**JPA Specifications** are an accepted alternative to native SQL **only** for list
queries that are several *optional* equality/range/`IN` predicates on a single
table: the impl collects predicates into a list, `cb.and(...)`, then
`dao.findAll(spec, pageable)`. Anything with joins, aggregation, or CTEs stays
native SQL. Specifications live in `db/specifications/`.

## Converters

Hand-written and direction-specific. Prefer `to<Target>` names:

| Name | Direction |
|---|---|
| `toModel` | DTO → application model |
| `toDto` | application/domain → DTO |
| `toDomain` | DBO → domain model |
| `toDbo` | domain model → DBO |
| `toApplication` | DBO/projection → application read model |

Avoid `toDTO` casing, `toApplicationModel`-style verbosity, and reflection-based
auto-mappers (MapStruct, ModelMapper) unless the module already commits to one.

Two implementation styles are both acceptable:

1. **Extension functions** on the model being converted —
   `fun ProductDbo.toDomain(): Product`
2. **A mapper/converter class** — `object ProductMapper { fun toDomain(dbo) }`,
   or a `@Component` converter

Consistency within a context (ideally the whole service) is preferred. When adding
to existing code, match the surrounding style rather than introducing the other.

## Gateways and HTTP clients

Raw `@FeignClient ...Client` interfaces are centralized — typically in
`sharedkernel/infrastructure/` — so one service's client isn't redeclared in
several contexts. Each context wraps the client in a `...GatewayImpl` (`@Service`)
that implements the context's `...Gateway` port and maps responses into that
context's models.

Application code injects the **gateway**, never the client. That's what makes it
an anti-corruption layer instead of a pass-through.

## Messaging

The `...Publisher` port lives in `command/domain/contracts/`; the impl in
`command/infrastructure/publishers/` wraps the broker client (Pulsar, Kafka, …).
Listeners/consumers are entry points in `command/infrastructure/listeners/` — as
thin as controllers, delegating to a use case or an `...Handler`.

## Authorization

- **Coarse**: `@PreAuthorize("hasAuthority(...)")` on the controller, against a
  per-context authority constants class.
- **Row-level**: a `...ViewPolicy` component called by the use case. See
  `cqrs.md` for placement.

## Testing

Three tiers across two source sets — `src/test/` (unit, Gradle `test`) and
`src/test-integration/` (integration, Gradle `integrationTest`). Libraries:
**MockK** + **kotest** assertions, **springmockk** for `@MockkBean`,
**Testcontainers** for the database.

**Unit** — use cases, domain models, converters, policies. Plain JUnit in
`src/test/`, colocated by package. Construct the class by hand with `mockk()`
collaborators, stub with `every { } returns`, assert with `shouldBe`, verify
interactions with `verify(exactly = n) { }`.

**Controller** — `@WebMvcTest` + MockMvc. Slice-load one controller, `@MockkBean`
the use case (springmockk's `@MockkBean`, not Mockito's `@MockBean`), assert
status and JSON body.

**DAO / integration** — Testcontainers Postgres. Extend the service's shared base
test class so the container starts once as a singleton; wipe state via the shared
cleanup service (`TRUNCATE … CASCADE`); seed per class with
`@TestInstance(PER_CLASS)` + `@BeforeAll`; `@AutoConfigureTestDatabase(replace = NONE)`.

**Seeding** — direct DBO construction plus a root `save()` (cascade does the rest),
or an object-mother fixture builder when the context provides one. Prefer the
fixture for readability.

**Naming** — unit tests `...Test`, integration tests `...IntegrationTest`. Some
services suffix repository-impl integration tests `...ImplTest` or
`...RepoImplIntegrationTest`; acceptable if consistent within the service.

## Configuration

A profile-agnostic `application.yaml` base with `application-local` /
`application-dev` / `application-prod` overrides, plus `application-test` for
integration tests (the database supplied by Testcontainers).

## Running tests locally

Integration tests start containers and are resource-heavy. Select the classes your
change touches rather than running whole suites, and don't run `test`,
`integrationTest`, and static analysis concurrently:

```bash
./gradlew test --tests '*LocalInventorySnapshotTest'
./gradlew integrationTest --tests '*LocalInventorySnapshotRepoImplTest'
```

Skip local coverage tasks — they typically re-run the full integration suite
unconditionally. Full-suite runs and coverage are CI's job.
