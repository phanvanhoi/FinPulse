FORMATTER_PROMPT = """Convert the following analysis into a clear, concise insight for a business owner.

## Analysis
{analysis}

## Rules
- Title: max 80 characters, start with an action verb or key finding
- Body: markdown format, 2-4 short paragraphs
- Use bullet points for lists
- Include specific numbers
- End with a clear "What to do" section if there's an actionable recommendation
- Severity: "info" for general updates, "warning" for concerning trends, "critical" for immediate action needed
- Do NOT use technical jargon - write as if explaining to a smart friend who doesn't know finance/marketing terminology
"""
