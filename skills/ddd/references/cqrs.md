# The command/query split (CQRS)

Read this when the bounded context you're editing splits reads from writes, or
when you're deciding whether a new one should. The invariants in `SKILL.md` still
apply — this adds the rules that don't follow from layering alone.

## Why split at all

Every use case either **changes state** (a command) or **reads state and changes
nothing** (a query). The domain layer exists to protect invariants while
*changing* state. Reads change nothing, so they need no invariant protection —
and forcing them through the write model buys nothing while costing a lot:
loading whole aggregates to render a list, joining across roots that don't want
to be joined, read shapes distorted to fit write models.

Splitting makes that explicit at the top of the context, so write-side rules stay
out of read paths and read-shaped convenience stays out of the write model.

**The cost:** two of most things, a `common/` module to arbitrate, and a rule
everyone has to remember (below). Pay it when reads and writes genuinely diverge.
Don't pay it for a CRUD context — see the topology table in `SKILL.md`.

## The rule that matters most

**The query side has no domain layer, and query code never imports command-side
domain models.**

A query shapes data from infrastructure into read models. That's it. The moment a
query imports the write aggregate, the split has stopped paying for itself and
started costing: the write model is now shaped by read needs, and read paths can
trip write invariants.

Corollaries:

- A `query/domain/` package is always wrong. If you find one, its contents belong
  in `query/application/model[s]/` (read models) or on the command side.
- Query-side **ports live in `query/application/contracts/`** — there is no query
  domain layer to hold them. Command-side ports live in
  `command/domain/contracts/`. This asymmetry is deliberate, not an oversight.
- Shared value objects, enums, and statuses that both sides genuinely need go in
  `common/domain/model[s]/` — never the aggregate itself.

## Canonical tree

One split context, fully populated. `[s]`, `[/pg]` etc. mark accepted variations
(see the last section) — pick one per service and stay with it.

```
<context>/
├── command[s]/
│   ├── domain/
│   │   ├── model[s]/              # aggregate root, entities, write-side value objects
│   │   ├── contracts/             # ports: ...Repo(sitory), ...Gateway, ...Publisher
│   │   ├── events/                # domain events emitted by aggregates
│   │   ├── services/              # domain services (logic spanning models)
│   │   └── exceptions/            # (optional) write-side-only exceptions
│   ├── application/
│   │   ├── usecase[s]/            # one class per use case, single execute()
│   │   ├── model[s]/              # ...Command / ...Request inputs, ...Result outputs
│   │   └── policy/                # only if a command needs an access policy
│   └── infrastructure/
│       ├── controllers/
│       ├── converters/            # or controllers/converters + repositories/converters
│       ├── repositories/          # ...RepoImpl implementing the domain contracts
│       ├── gateways/              # ...GatewayImpl wrapping shared HTTP clients
│       ├── publishers/            # or producers/
│       ├── listeners/             # or consumers/
│       ├── jobs/                  # scheduled entry points
│       └── config/
├── quer{y,ies}/
│   ├── application/               # ← no domain layer
│   │   ├── usecase[s]/
│   │   ├── model[s]/              # ...Query inputs, read models / result types
│   │   ├── contracts/             # ports: ...QueryRepo(sitory)
│   │   └── policy/                # ...ViewPolicy — row-level access rules
│   └── infrastructure/
│       ├── controllers/
│       ├── converters/
│       └── repositories/          # ...QueryRepoImpl
└── common/                        # shared *within* this context
    ├── domain/
    │   └── model[s]/              # shared value objects, enums, statuses
    ├── application/
    │   ├── services/              # services genuinely used by both sides
    │   ├── policy/                # only if a policy is genuinely used by both sides
    │   └── exceptions/            # error-code constants
    ├── exceptions/                # the context's domain exception hierarchy
    └── infrastructure/
        ├── controllers/           # ...ControllerExceptionHandler, filter parsers
        ├── gateways/              # only if a gateway serves both sides
        └── db/
            ├── dao[/pg]/
            │   └── queries/       # extracted SQL constants
            │       └── fragments/ # only for genuinely large composed queries
            ├── models[/pg]/       # persistence entities
            ├── projections/       # read projections, beside the entities
            └── specifications/    # dynamic-filter specifications
```

