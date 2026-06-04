import json
import time
import random
from datetime import datetime, timedelta

# Simulate Argo CD / Flux CD reconciliation events
# These could be real-time events from APIs or log parsing

def generate_reconciliation_event(component: str, app_name: str, status: str, duration_ms: int,
                                 error_message: str = None, trace_id: str = None) -> dict:
    """Generates a simulated reconciliation event."""
    event = {
        "timestamp": datetime.now().isoformat(),
        "component": component,
        "app_name": app_name,
        "status": status,  # e.g., 'SUCCESS', 'FAILURE', 'IN_PROGRESS'
        "duration_ms": duration_ms,
        "trace_id": trace_id or f"trace-{random.randint(1000, 9999)}"
    }
    if error_message:
        event["error_message"] = error_message
    return event

def process_event(event: dict, metrics: dict, logs: list, traces: dict):
    """Processes a single event to update metrics, logs, and traces."""

    # 1. Metrics Collection (Simulated Prometheus counters/histograms)
    component = event['component']
    app_name = event['app_name']
    status = event['status']
    duration_ms = event['duration_ms']

    # Initialize metrics if not present
    if component not in metrics:
        metrics[component] = {
            'reconciliation_total_count': {},
            'reconciliation_duration_sum_ms': {},
            'reconciliation_duration_count': {},
        }
    if app_name not in metrics[component]['reconciliation_total_count']:
        metrics[component]['reconciliation_total_count'][app_name] = {'SUCCESS': 0, 'FAILURE': 0, 'IN_PROGRESS': 0}
        metrics[component]['reconciliation_duration_sum_ms'][app_name] = 0
        metrics[component]['reconciliation_duration_count'][app_name] = 0

    metrics[component]['reconciliation_total_count'][app_name][status] += 1
    metrics[component]['reconciliation_duration_sum_ms'][app_name] += duration_ms
    metrics[component]['reconciliation_duration_count'][app_name] += 1

    # 2. Log Aggregation (Simulated structured logs)
    logs.append({
        "time": event['timestamp'],
        "level": "INFO" if status == "SUCCESS" else "ERROR",
        "message": f"App '{app_name}' reconciliation {status}",
        "component": component,
        "trace_id": event.get('trace_id'),
        "details": {"duration_ms": duration_ms, "error": event.get('error_message')}
    })

    # 3. Tracing (Simulated span aggregation for a single trace_id)
    trace_id = event['trace_id']
    if trace_id not in traces:
        traces[trace_id] = []
    
    # Each event represents a 'span' in the trace
    traces[trace_id].append({
        "span_name": f"{component}-reconcile-{app_name}",
        "start_time": event['timestamp'],
        "duration_ms": duration_ms,
        "status": status,
        "tags": {
            "app_name": app_name,
            "component": component,
            "error": "true" if status == "FAILURE" else "false",
            "error_message": event.get('error_message', "")
        }
    })

# Initialize storage for our observability data
observability_metrics = {}
observability_logs = []
observability_traces = {}

# Simulate a series of reconciliation events over time
print("--- Generating Reconciliation Events ---")
for i in range(10):
    component_choice = random.choice(['argocd-controller', 'flux-reconciler'])
    app_choice = random.choice(['my-app-prod', 'dev-api', 'auth-service'])
    status_choice = 'SUCCESS'
    error_msg = None
    if random.random() < 0.2:  # Simulate 20% failures
        status_choice = 'FAILURE'
        error_msg = random.choice([
            "Helm chart failed to render",
            "Kubernetes API unauthorized",
            "Resource already exists",
            "Image pull failed"
        ])

    duration = random.randint(100, 5000) # 100ms to 5s
    
    event = generate_reconciliation_event(
        component=component_choice,
        app_name=app_choice,
        status=status_choice,
        duration_ms=duration,
        error_message=error_msg
    )
    print(f"Generated Event: {event['component']} / {event['app_name']} / {event['status']}")
    process_event(event, observability_metrics, observability_logs, observability_traces)
    time.sleep(0.1) # Simulate real-time processing

print("\n--- Processed Observability Data ---")

print("\nMetrics (Simplified View):")
for comp, comp_metrics in observability_metrics.items():
    print(f"Component: {comp}")
    for app, counts in comp_metrics['reconciliation_total_count'].items():
        avg_duration = 0
        if comp_metrics['reconciliation_duration_count'][app] > 0:
            avg_duration = comp_metrics['reconciliation_duration_sum_ms'][app] / comp_metrics['reconciliation_duration_count'][app]
        print(f"  App: {app}")
        print(f"    Successes: {counts['SUCCESS']}, Failures: {counts['FAILURE']}")
        print(f"    Avg Duration: {avg_duration:.2f} ms")

print("\nLast 3 Logs:")
for log in observability_logs[-3:]:
    print(json.dumps(log, indent=2))

print(f"\nTotal Traces Captured: {len(observability_traces)}")
print("Example Trace Details (first 1 trace_id found):")
if observability_traces:
    first_trace_id = next(iter(observability_traces))
    print(f"  Trace ID: {first_trace_id}")
    for span in observability_traces[first_trace_id]:
        print(f"    - {span['span_name']} ({span['duration_ms']}ms) - {span['status']}")
        if 'error_message' in span['tags'] and span['tags']['error_message']:
            print(f"      Error: {span['tags']['error_message']}")
