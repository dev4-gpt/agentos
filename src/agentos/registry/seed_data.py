"""Seed data for AgentOS Registry - Real SaaS integrations and tool definitions.

This file contains production-ready tool definitions for major SaaS platforms.
Run this to populate the registry on startup or via CLI command.
"""

from agentos.models import AuthConfig, AuthType, Integration, ToolRecord

# ===========================================================================
# INTEGRATIONS - SaaS Platform Catalog
# ===========================================================================

INTEGRATIONS = [
    Integration(
        id="slack-integration",
        name="Slack",
        slug="slack",
        description="Team communication and collaboration platform",
        logo_url="https://a.slack-edge.com/6c404/marketing/img/meta/slack-hash-256.png",
        docs_url="https://api.slack.com/",
        base_url="https://slack.com/api",
        auth=AuthConfig(
            type=AuthType.OAUTH2,
            scopes=["chat:write", "channels:read", "users:read"],
            auth_url="https://slack.com/oauth/v2/authorize",
            token_url="https://slack.com/api/oauth.v2.access",
            onboarding_flow="oauth2_redirect",
            docs_url="https://api.slack.com/authentication/oauth-v2",
        ),
        categories=["communication", "productivity", "collaboration"],
        tool_count=5,
        is_active=True,
    ),
    Integration(
        id="stripe-integration",
        name="Stripe",
        slug="stripe",
        description="Payment processing and financial infrastructure",
        logo_url="https://images.ctfassets.net/fzn2n1nzq965/HTTOloNPhisV9P4hlMPNA/cacf1bb88b9fc492dfad34378d844280/Stripe_icon_-_square.svg",
        docs_url="https://stripe.com/docs/api",
        base_url="https://api.stripe.com/v1",
        auth=AuthConfig(
            type=AuthType.API_KEY,
            scopes=[],
            onboarding_flow="api_key_paste",
            docs_url="https://stripe.com/docs/keys",
        ),
        categories=["payments", "billing", "fintech"],
        tool_count=4,
        is_active=True,
    ),
    Integration(
        id="github-integration",
        name="GitHub",
        slug="github",
        description="Developer platform for version control and collaboration",
        logo_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        docs_url="https://docs.github.com/en/rest",
        base_url="https://api.github.com",
        auth=AuthConfig(
            type=AuthType.OAUTH2,
            scopes=["repo", "user", "workflow"],
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            onboarding_flow="oauth2_redirect",
            docs_url="https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps",
        ),
        categories=["developer-tools", "version-control", "collaboration"],
        tool_count=6,
        is_active=True,
    ),
    Integration(
        id="notion-integration",
        name="Notion",
        slug="notion",
        description="Connected workspace for notes, docs, and knowledge base",
        logo_url="https://upload.wikimedia.org/wikipedia/commons/4/45/Notion_app_logo.png",
        docs_url="https://developers.notion.com/",
        base_url="https://api.notion.com/v1",
        auth=AuthConfig(
            type=AuthType.OAUTH2,
            scopes=["read_content", "insert_content", "update_content"],
            auth_url="https://api.notion.com/v1/oauth/authorize",
            token_url="https://api.notion.com/v1/oauth/token",
            onboarding_flow="oauth2_redirect",
            docs_url="https://developers.notion.com/docs/authorization",
        ),
        categories=["productivity", "knowledge-management", "collaboration"],
        tool_count=4,
        is_active=True,
    ),
    Integration(
        id="linear-integration",
        name="Linear",
        slug="linear",
        description="Issue tracking and project management for software teams",
        logo_url="https://asset.brandfetch.io/id20mQyGeY/idZfsGJQsg.png",
        docs_url="https://developers.linear.app/",
        base_url="https://api.linear.app/graphql",
        auth=AuthConfig(
            type=AuthType.API_KEY,
            scopes=[],
            onboarding_flow="api_key_paste",
            docs_url="https://developers.linear.app/docs/graphql/working-with-the-graphql-api#personal-api-keys",
        ),
        categories=["project-management", "developer-tools", "productivity"],
        tool_count=5,
        is_active=True,
    ),
]

# ===========================================================================
# TOOLS - Individual API endpoints for each integration
# ===========================================================================

