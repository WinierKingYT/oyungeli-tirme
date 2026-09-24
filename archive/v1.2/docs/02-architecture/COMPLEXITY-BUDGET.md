# Complexity Budget

Complexity is a budget, not a free by-product.

Every new manager, service, subsystem, interface, factory, registry, helper layer, dependency, global, schema, thread, replicated actor, tick, or persistent format requires a stated current problem and ownership.

## Review triggers

- a local feature modifies unrelated modules;
- more new abstractions than observable behaviors;
- duplicate vocabulary for the same capability;
- adapters with only one implementation and no boundary need;
- pass-through layers that add no policy;
- configuration split among multiple authorities;
- coordination objects that own domain state.

When a trigger fires, perform a delete-before-add review.

