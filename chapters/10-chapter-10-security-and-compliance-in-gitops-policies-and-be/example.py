# Simulate a GitOps policy engine for RBAC using Python
# This example demonstrates a basic policy check for resource creation.

class GitOpsPolicyEngine:
    def __init__(self, rbac_rules):
        # rbac_rules: A dictionary mapping roles to lists of allowed operations on resource types.
        # Example: {"admin": ["create_pod", "delete_deployment"], "developer": ["view_pod", "create_service"]}
        self.rbac_rules = rbac_rules

    def evaluate_policy(self, user_role, operation, resource_type):
        """
        Evaluates if a user's role allows a specific operation on a resource type.
        """
        if user_role not in self.rbac_rules:
            return False, f"Error: Role '{user_role}' not defined."

        # Construct the full operation to check against the rules
        # e.g., "create_Pod", "delete_Deployment"
        full_operation = f"{operation}_{resource_type}"

        if full_operation in self.rbac_rules[user_role]:
            return True, "Policy Granted: Operation allowed."
        else:
            return False, f"Policy Denied: Role '{user_role}' cannot '{operation}' resource type '{resource_type}'."

# Define RBAC rules for our simulated GitOps environment
sample_rbac_rules = {
    "admin": ["create_Pod", "delete_Deployment", "view_Pod", "create_Service", "update_ConfigMap"],
    "developer": ["view_Pod", "create_Service"],
    "auditor": ["view_Pod", "view_Deployment", "view_Service"]
}

# Initialize our policy engine with the defined rules
policy_engine = GitOpsPolicyEngine(sample_rbac_rules)

# Simulate different user requests
print("--- Admin User Actions ---")
# Admin trying to create a Pod (allowed)
allowed, message = policy_engine.evaluate_policy("admin", "create", "Pod")
print(f"Admin, create Pod: {message} (Allowed: {allowed})")

# Admin trying to delete a Deployment (allowed)
allowed, message = policy_engine.evaluate_policy("admin", "delete", "Deployment")
print(f"Admin, delete Deployment: {message} (Allowed: {allowed})\n")

print("--- Developer User Actions ---")
# Developer trying to create a Service (allowed)
allowed, message = policy_engine.evaluate_policy("developer", "create", "Service")
print(f"Developer, create Service: {message} (Allowed: {allowed})")


# Developer trying to delete a Deployment (denied)
allowed, message = policy_engine.evaluate_policy("developer", "delete", "Deployment")
print(f"Developer, delete Deployment: {message} (Allowed: {allowed})\n")

print("--- Auditor User Actions ---")
# Auditor trying to view a Pod (allowed)
allowed, message = policy_engine.evaluate_policy("auditor", "view", "Pod")
print(f"Auditor, view Pod: {message} (Allowed: {allowed})")

# Auditor trying to create a Pod (denied)
allowed, message = policy_engine.evaluate_policy("auditor", "create", "Pod")
print(f"Auditor, create Pod: {message} (Allowed: {allowed})\n")

print("--- Unknown Role Test ---")
# User with an undefined role
allowed, message = policy_engine.evaluate_policy("unknown_user", "view", "Pod")
print(f"Unknown User, view Pod: {message} (Allowed: {allowed})")