A **self-contained sub-module** (e.g. an `analytics/` reporting slice with its own
`domain`/`application`/`infrastructure` and no split, deliberately isolated from
the transactional model) is an allowed escape hatch. It is not permission to skip
layering elsewhere.

## What belongs in `common/`

**Yes:** persistence entities, DAOs, projections, specifications, extracted SQL;
value objects/enums/authority constants both sides use; the domain exception
hierarchy and error codes; the controller exception handler and filter parsers;
application services genuinely called by both sides; gateways used by both sides.

**No:** the write aggregate (→ `command/domain/model[s]/`); converters (→ each
side's infrastructure); a policy only one side calls (→ that side); use cases;
controllers with endpoints.

Parking the aggregate in `common/` is the most common way this collapses: the
query side can then reach it, and eventually will.

## Projections

Read paths return **projections** — narrow, per-column read types — not
persistence entities. The query repository impl maps projection → application read
model. Projections live beside the persistence entities (`db/projections/` or
`db/models[/pg]/projections/`), never loose inside the DAO package.

## Policies

Authorization sits at two levels, in two places:

- **Coarse** — "may this actor invoke this operation at all?" — at the controller,
  declaratively, against a per-context authority constants class in
  `common/domain/model[s]/`.
- **Fine-grained / row-level** — "which rows may they see, what may they do to
  this one?" — an explicit, testable `<Context>ViewPolicy` component. It lives on
  the side that calls it: `query/application/policy/` for read visibility,
  `command/application/policy/` when a command needs one,
  `common/application/policy/` only when genuinely shared.

Typical policy methods: derive the allowed filter set from the actor's
authorities, validate visibility of a single resource (throwing access-denied),
derive a permissions object (`canEdit`, `canSubmit`) to attach to the response.

The **use case calls the policy**. The rules are never inlined in the use case,
the controller, or the domain. A plain injected component — no shared interface,
no registry, no strategy lookup.

## Commands never read through the query side

A command controller must not call a query repository to build its response, and
a command use case must not re-read state it just wrote. If the response needs
the updated resource, the use case returns it from the aggregate it already
loaded and persisted. If the body isn't genuinely needed, return no body.

Returning a body "because the endpoint should return something" is not a reason
to add a read to a write path.

## Accepted variations

These differ between services without breaking anything. **Uniform within one
service, and especially within one context — match the module you're editing.**

- `command`/`query` vs `commands`/`queries`
- `model` vs `models`, `usecase` vs `usecases` (singular/plural generally)
- Use-case naming: bare verb-first (`CreateShipment`) vs `...UseCase` suffix —
  bare verb-first preferred for new code; keep the repo's pattern
- Controller granularity: one per endpoint vs one grouping a resource's endpoints
- Repository naming: `...Repo`/`...RepoImpl` vs `...Repository`/`...RepositoryImpl`,
  and suffix (`ShipmentQueryRepoImpl`) vs prefix (`QueryShipmentRepositoryImpl`)
- DB-vendor segment: `db/dao` + `db/models` vs `db/dao/pg` + `db/models/pg`
- Flat `infrastructure/converters/` vs nested `controllers/converters` +
  `repositories/converters`
- Converter style: extension functions vs a mapper/converter class. The two sides
  of one context may even differ — tolerated, not recommended; match what's there
- `publishers`/`listeners` vs `producers`/`consumers`

Per `SKILL.md` §5 these are **variations**: conform silently, and don't introduce
a third option. A stray `query/domain/`, an aggregate in `common/`, or a query
importing a write model is **not** a variation — those are defects.

## Split-context review checklist

- [ ] Commands and queries in separate top-level folders
- [ ] Query side has **no** domain layer and imports no command-side domain models
- [ ] Command ports in `command/domain/contracts/`; query ports in `query/application/contracts/`
- [ ] Aggregate in `command/domain/model[s]/`; `common/domain/` holds only shared value objects, enums, authorities
- [ ] Domain events in `command/domain/events/`
- [ ] Read paths return projections, located beside the persistence entities
- [ ] Row-level visibility via a `...ViewPolicy` on the calling side, invoked by the use case
- [ ] No command path reading through a query repository to build a response
- [ ] `common/` contains nothing that belongs to one side only
- [ ] Naming variations match the rest of the service — no third pattern
