## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, FinancialDocumentTool, InvestmentTool, RiskTool

## Creating a task to help solve user's query
analyze_financial_document = Task(
    description="Analyze the financial document and provide insights based on the user's query: {query}.\n\
    Read the financial document data using the read_data_tool.\n\
    Provide a comprehensive analysis with specific findings from the document.\n\
    Focus on key financial metrics, trends, and actionable insights.",

    expected_output="""Provide a structured analysis with:
    - Key financial highlights from the document
    - Specific metrics and numbers found
    - Analysis of trends and patterns
    - Clear recommendations based on the data
    - Professional summary in 2-3 paragraphs""",

    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    description="Provide investment analysis based on the financial document data.\n\
    Use the analyze_investment_tool to process the financial data.\n\
    Focus on the user's query: {query}.\n\
    Provide specific investment recommendations based on the document findings.",

    expected_output="""Provide investment recommendations with:
    - Specific investment opportunities identified
    - Risk-return analysis
    - Portfolio allocation suggestions
    - Market outlook based on the data
    - Clear next steps for the investor""",

    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    description="Conduct a risk assessment based on the financial document data.\n\
    Use the create_risk_assessment_tool to analyze the financial data.\n\
    Focus on the user's query: {query}.\n\
    Identify specific risks and provide mitigation strategies.",

    expected_output="""Provide a risk assessment with:
    - Key risk factors identified from the document
    - Risk level assessment (low/medium/high)
    - Specific mitigation strategies
    - Risk monitoring recommendations
    - Overall risk profile summary""",

    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

    
verification = Task(
    description="Verify the document type and validate the financial data quality.\n\
    Use the read_data_tool to examine the document content.\n\
    Confirm if this is a valid financial document and assess data quality.\n\
    Focus on the user's query: {query}.",

    expected_output="""Provide document verification with:
    - Document type confirmation
    - Data quality assessment
    - Key financial sections identified
    - Data completeness check
    - Verification status and recommendations""",

    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False
)