TOOLS = [
    # -----------------------------------------------------------------------
    # SLACK TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="slack-send-message",
        name="slack-send-message",
        description="Send a message to a Slack channel",
        input_schema={
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Channel ID or name"},
                "text": {"type": "string", "description": "Message text"},
                "thread_ts": {
                    "type": "string",
                    "description": "Thread timestamp to reply in thread",
                },
            },
            "required": ["channel", "text"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "ts": {"type": "string"},
                "channel": {"type": "string"},
            },
        },
        endpoint="https://slack.com/api/chat.postMessage",
        protocols=["http"],
        categories=["communication", "messaging"],
        tags=["slack", "chat", "message"],
        capabilities=["idempotent", "rate_limited"],
        authentication=AuthConfig(
            type=AuthType.OAUTH2,
            scopes=["chat:write"],
        ),
        mcp_tool_name="slack_send_message",
        integration_id="slack-integration",
    ),
    ToolRecord(
        id="slack-list-channels",
        name="slack-list-channels",
        description="List all Slack channels in the workspace",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 100},
                "types": {"type": "string", "default": "public_channel,private_channel"},
            },
        },
        endpoint="https://slack.com/api/conversations.list",
        protocols=["http"],
        categories=["communication"],
        tags=["slack", "channels"],
        capabilities=["paginated"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["channels:read"]),
        mcp_tool_name="slack_list_channels",
        integration_id="slack-integration",
    ),
    # -----------------------------------------------------------------------
    # STRIPE TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="stripe-create-customer",
        name="stripe-create-customer",
        description="Create a new customer in Stripe billing",
        input_schema={
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "metadata": {"type": "object"},
            },
            "required": ["email"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "email": {"type": "string"},
                "created": {"type": "integer"},
            },
        },
        endpoint="https://api.stripe.com/v1/customers",
        protocols=["http"],
        categories=["payments", "billing"],
        tags=["stripe", "customer", "billing"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="stripe_create_customer",
        integration_id="stripe-integration",
    ),
    ToolRecord(
        id="stripe-create-payment-intent",
        name="stripe-create-payment-intent",
        description="Create a payment intent to charge a customer",
        input_schema={
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "Amount in cents"},
                "currency": {"type": "string", "default": "usd"},
                "customer": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["amount", "currency"],
        },
        endpoint="https://api.stripe.com/v1/payment_intents",
        protocols=["http"],
        categories=["payments"],
        tags=["stripe", "payment", "charge"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="stripe_create_payment_intent",
        integration_id="stripe-integration",
    ),
    # -----------------------------------------------------------------------
    # GITHUB TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="github-create-issue",
        name="github-create-issue",
        description="Create a new issue in a GitHub repository",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "labels": {"type": "array", "items": {"type": "string"}},
                "assignees": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["owner", "repo", "title"],
        },
        endpoint="https://api.github.com/repos/{owner}/{repo}/issues",
        protocols=["http"],
        categories=["developer-tools", "project-management"],
        tags=["github", "issue", "bug-tracking"],
        capabilities=["rate_limited"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["repo"]),
        mcp_tool_name="github_create_issue",
        integration_id="github-integration",
    ),
    ToolRecord(
        id="github-list-pull-requests",
        name="github-list-pull-requests",
        description="List pull requests in a GitHub repository",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
            },
            "required": ["owner", "repo"],
        },
        endpoint="https://api.github.com/repos/{owner}/{repo}/pulls",
        protocols=["http"],
        categories=["developer-tools"],
        tags=["github", "pull-request", "code-review"],
        capabilities=["paginated", "rate_limited"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["repo"]),
        mcp_tool_name="github_list_pull_requests",
        integration_id="github-integration",
    ),
    # -----------------------------------------------------------------------
    # NOTION TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="notion-create-page",
        name="notion-create-page",
        description="Create a new page in a Notion database",
        input_schema={
            "type": "object",
            "properties": {
                "parent": {"type": "object", "properties": {"database_id": {"type": "string"}}},
                "properties": {"type": "object"},
                "children": {"type": "array"},
            },
            "required": ["parent"],
        },
        endpoint="https://api.notion.com/v1/pages",
        protocols=["http"],
        categories=["productivity", "knowledge-management"],
        tags=["notion", "page", "document"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["insert_content"]),
        mcp_tool_name="notion_create_page",
        integration_id="notion-integration",
    ),
    ToolRecord(
        id="notion-query-database",
        name="notion-query-database",
        description="Query a Notion database with filters and sorts",
        input_schema={
            "type": "object",
            "properties": {
                "database_id": {"type": "string"},
                "filter": {"type": "object"},
                "sorts": {"type": "array"},
            },
            "required": ["database_id"],
        },
        endpoint="https://api.notion.com/v1/databases/{database_id}/query",
        protocols=["http"],
        categories=["productivity", "data-retrieval"],
        tags=["notion", "database", "query"],
        capabilities=["paginated"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["read_content"]),
        mcp_tool_name="notion_query_database",
        integration_id="notion-integration",
    ),
    # -----------------------------------------------------------------------
    # LINEAR TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="linear-create-issue",
        name="linear-create-issue",
        description="Create a new issue in Linear",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "teamId": {"type": "string"},
                "priority": {"type": "integer", "minimum": 0, "maximum": 4},
                "assigneeId": {"type": "string"},
            },
            "required": ["title", "teamId"],
        },
        endpoint="https://api.linear.app/graphql",
        protocols=["graphql"],
        categories=["project-management", "issue-tracking"],
        tags=["linear", "issue", "task"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="linear_create_issue",
        integration_id="linear-integration",
    ),
    ToolRecord(
        id="linear-list-issues",
        name="linear-list-issues",
        description="List issues in Linear with optional filters",
        input_schema={
            "type": "object",
            "properties": {
                "teamId": {"type": "string"},
                "state": {"type": "string"},
                "assigneeId": {"type": "string"},
            },
        },
        endpoint="https://api.linear.app/graphql",
        protocols=["graphql"],
        categories=["project-management"],
        tags=["linear", "issues", "list"],
        capabilities=["paginated"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="linear_list_issues",
        integration_id="linear-integration",
    ),
]
