"""
Manual test for envs command - demonstrates the full workflow

Run this file to see the envs command in action:
    uv run python testsManual/test_envs_demo.py

This test:
1. Creates a realistic MCI schema with main tools, toolsets, and MCP servers
2. Demonstrates the table format output
3. Generates a .env.example.mci file
4. Shows how the command helps developers understand required environment variables
"""

import json
import tempfile
from pathlib import Path

from rich.console import Console

console = Console()


def create_demo_schema():
    """Create a realistic MCI schema for demonstration."""
    tmpdir = Path(tempfile.mkdtemp())
    console.print(f"\n[blue]Creating demo schema in: {tmpdir}[/blue]\n")

    # Create main schema with various env variable references
    main_schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "E-Commerce API Integration",
            "description": "MCI configuration for e-commerce platform integration",
        },
        "tools": [
            {
                "name": "create_order",
                "description": "Create a new order in the e-commerce system",
                "tags": ["api", "orders"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "items": {"type": "array"},
                        "total": {"type": "number"},
                    },
                    "required": ["customer_id", "items", "total"],
                },
                "execution": {
                    "type": "http",
                    "method": "POST",
                    "url": "{{env.ECOMMERCE_API_URL}}/orders",
                    "headers": {
                        "Authorization": "Bearer {{env.ECOMMERCE_API_KEY}}",
                        "X-Shop-ID": "{{env.SHOP_ID}}",
                    },
                },
            },
            {
                "name": "send_notification",
                "description": "Send customer notification",
                "tags": ["notifications"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customer_email": {"type": "string"},
                        "message": {"type": "string"},
                    },
                },
                "execution": {
                    "type": "cli",
                    "command": "mail",
                    "args": ["-s", "Order Update", "{{props.customer_email}}"],
                    "cwd": "{{env.PROJECT_ROOT}}",
                },
            },
            {
                "name": "export_report",
                "description": "Export sales report",
                "tags": ["reports"],
                "inputSchema": {"type": "object", "properties": {"month": {"type": "string"}}},
                "execution": {
                    "type": "file",
                    "path": "{{env.REPORTS_DIR}}/template.txt",
                },
                "directoryAllowList": ["{{env.REPORTS_DIR}}"],
            },
        ],
        "toolsets": ["payments", "analytics"],
        "mcp_servers": {
            "slack": {
                "type": "http",
                "url": "{{env.SLACK_MCP_URL}}",
                "headers": {
                    "Authorization": "Bearer {{env.SLACK_BOT_TOKEN}}",
                },
            },
            "database": {
                "command": "uvx",
                "args": ["mcix", "run", "--file", "db.mci.json"],
                "env": {
                    "DB_CONNECTION_STRING": "{{env.DATABASE_URL}}",
                    "DB_POOL_SIZE": "{{env.DB_POOL_SIZE}}",
                },
            },
        },
        "directoryAllowList": ["{{env.ALLOWED_BASE_DIR}}"],
    }

    main_file = tmpdir / "ecommerce.mci.json"
    main_file.write_text(json.dumps(main_schema, indent=2))
    console.print(f"✓ Created main schema: {main_file}")

    # Create toolsets directory
    mci_dir = tmpdir / "mci"
    mci_dir.mkdir()

    # Payments toolset
    payments_schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Payment Processing Tools",
            "description": "Tools for handling payments",
        },
        "tools": [
            {
                "name": "process_payment",
                "description": "Process a payment transaction",
                "tags": ["payments"],
                "execution": {
                    "type": "http",
                    "method": "POST",
                    "url": "{{env.PAYMENT_GATEWAY_URL}}/charge",
                    "headers": {
                        "X-API-Key": "{{env.PAYMENT_API_KEY}}",
                        "X-Secret": "{{env.PAYMENT_SECRET}}",
                    },
                },
            },
            {
                "name": "refund_payment",
                "description": "Process a refund",
                "tags": ["payments", "refunds"],
                "execution": {
                    "type": "http",
                    "method": "POST",
                    "url": "{{env.PAYMENT_GATEWAY_URL}}/refund",
                    "headers": {
                        "X-API-Key": "{{env.PAYMENT_API_KEY}}",
                    },
                },
            },
        ],
    }
    (mci_dir / "payments.mci.json").write_text(json.dumps(payments_schema, indent=2))
    console.print(f"✓ Created payments toolset")

    # Analytics toolset
    analytics_schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Analytics Tools",
            "description": "Tools for analytics and reporting",
        },
        "tools": [
            {
                "name": "track_event",
                "description": "Track analytics event",
                "tags": ["analytics"],
                "execution": {
                    "type": "http",
                    "method": "POST",
                    "url": "{{env.ANALYTICS_URL}}/track",
                    "headers": {
                        "Authorization": "Bearer {{env.ANALYTICS_TOKEN}}",
                        "X-Workspace": "{{env.ANALYTICS_WORKSPACE_ID}}",
                    },
                },
            },
        ],
    }
    (mci_dir / "analytics.mci.json").write_text(json.dumps(analytics_schema, indent=2))
    console.print(f"✓ Created analytics toolset\n")

    return main_file


def run_envs_command(schema_file: Path):
    """Run the envs command and display results."""
    import subprocess

    console.print("[bold cyan]═══ Running: uvx mcix envs (table format) ═══[/bold cyan]\n")

    # Run table format
    result = subprocess.run(
        ["uv", "run", "mcix", "envs", "--file", str(schema_file)],
        capture_output=True,
        text=True,
    )
    console.print(result.stdout)

    console.print("\n[bold cyan]═══ Running: uvx mcix envs --format=env ═══[/bold cyan]\n")

    # Run env format
    result = subprocess.run(
        ["uv", "run", "mcix", "envs", "--file", str(schema_file), "--format", "env"],
        capture_output=True,
        text=True,
        cwd=schema_file.parent,
    )
    console.print(result.stdout)

    # Display the generated .env file
    env_file = schema_file.parent / ".env.example.mci"
    if env_file.exists():
        console.print("\n[bold cyan]═══ Generated .env.example.mci ═══[/bold cyan]\n")
        console.print(env_file.read_text())


def main():
    """Run the demonstration."""
    console.print("\n[bold green]╔═══════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║    MCI Envs Command - Manual Demonstration       ║[/bold green]")
    console.print("[bold green]╚═══════════════════════════════════════════════════╝[/bold green]")

    console.print(
        "\n[yellow]This demo shows how the envs command helps you understand "
        "what environment variables your MCI configuration requires.[/yellow]\n"
    )

    # Create demo schema
    schema_file = create_demo_schema()

    # Run envs command
    run_envs_command(schema_file)

    console.print("\n[bold green]✓ Demo completed![/bold green]")
    console.print(
        "[dim]The envs command scanned the main schema, both toolsets (payments & analytics), "
        "and MCP server configurations to find all environment variable references.[/dim]"
    )
    console.print(
        "\n[yellow]💡 Tip:[/yellow] In a real project, commit .env.example.mci to your repo"
    )
    console.print(
        "   so team members know what environment variables they need to configure.\n"
    )


if __name__ == "__main__":
    main()
