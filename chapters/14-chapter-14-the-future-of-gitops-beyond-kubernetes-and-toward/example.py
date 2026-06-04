# This simplified example simulates a "cognitive" GitOps agent.
# It monitors a desired state (Git repository) and current state (simulated infrastructure).
# Instead of simple diffs, it uses basic "cognition" (pattern matching, heuristics)
# to suggest intelligent, proactive, or corrective actions, moving beyond direct reconciliation.

import time
import random

class GitRepository:
    """Simulates a Git repository where desired state is defined."""
    def __init__(self):
        self.desired_config = {
            "app_version": "1.0.0",
            "environment": "production",
            "resource_limits": {"cpu": "500m", "memory": "512Mi"},
            "autoscaling_enabled": True,
            "traffic_shaping_rules": {"burst": "high"}
        }

    def get_desired_state(self):
        return self.desired_config

    def update_desired_state(self, new_state):
        """Simulates a commit to Git."""
        self.desired_config.update(new_state)
        print(f"Git: Desired state updated to {new_state}")

class InfrastructureObserver:
    """Simulates an agent observing the current infrastructure state."""
    def __init__(self):
        self.current_config = {
            "app_version": "1.0.0",
            "environment": "production",
            "resource_limits": {"cpu": "400m", "memory": "256Mi"}, # Under-provisioned
            "autoscaling_enabled": False, # Disabled
            "traffic_shaping_rules": {"burst": "medium"}
        }
        self.current_metrics = {
            "cpu_utilization": 0.85, # High CPU
            "memory_usage": 0.70,
            "error_rate": 0.01
        }

    def get_current_state(self):
        # Simulate some drift and dynamic metrics
        self.current_metrics["cpu_utilization"] = round(random.uniform(0.6, 0.95), 2)
        self.current_metrics["error_rate"] = round(random.uniform(0.005, 0.03), 3)
        return self.current_config, self.current_metrics

class CognitiveGitOpsAgent:
    """
    Simulates a cognitive agent that not only reconciles but also
    suggests proactive changes based on current state and metrics.
    """
    def __init__(self, git_repo, infra_observer):
        self.git_repo = git_repo
        self.infra_observer = infra_observer

    def analyze_and_suggest(self):
        desired_state = self.git_repo.get_desired_state()
        current_state, current_metrics = self.infra_observer.get_current_state()
        suggestions = []

        print("\n--- Cognitive Agent Analyzing ---")
        print(f"Desired: {desired_state}")
        print(f"Current: {current_state}")
        print(f"Metrics: {current_metrics}")

        # Rule 1: Proactive scaling suggestion based on high CPU utilization
        if current_metrics["cpu_utilization"] > 0.8 and desired_state["autoscaling_enabled"]:
            if current_state["resource_limits"]["cpu"] == desired_state["resource_limits"]["cpu"]:
                suggestions.append(
                    f"High CPU ({current_metrics['cpu_utilization']}). "
                    "Recommend increasing 'resource_limits.cpu' in Git. (Proactive Scaling Re-evaluation)"
                )
        elif current_metrics["cpu_utilization"] < 0.3 and desired_state["autoscaling_enabled"]:
             if current_state["resource_limits"]["cpu"] == desired_state["resource_limits"]["cpu"]:
                suggestions.append(
                    f"Low CPU ({current_metrics['cpu_utilization']}). "
                    "Consider decreasing 'resource_limits.cpu' in Git to optimize costs. (Cost Optimization)"
                )


        # Rule 2: Drift detection for critical features not reflected in Git
        if not desired_state["autoscaling_enabled"] and current_state["autoscaling_enabled"]:
            suggestions.append(
                "Autoscaling is enabled in current state but disabled in Git. Reconcile by updating Git or disabling infra. (GitOps Drift)"
            )
        elif desired_state["autoscaling_enabled"] and not current_state["autoscaling_enabled"]:
             suggestions.append(
                "Autoscaling is disabled in current state but enabled in Git. Reconcile by updating Git or enabling infra. (GitOps Drift)"
            )

        # Rule 3: Heuristic for potential misconfiguration based on traffic shaping
        if desired_state["traffic_shaping_rules"]["burst"] == "high" and current_metrics["error_rate"] > 0.02:
            suggestions.append(
                "High error rate with 'high' traffic burst. "
                "Suggest reviewing 'traffic_shaping_rules' in Git, perhaps lowering burst or increasing resources. (Heuristic Anomaly)"
            )

        if not suggestions:
            print("No immediate cognitive suggestions.")
        else:
            print("\n--- Cognitive Suggestions for Git Updates ---")
            for s in suggestions:
                print(f"- {s}")

            # Example of a simple actionable suggestion:
            # If CPU is critically high and resource limits match, suggest increasing limits in Git.
            if "Recommend increasing 'resource_limits.cpu' in Git" in str(suggestions):
                current_cpu_limit = desired_state["resource_limits"]["cpu"]
                # A real system would parse "500m" to int and increment, this is simplified.
                new_cpu_value = "750m" if current_cpu_limit == "500m" else "1000m"
                print(f"\nACTIONABLE: Agent suggests updating Git with: {{'resource_limits': {{'cpu': '{new_cpu_value}'}}}}")
                # For demonstration, we'll simulate an approved change going into Git.
                # In a real system, this would be a PR suggestion or an auto-PR.
                # self.git_repo.update_desired_state({"resource_limits": {"cpu": new_cpu_value}})

# --- Simulation ---
git_repo = GitRepository()
infra_observer = InfrastructureObserver()
cognitive_agent = CognitiveGitOpsAgent(git_repo, infra_observer)

print("Initial States:")
cognitive_agent.analyze_and_suggest()

# Simulate some time passing and metrics changing
print("\n--- Simulating time and metric fluctuations ---")
for i in range(3):
    time.sleep(1) # Simulate observation interval
    print(f"\n--- Cycle {i+1} ---")
    cognitive_agent.analyze_and_suggest()

# Simulate a manual update to Git that fixes one issue (e.g., autoscaling enabled)
print("\n--- Simulating a Git commit to enable autoscaling ---")
git_repo.update_desired_state({"autoscaling_enabled": True})
time.sleep(1)
cognitive_agent.analyze_and_suggest()

# One more cycle to see effect
print("\n--- Final Cycle ---")
cognitive_agent.analyze_and_suggest()
