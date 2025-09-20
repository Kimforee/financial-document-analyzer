## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai_tools import SerperDevTool
from crewai.tools import tool
from langchain_community.document_loaders import PyPDFLoader


## Creating search tool
search_tool = SerperDevTool()


## Creating custom pdf reader tool
class FinancialDocumentTool:
    @tool("Read financial document data")
    def read_data_tool(path: str = "data/sample.pdf") -> str:
        """Reads and cleans text from a financial PDF document.

        Args:
            path (str, optional): Path to the PDF file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Extracted and cleaned financial document text.
        """
        try:
            # If path is not provided or doesn't exist, use default sample file
            if not path or not os.path.exists(path):
                default_path = "data/sample.pdf"
                if os.path.exists(default_path):
                    path = default_path
                else:
                    return f"Error: Neither provided file ({path}) nor default file ({default_path}) found"

            docs = PyPDFLoader(file_path=path).load()
            full_report = ""

            for data in docs:
                content = data.page_content

                # Normalize whitespace
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")

                full_report += content.strip() + "\n"

            return full_report.strip()
        except Exception as e:
            return f"Error reading PDF: {e}"


## Creating Investment Analysis Tool
class InvestmentTool:
    @tool("Analyze investment data")
    def analyze_investment_tool(financial_document_data: str) -> str:
        """Analyzes investment data from financial document text.

        Args:
            financial_document_data (str): Extracted financial document text.

        Returns:
            str: Extracted insights or error message if processing fails.
        """
        if not financial_document_data:
            return "No financial data provided."

        # Clean up double spaces
        processed_data = " ".join(financial_document_data.split())
        
        # Extract key financial metrics
        analysis = []
        
        # Look for revenue patterns
        if "revenue" in processed_data.lower():
            analysis.append("• Revenue analysis: Document contains revenue data")
        
        # Look for profit/loss indicators
        if any(word in processed_data.lower() for word in ["profit", "income", "earnings", "net income"]):
            analysis.append("• Profitability: Document contains profit/income data")
        
        # Look for growth indicators
        if any(word in processed_data.lower() for word in ["growth", "increase", "decrease", "decline", "rise", "fall"]):
            analysis.append("• Growth trends: Document contains growth/decline indicators")
        
        # Look for cash flow data
        if any(word in processed_data.lower() for word in ["cash flow", "operating cash", "free cash"]):
            analysis.append("• Cash flow: Document contains cash flow information")
        
        # Look for debt/liability data
        if any(word in processed_data.lower() for word in ["debt", "liability", "borrowing", "loan"]):
            analysis.append("• Debt analysis: Document contains debt/liability information")
        
        # Look for market indicators
        if any(word in processed_data.lower() for word in ["market", "share", "stock", "equity", "valuation"]):
            analysis.append("• Market analysis: Document contains market/share data")
        
        if not analysis:
            analysis.append("• General analysis: Document contains financial data requiring detailed review")
        
        return "\n".join(analysis) if analysis else "No specific investment indicators found"


## Creating Risk Assessment Tool
class RiskTool:
    @tool("Create risk assessment")
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        """Creates a risk assessment from financial document text.

        Args:
            financial_document_data (str): Extracted financial document text.

        Returns:
            str: Extracted insights or error message if processing fails.
        """
        if not financial_document_data:
            return "No financial data provided."

        # Clean up double spaces
        processed_data = " ".join(financial_document_data.split())
        
        # Risk assessment analysis
        risks = []
        
        # Look for financial stress indicators
        if any(word in processed_data.lower() for word in ["loss", "deficit", "decline", "decrease", "negative"]):
            risks.append("• Financial stress: Document indicates potential financial losses or declines")
        
        # Look for debt-related risks
        if any(word in processed_data.lower() for word in ["debt", "liability", "borrowing", "credit", "leverage"]):
            risks.append("• Debt risk: Document contains debt/liability information requiring assessment")
        
        # Look for market volatility indicators
        if any(word in processed_data.lower() for word in ["volatile", "uncertain", "risk", "challenge", "difficult"]):
            risks.append("• Market volatility: Document indicates market uncertainty or challenges")
        
        # Look for regulatory/compliance risks
        if any(word in processed_data.lower() for word in ["regulation", "compliance", "legal", "audit", "investigation"]):
            risks.append("• Regulatory risk: Document mentions regulatory or compliance matters")
        
        # Look for operational risks
        if any(word in processed_data.lower() for word in ["operational", "production", "supply", "manufacturing", "capacity"]):
            risks.append("• Operational risk: Document contains operational information requiring risk assessment")
        
        # Look for competitive risks
        if any(word in processed_data.lower() for word in ["competition", "competitive", "market share", "pricing"]):
            risks.append("• Competitive risk: Document mentions competitive factors")
        
        # Look for technology risks
        if any(word in processed_data.lower() for word in ["technology", "digital", "cyber", "innovation", "disruption"]):
            risks.append("• Technology risk: Document contains technology-related information")
        
        if not risks:
            risks.append("• General risk: Document requires comprehensive risk assessment")
        
        return "\n".join(risks) if risks else "No specific risk indicators identified"
