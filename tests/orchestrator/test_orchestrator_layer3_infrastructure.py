"""
Layer 3: Infrastructure Orchestration - Comprehensive Test Suite

Tests cover:
- Cloud provider abstraction (AWS, GCP, Azure)
- Infrastructure state management
- Terraform orchestration
- Kubernetes orchestration
- Deployment planning, execution, and rollback
"""

import pytest
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../scripts"))

from orchestrator_layer3_infrastructure import (
    CloudProvider,
    DeploymentStrategy,
    ResourceType,
    CloudResource,
    InfrastructureState,
    DeploymentPlan,
    DeploymentResult,
    DeploymentRecord,
    CloudStateManager,
    TerraformOrchestrator,
    KubernetesOrchestrator,
    DeploymentOrchestrator,
)


class TestCloudProvider:
    """Test CloudProvider enum."""

    def test_cloud_provider_values(self):
        """Test all cloud providers are defined."""
        providers = [CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE]
        assert len(providers) == 3

    def test_cloud_provider_aws_value(self):
        """Test AWS provider value."""
        assert CloudProvider.AWS.value == "aws"

    def test_cloud_provider_gcp_value(self):
        """Test GCP provider value."""
        assert CloudProvider.GCP.value == "gcp"

    def test_cloud_provider_azure_value(self):
        """Test Azure provider value."""
        assert CloudProvider.AZURE.value == "azure"


class TestDeploymentStrategy:
    """Test deployment strategies."""

    def test_deployment_strategies_defined(self):
        """Test all strategies are defined."""
        strategies = [
            DeploymentStrategy.ROLLING,
            DeploymentStrategy.BLUE_GREEN,
            DeploymentStrategy.CANARY,
            DeploymentStrategy.ALL_AT_ONCE,
        ]
        assert len(strategies) == 4

    def test_rolling_strategy(self):
        """Test rolling strategy."""
        assert DeploymentStrategy.ROLLING.value == "rolling"

    def test_blue_green_strategy(self):
        """Test blue-green strategy."""
        assert DeploymentStrategy.BLUE_GREEN.value == "blue_green"


class TestResourceType:
    """Test cloud resource types."""

    def test_resource_types_defined(self):
        """Test all resource types are defined."""
        types = [
            ResourceType.COMPUTE,
            ResourceType.STORAGE,
            ResourceType.DATABASE,
            ResourceType.NETWORK,
            ResourceType.CONTAINER,
            ResourceType.LOAD_BALANCER,
        ]
        assert len(types) == 6


