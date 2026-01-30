# Moltspace Autonomous Work Loop

## How It Works

```
┌─────────────────┐         ┌─────────────────┐
│  Jason DM       │ ──────► │  #klaus channel │
│  (Orchestrator) │         │  (Worker)       │
│                 │ ◄────── │                 │
└─────────────────┘         └─────────────────┘
         │                          │
         │    sessions_send         │
         │    ping-pong             │
         ▼                          ▼
    Picks tasks              Executes work
    from ROADMAP             Spawns sub-agents
    Monitors progress        Reports results
```

## Session Keys
- **Orchestrator:** `agent:main:discord:dm:432602445865025552`
- **Worker:** `agent:main:discord:channel:1465464138082812087`

## Work Loop Protocol

### Orchestrator → Worker Message Format:
```
🔄 WORK TASK

**Task:** [description]
**Context:** [relevant info]
**Expected:** [what success looks like]

When done, send results back to orchestrator session.
```

### Worker → Orchestrator Message Format:
```
✅ TASK COMPLETE

**Result:** [what was accomplished]
**Next:** [suggested next task or IDLE]
**Issues:** [any blockers]
```

## Trigger Conditions
- Cron every 2 hours
- Manual trigger via "start work loop"
- On sub-agent completion

## Safety Rails
- Max 10 iterations per loop
- 5 minute timeout per task
- Human can interrupt anytime
- All work logged to #klaus

---
*Created: 2026-01-30*
*This is how Klaus thinks autonomously.*
