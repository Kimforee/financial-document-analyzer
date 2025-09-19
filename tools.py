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
    async def analyze_investment_tool(financial_document_data: str) -> str:
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

        # TODO: Implement actual investment analysis logic here
        return "Investment analysis functionality to be implemented"


## Creating Risk Assessment Tool
class RiskTool:
    @tool("Create risk assessment")
    async def create_risk_assessment_tool(financial_document_data: str) -> str:
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

        # TODO: Implement actual risk assessment logic here
        return "Risk assessment functionality to be implemented"
