import sys
import vertexai
from vertexai.preview import reasoning_engines
from vertexai.generative_models import Tool, grounding
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")


def deploy_gcp_dev_expert(project_id, data_store_id, location="us-central1"):
    """
    Deploy a new Vertex AI Agent Engine instance using the AG2 framework.
    """
    staging_bucket = f"gs://{project_id}-staging"
    logger.info(
        f"Initializing Vertex AI for project: {project_id} in {location} with bucket: {staging_bucket}"
    )
    vertexai.init(project=project_id, location=location, staging_bucket=staging_bucket)

    # Configure Vertex AI Search grounding
    # We use the Tool.from_retrieval which is the standard way to
    # provide Vertex AI Search grounding to Reasoning Engine agents.
    logger.info(f"Configuring grounding for Data Store: {data_store_id}")
    search_tool = Tool.from_retrieval(
        grounding.Retrieval(
            source=grounding.VertexAISearch(
                datastore=data_store_id,
                project=project_id,
                location="global",
            )
        )
    )

    # Initialize the AG2 Agent (Agentic Graph)
    # The 'Ag2' template uses the AG2 (formerly AutoGen) framework.
    logger.info("Initializing AG2Agent instance...")
    agent = reasoning_engines.AG2Agent(
        model="gemini-1.5-pro",
        runnable_name="GCP-Dev-Expert",
        tools=[search_tool],
        system_instruction=(
            "You are GCP-Dev-Expert, an AI agent specialized in Google Cloud Platform. "
            "You leverage Vertex AI Search to access internal project documentation. "
            "Always ground your responses in the provided documentation."
        ),
    )

    # Deploy the Reasoning Engine instance
    logger.info("Deploying Reasoning Engine instance to Vertex AI...")
    try:
        remote_agent = reasoning_engines.ReasoningEngine.create(
            agent,
            display_name="GCP-Dev-Expert",
            description="Agent for delegating production tasks grounded in GCP project docs.",
            # Requirements must include ag2 and google-cloud-aiplatform
            requirements=[
                "google-cloud-aiplatform[reasoningengine,agent-engines]",
                "ag2",
            ],
        )

        resource_name = remote_agent.resource_name
        logger.success("Deployment successful!")
        logger.info(f"Resource Name: {resource_name}")

        return resource_name

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        return None


if __name__ == "__main__":
    PROJECT_ID = "gen-lang-client-0186657829"
    # Placeholder for Data Store ID
    DATA_STORE_ID = "gcp-docs-data-store"

    logger.info("Starting deployment of GCP-Dev-Expert...")
    endpoint_name = deploy_gcp_dev_expert(PROJECT_ID, DATA_STORE_ID)

    if endpoint_name:
        print(f"\n_DEPLOYMENT_SUCCESSFUL_: {endpoint_name}")
    else:
        print("\n_DEPLOYMENT_FAILED_")
        sys.exit(1)
