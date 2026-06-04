# Deployment Evolution: Manual vs. Declarative (GitOps Principle)

# --- Manual Deployment (Simplified Analogy) ---
# Imagine a system administrator manually creating and updating servers.

class ManualServer:
    def __init__(self, name):
        self.name = name
        self.status = "off"
        self.app_version = "none"

    def start_server(self):
        # Manually perform actions
        self.status = "running"
        print(f"Manual: Server '{self.name}' started.")

    def deploy_app(self, version):
        # Manually copy files, run commands
        self.app_version = version
        print(f"Manual: App v{version} deployed to '{self.name}'.")

# Administrator's actions
server1_manual = ManualServer("web-01")
server1_manual.start_server()
server1_manual.deploy_app("1.0.0")

server2_manual = ManualServer("web-02")
server2_manual.start_server()
# Oops, forgot to deploy app to server2, or deployed a different version!
# This leads to inconsistency and errors.
# server2_manual.deploy_app("0.9.0")  # Potential drift


# --- Declarative Deployment (GitOps-like Principle) ---
# Define desired state in a 'git repository' (represented by a dictionary here).
# An automated agent (like Argo CD/Flux) continuously reconciles reality to this desired state.

class GitOpsAgent:
    def __init__(self, current_servers):
        self.current_servers = current_servers  # Current actual state, e.g., from a cluster API

    def reconcile(self, desired_state):
        print("\nDeclarative: Initiating reconciliation...")
        for server_name, desired_config in desired_state.items():
            if server_name not in self.current_servers:
                self.current_servers[server_name] = ManualServer(server_name)
                print(f"  Declarative: Creating missing server '{server_name}'.")

            server = self.current_servers[server_name]

            # Ensure server is running
            if desired_config.get("status") == "running" and server.status != "running":
                server.start_server()

            # Ensure correct app version is deployed
            desired_version = desired_config.get("app_version")
            if desired_version and server.app_version != desired_version:
                server.deploy_app(desired_version)
            elif not desired_version and server.app_version != "none":
                 # Optional: handle removal or default
                 server.app_version = "none"
                 print(f"  Declarative: Removing app from '{server_name}' (no version declared).")

        print("Declarative: Reconciliation complete. Current state:")
        for server_name, server in self.current_servers.items():
            print(f"  Server '{server.name}': Status={server.status}, App={server.app_version}")

# Desired state in 'Git'
desired_state_v1 = {
    "web-01": {"status": "running", "app_version": "1.0.0"},
    "web-02": {"status": "running", "app_version": "1.0.0"}
}

# Initial actual state (could be empty or inconsistent)
actual_servers_initial = {
    "web-01": ManualServer("web-01") # Server might exist, but not correctly configured
}

gitops_controller = GitOpsAgent(actual_servers_initial)
gitops_controller.reconcile(desired_state_v1)

# Now, let's update the desired state (e.g., commit to Git)
print("\n--- Applying a new desired state (v2) ---")
desired_state_v2 = {
    "web-01": {"status": "running", "app_version": "1.1.0"}, # Update
    "web-02": {"status": "running", "app_version": "1.1.0"}, # Update
    "db-01": {"status": "running", "app_version": "2.0.0"} # New resource
}

gitops_controller.reconcile(desired_state_v2)

# If an engineer manually changes something (drift), GitOps will fix it
# Simulate manual drift on web-01
print("\n--- Simulating manual drift ---")
gitops_controller.current_servers["web-01"].app_version = "OLD_VERSION"
print(f"  Manual: Server web-01 was manually downgraded to {gitops_controller.current_servers['web-01'].app_version}")

gitops_controller.reconcile(desired_state_v2) # GitOps reconciles the drift
