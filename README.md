# Dynamic Multi-Agent Task Allocation System

A CLI tool for real-time dynamic assignment of tasks to agents by integrating the `agent_representation_broker` with enhanced allocation algorithms. Optimizes resource utilization through multi-criteria scoring, workload balancing, and performance feedback.

## Features

- Import-based integration with `AgentBroker` for centralized coordination
- Real-time task assignment on submission with automatic matching
- Multi-criteria scoring: capabilities (required), workload (balance), performance (feedback)
- Task priority support for urgency weighting
- Dynamic rebalancing to optimize distribution
- Performance feedback loop to improve future assignments
- CLI with JSON output for automation
- Pure Python; can also import `DynamicAllocator` class directly

## Installation

Ensure `agent_representation_broker` is available in the Python path. The tool uses Python 3 standard library only otherwise.

```bash
# Check usage
python3 main.py --help
```

## Usage

### Command-Line Interface

| Option | Description |
|--------|-------------|
| `-a ID`, `--agent ID` | Register a new agent |
| `-c CAPS`, `--cap CAPS` | Agent capabilities (comma-separated, e.g., `python,api`) |
| `-T ID`, `--task ID` | Submit a new task |
| `-r REQS`, `--req REQS` | Task requirements (comma-separated) |
| `-p N`, `--pri N` | Task priority (default: 1) |
| `-R`, `--rebalance` | Rebalance all task assignments |
| `-S`, `--status` | Show current allocation status |
| `-j`, `--json` | Output status as JSON (instead of text) |
| `-f A T R`, `--feedback A T R` | Provide feedback (agent task rating 1-5) |

### Examples

**Register agent and submit task:**

```bash
python3 main.py -a agent1 -c python,api,testing -T task1 -r python,api -p 2 -S -j
```

**Sample output (JSON status):**
```json
{
  "agents": 1,
  "tasks": 1,
  "assigned": 1
}
```

**Multiple operations across separate invocations:**

```bash
# Register agents
python3 main.py -a agent1 -c python,ml
python3 main.py -a agent2 -c javascript,frontend
python3 main.py -a agent3 -c python,api

# Submit tasks
python3 main.py -T data_processing -r python,ml -p 1
python3 main.py -T web_ui -r javascript,frontend -p 1
python3 main.py -T api_service -r python,api -p 2

# Show status
python3 main.py -S
```

**Rebalance assignments to optimize workload:**
```bash
python3 main.py -R -S
```

**Record performance feedback to improve future allocations:**
```bash
python3 main.py -f agent1 data_processing 4.5
```

### Python API

Import the `DynamicAllocator` class:

```python
from main import DynamicAllocator

# Create broker
broker = DynamicAllocator()

# Register agents
broker.register_agent("agent1", ["python", "api", "testing"])
broker.register_agent("agent2", ["javascript", "frontend"])

# Submit tasks (auto-assigned on submit)
broker.submit_task("task1", ["python", "api"], priority=2)
broker.submit_task("task2", ["javascript", "frontend"], priority=1)

# Check status
print(broker.status())  # {'agents': 2, 'tasks': 2, 'assigned': 2}

# Rebalance tasks
broker.rebalance()

# Record feedback (1-5 scale)
broker.feedback("agent1", "task1", 4.5)
```

## Allocation Algorithm

1. On task submission, find all agents with **all** required capabilities.
2. Score each candidate agent using:
   - **Capability**: 1.0 (all requirements met)
   - **Workload**: `1 / (1 + task_count)` (prefers less loaded agents)
   - **Performance**: `feedback_rating / 5.0` (default 0.5 if no feedback)
3. Multiply by task priority.
4. Assign to highest-scoring agent.

Formula:
`score = (1.0 * capability_weight + (1/(1+tasks)) * workload_weight + (feedback/5) * performance_weight) * priority`

Default weights: capability=1.0, workload=0.5, performance=0.3

## Integration Details

This tool extends the `AgentBroker` class from `agent_representation_broker.agent_broker`. It adds:
- Priority field on tasks
- Automatic allocation on submit
- Workload-aware scoring
- Performance feedback tracking
- Rebalancing method

The broker state is in-memory only. For persistence, serialize using `broker.agents` and `broker.tasks` dictionaries along with `broker.feedback`.

## Limitations

- In-memory state only (lost on exit)
- CLI arguments replace each other; use the Python API for bulk operations
- Single-process; for distributed deployment, layer a REST API on top of `AgentBroker`

## Future Enhancements

- State persistence via JSON file
- Bulk import/export CLI commands
- More advanced scoring (deadline awareness, skill compatibility)
- REST API server mode
- Historical performance aggregation
