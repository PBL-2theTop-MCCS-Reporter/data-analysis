#!/usr/bin/env python3
"""
Example script demonstrating how to use the retail_llm_insights module
to generate AI-powered insights from retail analysis results.

Usage:
    python example_llm_insights.py --api_key YOUR_OPENAI_API_KEY [--question "Your specific question"]

Requirements:
    - OpenAI API key
    - Completed retail analysis (summary_report.txt must exist)
"""

import argparse
import os
from retail_llm_insights import (
    configure_openai_client,
    read_summary_report,
    generate_retail_insights,
    save_insights_to_file
)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate AI insights from retail analysis')
    parser.add_argument('--api_key', required=True, help='OpenAI API key')
    parser.add_argument('--question', help='Specific question to ask about the retail data')
    parser.add_argument('--output', default='retail_analysis_results/example_insights.md',
                        help='Output file path for insights')
    
    args = parser.parse_args()
    
    # Check if summary report exists
    if not os.path.exists('retail_analysis_results/summary_report.txt'):
        print("Error: Summary report not found. Please run the static analysis first.")
        return
    
    print("Generating AI insights from retail analysis results...")
    
    # Configure OpenAI client
    client = configure_openai_client(args.api_key)
    
    # Read summary report
    summary_content = read_summary_report()
    
    # Generate insights
    insights = generate_retail_insights(
        summary_content=summary_content,
        question=args.question,
        openai_client=client
    )
    
    # Save insights to file
    save_insights_to_file(insights, args.output)
    
    # Print insights to console
    print("\n" + "="*50)
    print("RETAIL ANALYSIS LLM INSIGHTS")
    print("="*50)
    print(insights)
    
    print(f"\nInsights saved to {args.output}")

if __name__ == "__main__":
    main()
