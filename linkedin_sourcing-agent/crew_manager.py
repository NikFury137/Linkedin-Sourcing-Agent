"""
Sourcing Crew Manager
====================

This module manages the coordination of multiple AI agents working together
to perform comprehensive supplier sourcing and evaluation.
"""

import asyncio
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from .agents.sourcing_researcher import SourcingResearcher
from .agents.supplier_analyst import SupplierAnalyst  
from .agents.risk_assessor import RiskAssessor
from .agents.report_generator import ReportGenerator
from .tools.web_search import WebSearchTool
from .tools.supplier_database import SupplierDatabaseTool
from .tools.compliance_checker import ComplianceCheckerTool
from .utils.config import Config
from .utils.logger import setup_logger

logger = setup_logger()

class SourcingCrewManager:
    """
    Manages the AI sourcing crew - coordinates multiple specialized agents
    to perform comprehensive supplier sourcing and evaluation.
    """

    def __init__(self):
        self.config = Config()
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.agents = self._create_agents()

    def _initialize_llm(self):
        """Initialize the language model"""
        try:
            if self.config.openai_api_key:
                return ChatOpenAI(
                    model_name="gpt-4",
                    temperature=0.1,
                    api_key=self.config.openai_api_key
                )
            elif self.config.google_api_key:
                return ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=0.1,
                    google_api_key=self.config.google_api_key
                )
            else:
                raise ValueError("No valid API key found for LLM initialization")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise

    def _initialize_tools(self):
        """Initialize all tools available to agents"""
        tools = {}

        try:
            # Web search tools
            if self.config.serper_api_key:
                tools['serper'] = SerperDevTool(api_key=self.config.serper_api_key)

            # Custom tools
            tools['web_search'] = WebSearchTool()
            tools['supplier_db'] = SupplierDatabaseTool()
            tools['compliance'] = ComplianceCheckerTool()
            tools['scraper'] = ScrapeWebsiteTool()

            logger.info(f"Initialized {len(tools)} tools")
            return tools

        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            return {}

    def _create_agents(self):
        """Create and configure all AI agents"""
        agents = {}

        try:
            # Sourcing Researcher Agent
            agents['researcher'] = Agent(
                role='Senior Sourcing Researcher',
                goal='Find and research potential suppliers for specific product categories',
                backstory="""You are an expert sourcing researcher with 15+ years of experience 
                in global supply chain management. You excel at discovering new suppliers, 
                analyzing market trends, and identifying emerging opportunities. Your research 
                is thorough, data-driven, and always considers geopolitical and economic factors.""",
                verbose=True,
                allow_delegation=False,
                llm=self.llm,
                tools=[
                    self.tools.get('serper'),
                    self.tools.get('web_search'),
                    self.tools.get('scraper')
                ]
            )

            # Supplier Analyst Agent  
            agents['analyst'] = Agent(
                role='Supplier Performance Analyst',
                goal='Evaluate supplier capabilities, quality, and performance metrics',
                backstory="""You are a meticulous supplier analyst with expertise in 
                evaluating supplier capabilities across multiple dimensions including quality, 
                capacity, financial stability, and operational excellence. You use data-driven 
                approaches to score and rank suppliers objectively.""",
                verbose=True,
                allow_delegation=False,
                llm=self.llm,
                tools=[
                    self.tools.get('supplier_db'),
                    self.tools.get('web_search')
                ]
            )

            # Risk Assessor Agent
            agents['risk_assessor'] = Agent(
                role='Supply Chain Risk Assessor',
                goal='Identify and evaluate potential risks associated with suppliers',
                backstory="""You are a seasoned risk management professional specializing 
                in supply chain risk assessment. You evaluate suppliers for financial, 
                operational, geopolitical, and compliance risks. Your assessments help 
                organizations make informed decisions and develop risk mitigation strategies.""",
                verbose=True,
                allow_delegation=False,
                llm=self.llm,
                tools=[
                    self.tools.get('compliance'),
                    self.tools.get('web_search')
                ]
            )

            # Report Generator Agent
            agents['reporter'] = Agent(
                role='Strategic Sourcing Report Writer',
                goal='Synthesize findings into comprehensive, actionable sourcing reports',
                backstory="""You are an expert business writer specializing in procurement 
                and sourcing reports. You excel at synthesizing complex data from multiple 
                sources into clear, actionable recommendations. Your reports are used by 
                C-level executives to make strategic sourcing decisions.""",
                verbose=True,
                allow_delegation=False,
                llm=self.llm,
                tools=[]
            )

            logger.info(f"Created {len(agents)} AI agents")
            return agents

        except Exception as e:
            logger.error(f"Failed to create agents: {e}")
            return {}

    async def research_suppliers(self, product_category: str, location_preference: str = "Global") -> List[Dict]:
        """Research and discover potential suppliers"""

        research_task = Task(
            description=f"""
            Research and identify potential suppliers for {product_category}.

            Your tasks:
            1. Search for suppliers specializing in {product_category}
            2. Focus on {location_preference} suppliers when possible
            3. Gather basic information: company name, location, website, specialties
            4. Look for both established companies and emerging suppliers
            5. Consider suppliers with different capabilities (OEM, contract manufacturing, distributors)

            Provide a structured list with at least 20 suppliers including:
            - Company name and location
            - Website and contact information  
            - Product specialties and capabilities
            - Years in business (if available)
            - Company size indicators
            """,
            agent=self.agents['researcher'],
            expected_output="Structured list of potential suppliers with detailed information"
        )

        # Create crew for research
        research_crew = Crew(
            agents=[self.agents['researcher']],
            tasks=[research_task],
            verbose=True,
            process=Process.sequential
        )

        try:
            result = research_crew.kickoff()
            # Parse result into structured format
            suppliers = self._parse_supplier_list(str(result))
            logger.info(f"Found {len(suppliers)} potential suppliers")
            return suppliers

        except Exception as e:
            logger.error(f"Supplier research failed: {e}")
            return []

    async def analyze_suppliers(self, suppliers: List[Dict], quality_standards: List[str]) -> Dict:
        """Analyze supplier capabilities and performance"""

        analysis_task = Task(
            description=f"""
            Analyze the following suppliers for capabilities and performance:

            Suppliers to analyze: {suppliers}
            Quality standards to consider: {quality_standards}

            For each supplier, evaluate:
            1. Product quality and certifications
            2. Manufacturing capabilities and capacity
            3. Financial stability indicators
            4. Customer reviews and reputation
            5. Innovation and technology adoption
            6. Pricing competitiveness
            7. Delivery and logistics capabilities
            8. Sustainability practices

            Score each supplier on a 1-10 scale for each criterion.
            Provide detailed analysis and recommendations.
            """,
            agent=self.agents['analyst'],
            expected_output="Comprehensive supplier analysis with scores and recommendations"
        )

        analysis_crew = Crew(
            agents=[self.agents['analyst']],
            tasks=[analysis_task],
            verbose=True,
            process=Process.sequential
        )

        try:
            result = analysis_crew.kickoff()
            analysis = self._parse_analysis_result(str(result))
            logger.info("Supplier analysis completed")
            return analysis

        except Exception as e:
            logger.error(f"Supplier analysis failed: {e}")
            return {}

    async def assess_risks(self, suppliers: List[Dict]) -> Dict:
        """Assess risks for each supplier"""

        risk_task = Task(
            description=f"""
            Conduct comprehensive risk assessment for these suppliers: {suppliers}

            Evaluate the following risk categories:
            1. Financial Risk - stability, creditworthiness, bankruptcy risk
            2. Operational Risk - capacity constraints, quality issues, delivery delays  
            3. Geopolitical Risk - political stability, trade restrictions, sanctions
            4. Compliance Risk - regulatory compliance, certifications, legal issues
            5. Cybersecurity Risk - data protection, system security
            6. Reputation Risk - public perception, scandals, controversies
            7. Supply Chain Risk - dependencies, single points of failure
            8. Environmental Risk - climate change impacts, sustainability issues

            For each supplier and risk category:
            - Assign risk level: LOW, MEDIUM, HIGH, CRITICAL
            - Provide specific risk factors and evidence
            - Suggest mitigation strategies
            """,
            agent=self.agents['risk_assessor'],
            expected_output="Detailed risk assessment matrix with mitigation recommendations"
        )

        risk_crew = Crew(
            agents=[self.agents['risk_assessor']],
            tasks=[risk_task],
            verbose=True,
            process=Process.sequential
        )

        try:
            result = risk_crew.kickoff()
            risk_assessment = self._parse_risk_assessment(str(result))
            logger.info("Risk assessment completed")
            return risk_assessment

        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {}

    async def generate_report(self, suppliers: List[Dict], analysis: Dict, 
                            risk_assessment: Dict, product_category: str,
                            budget_range: str, sustainability_requirements: bool) -> Dict:
        """Generate comprehensive sourcing report"""

        report_task = Task(
            description=f"""
            Create a comprehensive sourcing report based on the following data:

            Product Category: {product_category}
            Budget Range: {budget_range}
            Sustainability Required: {sustainability_requirements}

            Suppliers Found: {suppliers}
            Analysis Results: {analysis}
            Risk Assessment: {risk_assessment}

            Generate a professional report including:

            1. EXECUTIVE SUMMARY
               - Key findings and recommendations
               - Total suppliers evaluated
               - Top 3 recommended suppliers with rationale

            2. MARKET ANALYSIS
               - Market trends and insights
               - Pricing analysis and benchmarks
               - Supply availability assessment

            3. SUPPLIER RECOMMENDATIONS
               - Detailed profiles of top 5 suppliers
               - Scoring matrix with all evaluation criteria
               - Pros and cons for each supplier

            4. RISK ANALYSIS
               - Overall risk landscape
               - Specific risks by supplier
               - Risk mitigation strategies

            5. IMPLEMENTATION ROADMAP
               - Next steps and action items
               - Timeline for supplier engagement
               - Contract negotiation recommendations

            6. APPENDICES
               - Full supplier list with basic information
               - Detailed scoring methodology
               - Data sources and assumptions
            """,
            agent=self.agents['reporter'],
            expected_output="Professional sourcing report in structured format"
        )

        report_crew = Crew(
            agents=[self.agents['reporter']],
            tasks=[report_task],
            verbose=True,
            process=Process.sequential
        )

        try:
            result = report_crew.kickoff()
            report = self._parse_final_report(str(result))
            logger.info("Final report generated")
            return report

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {}

    def _parse_supplier_list(self, raw_result: str) -> List[Dict]:
        """Parse raw supplier research results into structured format"""
        # This would include parsing logic to extract structured data
        # For now, return mock data structure
        suppliers = []
        # Add parsing logic here based on the actual output format
        return suppliers

    def _parse_analysis_result(self, raw_result: str) -> Dict:
        """Parse supplier analysis results"""
        analysis = {
            'total_suppliers': 0,
            'analyzed_suppliers': [],
            'scoring_criteria': [],
            'average_scores': {}
        }
        # Add parsing logic here
        return analysis

    def _parse_risk_assessment(self, raw_result: str) -> Dict:
        """Parse risk assessment results"""
        risk_data = {
            'overall_risk_level': 'MEDIUM',
            'risk_categories': [],
            'supplier_risks': {},
            'mitigation_strategies': []
        }
        # Add parsing logic here
        return risk_data

    def _parse_final_report(self, raw_result: str) -> Dict:
        """Parse final report into structured format"""
        report = {
            'executive_summary': '',
            'total_suppliers': 0,
            'recommended_count': 0,
            'top_suppliers': [],
            'overall_risk_level': 'MEDIUM',
            'estimated_savings': 'TBD',
            'generated_at': str(asyncio.get_event_loop().time()),
            'full_report': raw_result
        }
        # Add parsing logic here
        return report
