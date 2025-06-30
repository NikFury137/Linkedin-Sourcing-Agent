"""
AI Sourcing Agent - Main Application
====================================

An advanced AI-powered sourcing agent that automates supplier discovery,
evaluation, and risk assessment using multi-agent collaboration.

Features:
- Automated supplier research and discovery
- Comprehensive supplier evaluation with multiple criteria
- Risk assessment and compliance checking
- Detailed sourcing reports and recommendations
- Real-time market analysis and pricing insights

Author: AI Sourcing Agent Team
License: MIT
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, List
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom modules
from src.crew_manager import SourcingCrewManager
from src.utils.config import Config
from src.utils.logger import setup_logger

# Initialize console and logger
console = Console()
logger = setup_logger()

# Create Typer app
app = typer.Typer(
    name="ai-sourcing-agent",
    help="AI-powered sourcing agent for automated supplier discovery and evaluation",
    add_completion=False,
)

class SourcingAgent:
    """Main AI Sourcing Agent class"""

    def __init__(self):
        self.config = Config()
        self.crew_manager = SourcingCrewManager()
        self.console = Console()

    def display_banner(self):
        """Display application banner"""
        banner = """
╭─────────────────────────────────────────────────────────────────╮
│                                                                 │
│      🤖 AI SOURCING AGENT - SYNAPSE HACKATHON 2025 🤖          │
│                                                                 │
│  ⚡ Automated Supplier Discovery & Evaluation                   │
│  📊 Risk Assessment & Compliance Checking                       │
│  📈 Market Analysis & Pricing Insights                          │
│  🎯 Multi-Agent Collaborative Intelligence                      │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯
        """
        self.console.print(banner, style="bold blue")

    async def run_sourcing_analysis(self, 
                                  product_category: str,
                                  budget_range: str,
                                  location_preference: str = "Global",
                                  sustainability_requirements: bool = True,
                                  quality_standards: List[str] = None):
        """Run comprehensive sourcing analysis"""

        self.display_banner()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:

            # Step 1: Initialize crew
            task1 = progress.add_task("🚀 Initializing AI Sourcing Crew...", total=None)
            await asyncio.sleep(1)

            # Step 2: Research suppliers
            progress.update(task1, description="🔍 Researching suppliers...")
            suppliers = await self.crew_manager.research_suppliers(
                product_category, location_preference
            )

            # Step 3: Analyze suppliers
            progress.update(task1, description="📊 Analyzing supplier capabilities...")
            analysis = await self.crew_manager.analyze_suppliers(
                suppliers, quality_standards or []
            )

            # Step 4: Assess risks
            progress.update(task1, description="⚠️  Assessing supplier risks...")
            risk_assessment = await self.crew_manager.assess_risks(suppliers)

            # Step 5: Generate report
            progress.update(task1, description="📄 Generating comprehensive report...")
            report = await self.crew_manager.generate_report(
                suppliers, analysis, risk_assessment, 
                product_category, budget_range, sustainability_requirements
            )

            progress.update(task1, description="✅ Analysis complete!")

        return report

    def display_results(self, report: dict):
        """Display sourcing results in a formatted table"""

        self.console.print("\n🎯 SOURCING ANALYSIS RESULTS", style="bold green")
        self.console.print("="*50, style="green")

        # Summary table
        summary_table = Table(title="📊 Executive Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")

        summary_table.add_row("Suppliers Found", str(report.get('total_suppliers', 0)))
        summary_table.add_row("Recommended Suppliers", str(report.get('recommended_count', 0)))
        summary_table.add_row("Risk Level", report.get('overall_risk_level', 'Unknown'))
        summary_table.add_row("Estimated Savings", report.get('estimated_savings', 'N/A'))

        self.console.print(summary_table)

        # Top suppliers table
        if 'top_suppliers' in report:
            suppliers_table = Table(title="🏆 Top Recommended Suppliers")
            suppliers_table.add_column("Rank", style="cyan")
            suppliers_table.add_column("Supplier Name", style="yellow")
            suppliers_table.add_column("Country", style="green")
            suppliers_table.add_column("Score", style="magenta")
            suppliers_table.add_column("Risk Level", style="red")

            for i, supplier in enumerate(report['top_suppliers'][:5], 1):
                suppliers_table.add_row(
                    str(i),
                    supplier.get('name', 'Unknown'),
                    supplier.get('country', 'Unknown'),
                    f"{supplier.get('score', 0):.1f}/10",
                    supplier.get('risk_level', 'Unknown')
                )

            self.console.print(suppliers_table)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sourcing_report_{timestamp}.json"

        os.makedirs("data/reports", exist_ok=True)
        with open(f"data/reports/{filename}", "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.console.print(f"\n💾 Full report saved to: data/reports/{filename}", style="green")

@app.command()
def analyze(
    product: str = typer.Argument(..., help="Product category to source (e.g., 'electronic components')"),
    budget: str = typer.Option("$10,000-$50,000", "--budget", "-b", help="Budget range"),
    location: str = typer.Option("Global", "--location", "-l", help="Location preference"),
    sustainability: bool = typer.Option(True, "--sustainability", "-s", help="Include sustainability requirements"),
    quality: Optional[str] = typer.Option(None, "--quality", "-q", help="Quality standards (comma-separated)")
):
    """
    Run AI-powered sourcing analysis for a specific product category

    Example:
        python main.py analyze "industrial sensors" --budget "$20,000-$100,000" --location "Asia"
    """

    # Parse quality standards
    quality_standards = []
    if quality:
        quality_standards = [q.strip() for q in quality.split(",")]

    # Create and run sourcing agent
    agent = SourcingAgent()

    try:
        # Run async analysis
        report = asyncio.run(agent.run_sourcing_analysis(
            product_category=product,
            budget_range=budget,
            location_preference=location,
            sustainability_requirements=sustainability,
            quality_standards=quality_standards
        ))

        # Display results
        agent.display_results(report)

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        logger.error(f"Sourcing analysis failed: {e}")
        raise typer.Exit(1)

@app.command()
def dashboard():
    """Launch the interactive web dashboard"""
    console.print("🚀 Launching AI Sourcing Agent Dashboard...", style="bold blue")

    try:
        import subprocess
        subprocess.run(["streamlit", "run", "src/web/dashboard.py"])
    except Exception as e:
        console.print(f"❌ Error launching dashboard: {str(e)}", style="bold red")
        console.print("💡 Try running: pip install streamlit", style="yellow")

@app.command()
def setup():
    """Setup the AI Sourcing Agent environment"""
    console.print("🔧 Setting up AI Sourcing Agent...", style="bold blue")

    # Create necessary directories
    directories = [
        "data/suppliers",
        "data/reports", 
        "data/templates",
        "logs"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        console.print(f"✅ Created directory: {directory}")

    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""# AI Sourcing Agent Configuration
# Add your API keys here

# OpenAI API Key (for GPT models)
OPENAI_API_KEY=your_openai_key_here

# Google Gemini API Key (alternative to OpenAI)
GOOGLE_API_KEY=your_google_key_here

# Tavily Search API Key (for web search)
TAVILY_API_KEY=your_tavily_key_here

# Serper API Key (for Google search)
SERPER_API_KEY=your_serper_key_here

# Application Settings
LOG_LEVEL=INFO
CACHE_ENABLED=true
MAX_SUPPLIERS=50
""")
        console.print("✅ Created .env file template")
        console.print("📝 Please edit .env file and add your API keys", style="yellow")

    console.print("🎉 Setup complete! Run 'python main.py analyze --help' to get started.", style="bold green")

if __name__ == "__main__":
    app()
