"""The recommendations app defines no persistent models.

Matches, gaps and learning suggestions are computed on demand from live
data (services in apps/core/services/) so results never go stale. A
student's last match snapshot can be cached later if needed.
"""