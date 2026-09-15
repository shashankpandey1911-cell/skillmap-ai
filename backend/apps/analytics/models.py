"""The analytics app defines no models.

It exposes read-only aggregation endpoints that compute statistics from the
other apps' data at request time (services in apps/core/services/). Keeping
it model-free avoids denormalized caches and stale numbers.
"""