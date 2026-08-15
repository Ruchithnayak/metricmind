# Audit Model

The audit trail records local user actions such as sign-in, analyst queries, scenario execution, filter resets and exports.

A production audit system should persist actor identity, timestamp, action, object, before/after values and authorization result in an append-only store.