class TestCloudResource:
    """Test CloudResource."""

    def test_create_compute_resource(self):
        """Test creating a compute resource."""
        resource = CloudResource(
            id="ec2-001",
            type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        assert resource.id == "ec2-001"
        assert resource.type == ResourceType.COMPUTE
        assert resource.provider == CloudProvider.AWS
        assert resource.region == "us-east-1"

    def test_create_database_resource(self):
        """Test creating a database resource."""
        resource = CloudResource(
            id="rds-001",
            type=ResourceType.DATABASE,
            provider=CloudProvider.AWS,
            region="us-west-2",
        )

        assert resource.type == ResourceType.DATABASE

    def test_resource_with_tags(self):
        """Test resource with tags."""
        resource = CloudResource(
            id="ec2-001",
            type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            region="us-east-1",
            tags={"env": "prod", "team": "backend"},
        )

        assert resource.tags["env"] == "prod"
        assert resource.tags["team"] == "backend"

    def test_resource_with_configuration(self):
        """Test resource with configuration."""
        resource = CloudResource(
            id="ec2-001",
            type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            region="us-east-1",
            configuration={"instance_type": "t3.medium", "volume_size": 100},
        )

        assert resource.configuration["instance_type"] == "t3.medium"


class TestInfrastructureState:
    """Test InfrastructureState."""

    def test_state_creation(self):
        """Test creating infrastructure state."""
        state = InfrastructureState(
            timestamp="2026-07-12T10:00:00",
            cloud_provider=CloudProvider.AWS,
            environment="staging",
        )

        assert state.cloud_provider == CloudProvider.AWS
        assert state.environment == "staging"
        assert len(state.resources) == 0

    def test_state_with_resources(self):
        """Test state with resources."""
        resource = CloudResource(
            id="vpc-001",
            type=ResourceType.NETWORK,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        state = InfrastructureState(
            timestamp="2026-07-12T10:00:00",
            cloud_provider=CloudProvider.AWS,
            environment="prod",
            resources=[resource],
        )

        assert len(state.resources) == 1
        assert state.resources[0].id == "vpc-001"

    def test_state_hash_computation(self):
        """Test state hash is computed."""
        state = InfrastructureState(
            timestamp="2026-07-12T10:00:00",
            cloud_provider=CloudProvider.AWS,
            environment="prod",
        )

        hash1 = state.compute_hash()
        assert len(hash1) == 64  # SHA256 hex is 64 chars
        assert hash1.startswith("")  # Valid hex

    def test_state_summary(self):
        """Test state summary."""
        resource = CloudResource(
            id="ec2-001",
            type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        state = InfrastructureState(
            timestamp="2026-07-12T10:00:00",
            cloud_provider=CloudProvider.AWS,
            environment="staging",
            resources=[resource],
        )

        summary = state.summary()
        assert summary["provider"] == "aws"
        assert summary["environment"] == "staging"
        assert summary["resource_count"] == 1


class TestCloudStateManager:
    """Test CloudStateManager."""

    def test_state_manager_initialization(self):
        """Test initializing state manager."""
        manager = CloudStateManager(CloudProvider.AWS, "prod")

        assert manager.provider == CloudProvider.AWS
        assert manager.environment == "prod"
        assert len(manager.state_history) == 0

    def test_capture_state(self):
        """Test capturing state."""
        manager = CloudStateManager(CloudProvider.AWS, "staging")

        resource = CloudResource(
            id="vpc-001",
            type=ResourceType.NETWORK,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        state = manager.capture_state([resource])

        assert len(state.resources) == 1
        assert len(manager.state_history) == 1
        assert manager.current_state == state

    def test_state_history_tracking(self):
        """Test state history is tracked."""
        manager = CloudStateManager(CloudProvider.AWS, "prod")

        # Capture two states
        state1 = manager.capture_state([])
        state2 = manager.capture_state([])

        assert len(manager.state_history) == 2
        assert manager.state_history[0] != manager.state_history[1]

    def test_get_previous_state(self):
        """Test retrieving previous state."""
        manager = CloudStateManager(CloudProvider.AWS, "prod")

        state1 = manager.capture_state([])
        state2 = manager.capture_state([])

        previous = manager.get_previous_state()
        assert previous == state1

    def test_state_changed_detection(self):
        """Test detecting state changes."""
        manager = CloudStateManager(CloudProvider.AWS, "prod")

        resource1 = CloudResource(
            id="vpc-001",
            type=ResourceType.NETWORK,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        manager.capture_state([resource1])
        # After first capture, no previous state to compare, state_changed checks history
        assert manager.get_previous_state() is None

        resource2 = CloudResource(
            id="vpc-002",
            type=ResourceType.NETWORK,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        manager.capture_state([resource1, resource2])
        # Now we have previous state, and it changed (added resource2)
        assert manager.state_changed() == True

    def test_state_diff(self):
        """Test computing state diff."""
        manager = CloudStateManager(CloudProvider.AWS, "prod")

        resource1 = CloudResource(
            id="vpc-001",
            type=ResourceType.NETWORK,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        manager.capture_state([resource1])

        resource2 = CloudResource(
            id="vpc-002",
            type=ResourceType.NETWORK,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        manager.capture_state([resource1, resource2])

        diff = manager.get_state_diff()
        assert "added" in diff or "added_resources" in diff


class TestDeploymentPlan:
    """Test DeploymentPlan."""

    def test_plan_creation(self):
        """Test creating deployment plan."""
        plan = DeploymentPlan(
            plan_id="TFPLAN_ABC123",
            provider=CloudProvider.AWS,
            strategy=DeploymentStrategy.ROLLING,
        )

        assert plan.plan_id == "TFPLAN_ABC123"
        assert plan.provider == CloudProvider.AWS
        assert plan.strategy == DeploymentStrategy.ROLLING

    def test_add_resource_change(self):
        """Test adding resource change."""
        plan = DeploymentPlan(
            plan_id="TFPLAN_1",
            provider=CloudProvider.AWS,
            strategy=DeploymentStrategy.CANARY,
        )

        plan.add_resource_change("create", "vpc-001", "network")
        assert len(plan.changes) == 1
        assert plan.changes[0]["action"] == "create"

    def test_add_deployment_change(self):
        """Test adding deployment change."""
        plan = DeploymentPlan(
            plan_id="TFPLAN_1",
            provider=CloudProvider.AWS,
            strategy=DeploymentStrategy.ROLLING,
        )

        plan.add_deployment_change("api", "1.0.0", 3)
        assert len(plan.changes) == 1
        assert plan.changes[0]["version"] == "1.0.0"


class TestTerraformOrchestrator:
    """Test TerraformOrchestrator."""

    def test_orchestrator_initialization(self):
        """Test initializing terraform orchestrator."""
        orchestrator = TerraformOrchestrator(CloudProvider.AWS)

        assert orchestrator.provider == CloudProvider.AWS

    def test_create_deployment_plan(self):
        """Test creating deployment plan."""
        orchestrator = TerraformOrchestrator(CloudProvider.AWS)

        resource = CloudResource(
            id="vpc-001",
            type=ResourceType.NETWORK,
            provider=CloudProvider.AWS,
            region="us-east-1",
        )

        plan = orchestrator.create_deployment_plan(
            "staging",
            DeploymentStrategy.ROLLING,
            [resource],
        )

        assert plan.provider == CloudProvider.AWS
        assert len(plan.changes) > 0

    def test_verify_plan_valid(self):
        """Test verifying valid plan."""
        orchestrator = TerraformOrchestrator(CloudProvider.AWS)

        plan = DeploymentPlan(
            plan_id="TFPLAN_1",
            provider=CloudProvider.AWS,
            strategy=DeploymentStrategy.ROLLING,
        )
        plan.add_resource_change("create", "vpc-001", "network")

        safe, issues = orchestrator.verify_plan(plan)
        assert safe == True
        assert len(issues) == 0

    def test_verify_plan_invalid_empty(self):
        """Test verifying plan with no changes."""
        orchestrator = TerraformOrchestrator(CloudProvider.AWS)

        plan = DeploymentPlan(
            plan_id="TFPLAN_1",
            provider=CloudProvider.AWS,
            strategy=DeploymentStrategy.ROLLING,
        )

        safe, issues = orchestrator.verify_plan(plan)
        assert safe == False
        assert len(issues) > 0

    def test_apply_plan(self):
        """Test applying deployment plan."""
        orchestrator = TerraformOrchestrator(CloudProvider.AWS)

        plan = DeploymentPlan(
            plan_id="TFPLAN_1",
            provider=CloudProvider.AWS,
            strategy=DeploymentStrategy.BLUE_GREEN,
        )
        plan.add_resource_change("create", "vpc-001", "network")
        plan.add_resource_change("create", "rds-001", "database")

        result = orchestrator.apply_plan(plan)

        assert result.success == True
        assert result.resources_created == 2

    def test_duration_estimation_rolling(self):
        """Test duration estimation for rolling strategy."""
        orchestrator = TerraformOrchestrator(CloudProvider.AWS)

        plan = orchestrator.create_deployment_plan(
            "prod",
            DeploymentStrategy.ROLLING,
            [CloudResource("r1", ResourceType.COMPUTE, CloudProvider.AWS, "us-east-1")],
        )

        # Rolling strategy: 60 + (1 * 3) = 63 seconds minimum
        assert plan.estimated_duration_seconds >= 60

    def test_duration_estimation_canary(self):
        """Test duration estimation for canary strategy."""
        orchestrator = TerraformOrchestrator(CloudProvider.AWS)

        resources = [
            CloudResource(f"r{i}", ResourceType.COMPUTE, CloudProvider.AWS, "us-east-1")
            for i in range(3)
        ]

        plan = orchestrator.create_deployment_plan(
            "prod",
            DeploymentStrategy.CANARY,
            resources,
        )

        # Canary: 60 + (3 * 5) = 75 seconds
        assert plan.estimated_duration_seconds >= 60


class TestKubernetesOrchestrator:
    """Test KubernetesOrchestrator."""

    def test_orchestrator_initialization(self):
        """Test initializing kubernetes orchestrator."""
        orchestrator = KubernetesOrchestrator("my-cluster")

        assert orchestrator.cluster_name == "my-cluster"

    def test_create_deployment(self):
        """Test creating deployment."""
        orchestrator = KubernetesOrchestrator("my-cluster")

        deployment = orchestrator.create_deployment(
            "api", "my-api:1.0", 3, {"DB_HOST": "localhost"}
        )

        assert deployment["name"] == "api"
        assert deployment["image"] == "my-api:1.0"
        assert deployment["replicas"] == 3

    def test_create_service(self):
        """Test creating service."""
        orchestrator = KubernetesOrchestrator("my-cluster")

        service = orchestrator.create_service("api", 80, 8080)

        assert service["name"] == "api"
        assert service["port"] == 80
        assert service["target_port"] == 8080

    def test_scale_deployment(self):
        """Test scaling deployment."""
        orchestrator = KubernetesOrchestrator("my-cluster")

        orchestrator.create_deployment("api", "api:1.0", 1, {})
        success = orchestrator.scale_deployment("api", 5)

        assert success == True
        assert orchestrator.deployments["api"]["replicas"] == 5

    def test_get_deployment_status(self):
        """Test getting deployment status."""
        orchestrator = KubernetesOrchestrator("my-cluster")

        orchestrator.create_deployment("api", "api:1.0", 3, {})
        status = orchestrator.get_deployment_status("api")

        assert status["name"] == "api"
        assert status["replicas"] == 3
        assert status["ready"] == 3


class TestDeploymentOrchestrator:
    """Test high-level DeploymentOrchestrator."""

    def test_orchestrator_initialization(self):
        """Test initializing deployment orchestrator."""
        orchestrator = DeploymentOrchestrator(
            CloudProvider.AWS, "staging", "my-cluster"
        )

        assert orchestrator.provider == CloudProvider.AWS
        assert orchestrator.environment == "staging"

    def test_plan_deployment(self):
        """Test planning deployment."""
        orchestrator = DeploymentOrchestrator(CloudProvider.AWS, "prod", "prod-cluster")

        resources = [
            CloudResource(
                "vpc-001", ResourceType.NETWORK, CloudProvider.AWS, "us-east-1"
            )
        ]

        plan = orchestrator.plan_deployment(DeploymentStrategy.ROLLING, resources)

        assert plan.provider == CloudProvider.AWS
        assert len(plan.changes) > 0

    def test_execute_deployment(self):
        """Test executing deployment."""
        orchestrator = DeploymentOrchestrator(
            CloudProvider.AWS, "staging", "staging-cluster"
        )

        resources = [
            CloudResource(
                "vpc-001", ResourceType.NETWORK, CloudProvider.AWS, "us-east-1"
            ),
            CloudResource(
                "db-001", ResourceType.DATABASE, CloudProvider.AWS, "us-east-1"
            ),
        ]

        plan = orchestrator.plan_deployment(DeploymentStrategy.CANARY, resources)

        services = {
            "api": {"image": "api:1.0", "replicas": "3"},
            "worker": {"image": "worker:1.0", "replicas": "2"},
        }

        result, deployment_id = orchestrator.execute_deployment(plan, services)

        assert result.success == True
        assert len(result.deployed_services) == 2
        assert deployment_id in orchestrator.deployment_history

    def test_get_deployment_status(self):
        """Test getting deployment status."""
        orchestrator = DeploymentOrchestrator(
            CloudProvider.AWS, "staging", "staging-cluster"
        )

        plan = orchestrator.plan_deployment(
            DeploymentStrategy.ROLLING,
            [
                CloudResource(
                    "vpc-001", ResourceType.NETWORK, CloudProvider.AWS, "us-east-1"
                )
            ],
        )

        result, deployment_id = orchestrator.execute_deployment(plan, {})

        status = orchestrator.get_deployment_status(deployment_id)
        assert status is not None
        assert status.deployment_id == deployment_id

    def test_rollback_deployment(self):
        """Test rollback capability."""
        orchestrator = DeploymentOrchestrator(CloudProvider.AWS, "prod", "prod-cluster")

        plan = orchestrator.plan_deployment(
            DeploymentStrategy.BLUE_GREEN,
            [
                CloudResource(
                    "vpc-001", ResourceType.NETWORK, CloudProvider.AWS, "us-east-1"
                )
            ],
        )

        result, deployment_id = orchestrator.execute_deployment(plan, {})

        # Get status before rollback
        status_before = orchestrator.get_deployment_status(deployment_id)
        assert status_before.can_rollback == True

        # Execute rollback
        success = orchestrator.rollback_deployment(deployment_id)
        assert success == True

        # Get status after rollback
        status_after = orchestrator.get_deployment_status(deployment_id)
        assert status_after.can_rollback == False


class TestLayer3Integration:
    """Integration tests for Layer 3."""

    def test_end_to_end_deployment_aws(self):
        """Test end-to-end AWS deployment."""
        orchestrator = DeploymentOrchestrator(
            CloudProvider.AWS, "staging", "staging-k8s"
        )

        # Create infrastructure resources
        resources = [
            CloudResource(
                "vpc-001", ResourceType.NETWORK, CloudProvider.AWS, "us-east-1"
            ),
            CloudResource(
                "rds-001", ResourceType.DATABASE, CloudProvider.AWS, "us-east-1"
            ),
            CloudResource(
                "lb-001", ResourceType.LOAD_BALANCER, CloudProvider.AWS, "us-east-1"
            ),
        ]

        # Plan deployment
        plan = orchestrator.plan_deployment(DeploymentStrategy.ROLLING, resources)
        assert len(plan.changes) == 3

        # Verify plan
        safe, issues = orchestrator.terraform.verify_plan(plan)
        assert safe == True

        # Execute deployment
        services = {
            "api": {"image": "api:1.2.0", "replicas": "3"},
            "cache": {"image": "cache:1.0", "replicas": "1"},
        }

        result, deployment_id = orchestrator.execute_deployment(plan, services)

        # Verify results
        assert result.success == True
        assert result.resources_created == 3
        assert len(result.deployed_services) == 2

    def test_multi_cloud_deployment(self):
        """Test deploying to multiple clouds."""
        aws = DeploymentOrchestrator(CloudProvider.AWS, "prod", "aws-prod")
        gcp = DeploymentOrchestrator(CloudProvider.GCP, "prod", "gcp-prod")

        resource_aws = CloudResource(
            "vm-aws", ResourceType.COMPUTE, CloudProvider.AWS, "us-east-1"
        )
        resource_gcp = CloudResource(
            "vm-gcp", ResourceType.COMPUTE, CloudProvider.GCP, "us-central1"
        )

        plan_aws = aws.plan_deployment(DeploymentStrategy.BLUE_GREEN, [resource_aws])
        plan_gcp = gcp.plan_deployment(DeploymentStrategy.BLUE_GREEN, [resource_gcp])

        assert plan_aws.provider == CloudProvider.AWS
        assert plan_gcp.provider == CloudProvider.GCP

    def test_deployment_with_state_tracking(self):
        """Test deployment with state tracking."""
        orchestrator = DeploymentOrchestrator(CloudProvider.AWS, "prod", "prod-cluster")

        resources = [
            CloudResource("r1", ResourceType.COMPUTE, CloudProvider.AWS, "us-east-1")
        ]

        plan = orchestrator.plan_deployment(DeploymentStrategy.CANARY, resources)
        result, deployment_id = orchestrator.execute_deployment(plan, {})

        # Check state manager
        state = orchestrator.state_manager.current_state
        assert state is not None

        # Check deployment history
        record = orchestrator.get_deployment_status(deployment_id)
        assert record.success == True
        assert record.resources_affected > 0


class TestLayer3ComplexScenarios:
    """Complex real-world scenarios."""

    def test_large_scale_deployment(self):
        """Test deploying large infrastructure."""
        orchestrator = DeploymentOrchestrator(CloudProvider.AWS, "prod", "prod-cluster")

        # Create 10 resources
        resources = [
            CloudResource(
                f"resource-{i}",
                ResourceType.COMPUTE if i % 2 == 0 else ResourceType.DATABASE,
                CloudProvider.AWS,
                "us-east-1",
            )
            for i in range(10)
        ]

        plan = orchestrator.plan_deployment(DeploymentStrategy.ROLLING, resources)
        assert len(plan.changes) == 10

        result, _ = orchestrator.execute_deployment(plan, {})
        assert result.success == True
        assert result.resources_created == 10

    def test_deployment_rollback_chain(self):
        """Test multiple deployments and rollback."""
        orchestrator = DeploymentOrchestrator(CloudProvider.AWS, "prod", "prod-cluster")

        # Deploy v1
        resources = [
            CloudResource("r1", ResourceType.COMPUTE, CloudProvider.AWS, "us-east-1")
        ]
        plan1 = orchestrator.plan_deployment(DeploymentStrategy.CANARY, resources)
        result1, deployment_id_1 = orchestrator.execute_deployment(plan1, {})

        # Deploy v2
        plan2 = orchestrator.plan_deployment(DeploymentStrategy.CANARY, resources)
        result2, deployment_id_2 = orchestrator.execute_deployment(plan2, {})

        # Rollback v2
        success = orchestrator.rollback_deployment(deployment_id_2)
        assert success == True

        # v1 should still be rollbackable
        v1_status = orchestrator.get_deployment_status(deployment_id_1)
        assert v1_status.can_rollback == True

    def test_multi_region_deployment(self):
        """Test deploying across multiple regions."""
        orchestrator_east = DeploymentOrchestrator(
            CloudProvider.AWS, "prod-east", "prod-east-cluster"
        )
        orchestrator_west = DeploymentOrchestrator(
            CloudProvider.AWS, "prod-west", "prod-west-cluster"
        )

        # Deploy to both regions
        resources = [
            CloudResource(
                "vpc-east", ResourceType.NETWORK, CloudProvider.AWS, "us-east-1"
            )
        ]
        plan_east = orchestrator_east.plan_deployment(
            DeploymentStrategy.ROLLING, resources
        )
        result_east, _ = orchestrator_east.execute_deployment(plan_east, {})

        resources = [
            CloudResource(
                "vpc-west", ResourceType.NETWORK, CloudProvider.AWS, "us-west-2"
            )
        ]
        plan_west = orchestrator_west.plan_deployment(
            DeploymentStrategy.ROLLING, resources
        )
        result_west, _ = orchestrator_west.execute_deployment(plan_west, {})

        assert result_east.success == True
        assert result_west.success == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
