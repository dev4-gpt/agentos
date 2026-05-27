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
    # -----------------------------------------------------------------------
    # BATCH 1 - NEW INTEGRATIONS
    # -----------------------------------------------------------------------
    Integration(
        id="discord-integration",
        name="Discord",
        slug="discord",
        description="Community messaging and bot platform used by developers, gamers, and online communities. Agents can send messages, manage channels, and interact with servers.",
        logo_url="https://cdn.simpleicons.org/discord",
        docs_url="https://discord.com/developers/docs",
        base_url="https://discord.com/api/v10",
        auth=AuthConfig(
            type=AuthType.OAUTH2,
            scopes=["bot", "identify", "guilds", "messages.read"],
            auth_url="https://discord.com/api/oauth2/authorize",
            token_url="https://discord.com/api/oauth2/token",
            onboarding_flow="oauth2_redirect",
            docs_url="https://discord.com/developers/docs/topics/oauth2",
        ),
        categories=["communication", "community", "messaging"],
        tool_count=3,
        is_active=True,
    ),
    Integration(
        id="telegram-integration",
        name="Telegram",
        slug="telegram",
        description="Fast and secure messaging platform with a powerful bot API. Agents can send messages, photos, and receive updates through Telegram bots.",
        logo_url="https://cdn.simpleicons.org/telegram",
        docs_url="https://core.telegram.org/bots/api",
        base_url="https://api.telegram.org",
        auth=AuthConfig(
            type=AuthType.API_KEY,
            scopes=[],
            auth_url=None,
            token_url=None,
            onboarding_flow="api_key",
            docs_url="https://core.telegram.org/bots#how-do-i-create-a-bot",
        ),
        categories=["communication", "messaging", "bots"],
        tool_count=3,
        is_active=True,
    ),
    Integration(
        id="sendgrid-integration",
        name="SendGrid",
        slug="sendgrid",
        description="Twilio SendGrid is a cloud-based email delivery platform. Agents can send transactional emails, create templates, and validate email addresses programmatically.",
        logo_url="https://cdn.simpleicons.org/sendgrid",
        docs_url="https://docs.sendgrid.com/api-reference",
        base_url="https://api.sendgrid.com/v3",
        auth=AuthConfig(
            type=AuthType.API_KEY,
            scopes=[],
            auth_url=None,
            token_url=None,
            onboarding_flow="api_key",
            docs_url="https://docs.sendgrid.com/ui/account-and-settings/api-keys",
        ),
        categories=["email", "marketing", "communication"],
        tool_count=3,
        is_active=True,
    ),
    Integration(
        id="mailchimp-integration",
        name="Mailchimp",
        slug="mailchimp",
        description="Email marketing and automation platform. Agents can manage audiences, create campaigns, and track subscriber activity without human intervention.",
        logo_url="https://cdn.simpleicons.org/mailchimp",
        docs_url="https://mailchimp.com/developer/marketing/api/",
        base_url="https://us1.api.mailchimp.com/3.0",
        auth=AuthConfig(
            type=AuthType.OAUTH2,
            scopes=["basic"],
            auth_url="https://login.mailchimp.com/oauth2/authorize",
            token_url="https://login.mailchimp.com/oauth2/token",
            onboarding_flow="oauth2_redirect",
            docs_url="https://mailchimp.com/developer/marketing/guides/access-user-data-oauth-2/",
        ),
        categories=["email", "marketing", "automation"],
        tool_count=3,
        is_active=True,
    ),
    Integration(
        id="trello-integration",
        name="Trello",
        slug="trello",
        description="Visual project management tool using Kanban boards. Agents can create cards, manage boards, and update checklists to automate task tracking.",
        logo_url="https://cdn.simpleicons.org/trello",
        docs_url="https://developer.atlassian.com/cloud/trello/rest/",
        base_url="https://api.trello.com/1",
        auth=AuthConfig(
            type=AuthType.API_KEY,
            scopes=[],
            auth_url=None,
            token_url=None,
            onboarding_flow="api_key",
            docs_url="https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/",
        ),
        categories=["project-management", "productivity", "collaboration"],
        tool_count=3,
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
    # -----------------------------------------------------------------------
    # DISCORD TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="discord-send-message",
        name="discord-send-message",
        description="Send a text message to a specific Discord channel",
        input_schema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "The ID of the Discord channel to send the message to"},
                "content": {"type": "string", "description": "The text content of the message. Maximum 2000 characters."},
            },
            "required": ["channel_id", "content"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "The unique ID of the sent message"},
                "timestamp": {"type": "string", "description": "ISO timestamp of when the message was sent"},
                "channel_id": {"type": "string"},
            },
        },
        endpoint="https://discord.com/api/v10/channels/{channel_id}/messages",
        protocols=["http"],
        categories=["communication", "messaging"],
        tags=["discord", "message", "send", "chat"],
        capabilities=["rate_limited"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["bot"]),
        mcp_tool_name="discord_send_message",
        integration_id="discord-integration",
    ),
    ToolRecord(
        id="discord-create-channel",
        name="discord-create-channel",
        description="Create a new text or voice channel in a Discord server",
        input_schema={
            "type": "object",
            "properties": {
                "guild_id": {"type": "string", "description": "The ID of the Discord server (guild)"},
                "name": {"type": "string", "description": "Channel name, lowercase with hyphens (e.g. general-chat)"},
                "type": {"type": "integer", "description": "0 = text channel, 2 = voice channel", "default": 0},
            },
            "required": ["guild_id", "name"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string"},
                "name": {"type": "string"},
                "guild_id": {"type": "string"},
            },
        },
        endpoint="https://discord.com/api/v10/guilds/{guild_id}/channels",
        protocols=["http"],
        categories=["communication", "community"],
        tags=["discord", "channel", "create", "server"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["bot"]),
        mcp_tool_name="discord_create_channel",
        integration_id="discord-integration",
    ),
    ToolRecord(
        id="discord-get-messages",
        name="discord-get-messages",
        description="Retrieve recent messages from a Discord channel",
        input_schema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "The ID of the Discord channel to read messages from"},
                "limit": {"type": "integer", "description": "Number of messages to retrieve, max 100", "default": 10},
            },
            "required": ["channel_id"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "content": {"type": "string"},
                            "author": {"type": "string"},
                            "timestamp": {"type": "string"},
                        },
                    },
                },
            },
        },
        endpoint="https://discord.com/api/v10/channels/{channel_id}/messages",
        protocols=["http"],
        categories=["communication", "messaging"],
        tags=["discord", "messages", "read", "history"],
        capabilities=["paginated", "rate_limited"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["bot"]),
        mcp_tool_name="discord_get_messages",
        integration_id="discord-integration",
    ),
    # -----------------------------------------------------------------------
    # TELEGRAM TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="telegram-send-message",
        name="telegram-send-message",
        description="Send a text message to a Telegram chat or user via a Telegram bot",
        input_schema={
            "type": "object",
            "properties": {
                "chat_id": {"type": "string", "description": "Target chat ID or @username"},
                "text": {"type": "string", "description": "The message text to send"},
                "parse_mode": {"type": "string", "enum": ["Markdown", "HTML", ""], "default": ""},
            },
            "required": ["chat_id", "text"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "message_id": {"type": "integer"},
                "chat_id": {"type": "string"},
                "date": {"type": "integer", "description": "Unix timestamp of the message"},
            },
        },
        endpoint="https://api.telegram.org/bot{api_key}/sendMessage",
        protocols=["http"],
        categories=["communication", "messaging"],
        tags=["telegram", "message", "send", "bot"],
        capabilities=["rate_limited"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="telegram_send_message",
        integration_id="telegram-integration",
    ),
    ToolRecord(
        id="telegram-send-photo",
        name="telegram-send-photo",
        description="Send an image to a Telegram chat using a public URL",
        input_schema={
            "type": "object",
            "properties": {
                "chat_id": {"type": "string", "description": "The chat, group, or channel to send the photo to"},
                "photo": {"type": "string", "description": "A public HTTPS URL of the image (JPEG, PNG)"},
                "caption": {"type": "string", "description": "Optional text caption below the photo"},
            },
            "required": ["chat_id", "photo"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "message_id": {"type": "integer"},
                "photo_id": {"type": "string", "description": "Telegram internal file ID"},
            },
        },
        endpoint="https://api.telegram.org/bot{api_key}/sendPhoto",
        protocols=["http"],
        categories=["communication", "media"],
        tags=["telegram", "photo", "image", "bot"],
        capabilities=["rate_limited"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="telegram_send_photo",
        integration_id="telegram-integration",
    ),
    ToolRecord(
        id="telegram-get-updates",
        name="telegram-get-updates",
        description="Retrieve incoming messages and events sent to the Telegram bot",
        input_schema={
            "type": "object",
            "properties": {
                "offset": {"type": "integer", "description": "ID of first update to return, to avoid re-reading messages"},
                "limit": {"type": "integer", "description": "Max updates to retrieve, 1-100", "default": 10},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "updates": {"type": "array", "items": {"type": "object"}},
            },
        },
        endpoint="https://api.telegram.org/bot{api_key}/getUpdates",
        protocols=["http"],
        categories=["communication", "bots"],
        tags=["telegram", "updates", "read", "inbox"],
        capabilities=["paginated"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="telegram_get_updates",
        integration_id="telegram-integration",
    ),
    # -----------------------------------------------------------------------
    # SENDGRID TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="sendgrid-send-email",
        name="sendgrid-send-email",
        description="Send a transactional email through SendGrid",
        input_schema={
            "type": "object",
            "properties": {
                "to_email": {"type": "string", "description": "Recipient email address"},
                "to_name": {"type": "string", "description": "Recipient display name"},
                "from_email": {"type": "string", "description": "Sender email, must be verified in SendGrid"},
                "from_name": {"type": "string", "description": "Sender display name"},
                "subject": {"type": "string", "description": "Email subject line"},
                "content_html": {"type": "string", "description": "HTML body of the email"},
                "content_text": {"type": "string", "description": "Plain-text fallback body"},
            },
            "required": ["to_email", "from_email", "subject", "content_html"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "status_code": {"type": "integer", "description": "202 = accepted and queued"},
                "message_id": {"type": "string"},
            },
        },
        endpoint="https://api.sendgrid.com/v3/mail/send",
        protocols=["http"],
        categories=["email", "communication"],
        tags=["sendgrid", "email", "send", "transactional"],
        capabilities=["rate_limited"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="sendgrid_send_email",
        integration_id="sendgrid-integration",
    ),
    ToolRecord(
        id="sendgrid-create-template",
        name="sendgrid-create-template",
        description="Create a reusable email template in SendGrid",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Internal template name"},
                "generation": {"type": "string", "default": "dynamic"},
            },
            "required": ["name"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "template_id": {"type": "string"},
                "name": {"type": "string"},
            },
        },
        endpoint="https://api.sendgrid.com/v3/templates",
        protocols=["http"],
        categories=["email", "marketing"],
        tags=["sendgrid", "template", "email", "create"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="sendgrid_create_template",
        integration_id="sendgrid-integration",
    ),
    ToolRecord(
        id="sendgrid-validate-email",
        name="sendgrid-validate-email",
        description="Check if an email address is valid and deliverable before sending",
        input_schema={
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "The email address to validate"},
            },
            "required": ["email"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "valid": {"type": "boolean"},
                "verdict": {"type": "string", "description": "'Valid', 'Risky', or 'Invalid'"},
                "score": {"type": "number", "description": "Confidence score 0-1"},
                "suggestion": {"type": "string", "description": "Did-you-mean suggestion for typos"},
            },
        },
        endpoint="https://api.sendgrid.com/v3/validations/email",
        protocols=["http"],
        categories=["email", "validation"],
        tags=["sendgrid", "validate", "email", "deliverability"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="sendgrid_validate_email",
        integration_id="sendgrid-integration",
    ),
    # -----------------------------------------------------------------------
    # MAILCHIMP TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="mailchimp-add-subscriber",
        name="mailchimp-add-subscriber",
        description="Add a new contact to a Mailchimp audience (mailing list)",
        input_schema={
            "type": "object",
            "properties": {
                "list_id": {"type": "string", "description": "The Mailchimp audience ID"},
                "email_address": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["subscribed", "pending", "unsubscribed"],
                    "default": "subscribed",
                },
            },
            "required": ["list_id", "email_address"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "subscriber_id": {"type": "string"},
                "status": {"type": "string"},
                "email_address": {"type": "string"},
            },
        },
        endpoint="https://us1.api.mailchimp.com/3.0/lists/{list_id}/members",
        protocols=["http"],
        categories=["email", "marketing"],
        tags=["mailchimp", "subscriber", "add", "list", "audience"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["basic"]),
        mcp_tool_name="mailchimp_add_subscriber",
        integration_id="mailchimp-integration",
    ),
    ToolRecord(
        id="mailchimp-create-campaign",
        name="mailchimp-create-campaign",
        description="Create a new email marketing campaign in Mailchimp",
        input_schema={
            "type": "object",
            "properties": {
                "list_id": {"type": "string", "description": "The audience ID this campaign will be sent to"},
                "subject_line": {"type": "string"},
                "from_name": {"type": "string"},
                "reply_to": {"type": "string", "format": "email"},
                "campaign_type": {"type": "string", "default": "regular"},
            },
            "required": ["list_id", "subject_line", "from_name", "reply_to"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "status": {"type": "string"},
                "archive_url": {"type": "string"},
            },
        },
        endpoint="https://us1.api.mailchimp.com/3.0/campaigns",
        protocols=["http"],
        categories=["email", "marketing"],
        tags=["mailchimp", "campaign", "create", "newsletter"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["basic"]),
        mcp_tool_name="mailchimp_create_campaign",
        integration_id="mailchimp-integration",
    ),
    ToolRecord(
        id="mailchimp-get-lists",
        name="mailchimp-get-lists",
        description="Retrieve all mailing lists (audiences) in your Mailchimp account",
        input_schema={
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Number of lists to return", "default": 10},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "lists": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "member_count": {"type": "integer"},
                        },
                    },
                },
                "total_items": {"type": "integer"},
            },
        },
        endpoint="https://us1.api.mailchimp.com/3.0/lists",
        protocols=["http"],
        categories=["email", "marketing"],
        tags=["mailchimp", "lists", "audiences", "get"],
        capabilities=["paginated"],
        authentication=AuthConfig(type=AuthType.OAUTH2, scopes=["basic"]),
        mcp_tool_name="mailchimp_get_lists",
        integration_id="mailchimp-integration",
    ),
    # -----------------------------------------------------------------------
    # TRELLO TOOLS
    # -----------------------------------------------------------------------
    ToolRecord(
        id="trello-create-card",
        name="trello-create-card",
        description="Create a new card on a Trello board list",
        input_schema={
            "type": "object",
            "properties": {
                "idList": {"type": "string", "description": "The ID of the Trello list (column) to add this card to"},
                "name": {"type": "string", "description": "The title of the card"},
                "desc": {"type": "string", "description": "Card description, supports Markdown"},
                "due": {"type": "string", "description": "Due date in ISO 8601 format"},
                "pos": {"type": "string", "description": "'top', 'bottom', or a positive float", "default": "bottom"},
            },
            "required": ["idList", "name"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "string"},
                "card_url": {"type": "string", "description": "Direct URL to view the card in Trello"},
                "name": {"type": "string"},
            },
        },
        endpoint="https://api.trello.com/1/cards",
        protocols=["http"],
        categories=["project-management", "productivity"],
        tags=["trello", "card", "create", "task", "kanban"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="trello_create_card",
        integration_id="trello-integration",
    ),
    ToolRecord(
        id="trello-get-board-lists",
        name="trello-get-board-lists",
        description="Retrieve all lists (columns) on a Trello board",
        input_schema={
            "type": "object",
            "properties": {
                "board_id": {"type": "string", "description": "The ID of the Trello board, found in the board URL"},
            },
            "required": ["board_id"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "lists": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "closed": {"type": "boolean"},
                        },
                    },
                },
            },
        },
        endpoint="https://api.trello.com/1/boards/{board_id}/lists",
        protocols=["http"],
        categories=["project-management", "productivity"],
        tags=["trello", "lists", "board", "columns"],
        capabilities=["paginated"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="trello_get_board_lists",
        integration_id="trello-integration",
    ),
    ToolRecord(
        id="trello-update-card",
        name="trello-update-card",
        description="Update an existing Trello card — move it, rename it, or mark it complete",
        input_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "string", "description": "The ID of the Trello card to update"},
                "name": {"type": "string", "description": "New title for the card"},
                "desc": {"type": "string", "description": "New description for the card"},
                "idList": {"type": "string", "description": "Move card to this list ID"},
                "closed": {"type": "boolean", "description": "Set true to archive the card"},
            },
            "required": ["card_id"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "card_id": {"type": "string"},
                "name": {"type": "string"},
                "card_url": {"type": "string"},
                "list_id": {"type": "string"},
            },
        },
        endpoint="https://api.trello.com/1/cards/{card_id}",
        protocols=["http"],
        categories=["project-management", "productivity"],
        tags=["trello", "card", "update", "move", "edit"],
        capabilities=["idempotent"],
        authentication=AuthConfig(type=AuthType.API_KEY),
        mcp_tool_name="trello_update_card",
        integration_id="trello-integration",
    ),
]
