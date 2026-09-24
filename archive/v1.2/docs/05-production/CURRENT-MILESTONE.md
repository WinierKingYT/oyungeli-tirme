# Current Milestone

Milestone ID: `G0-PROCESS-BOOTSTRAP`

Status: `UNAPPROVED`

## Goal

Install and ratify the development operating system in the real game repository without modifying production gameplay.

## Exit criteria

- `python scripts/doctor.py --require-claude` and `python scripts/validate_os.py` pass in the real developer environment.
- Project owner reviews constitution and permission model.
- Project discovery task is created.
- No active implementation lease exists.
- Initial authority and status documents contain no false accepted claims.

## Abort/replan criteria

- Claude Code version does not support required hooks/settings.
- Required Python runtime cannot be made available.
- Repository policy conflicts with the lease model.
