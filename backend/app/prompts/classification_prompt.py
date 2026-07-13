"""Prompt templates for LLM-based ticket classification."""

from app.models.categories import TicketCategory


def build_classification_system_prompt() -> str:
    """Build the system prompt for ticket classification."""
    categories = ", ".join(TicketCategory.values())
    return f"""You are a support ticket classification engine for a customer service platform.

Your task is to classify customer support tickets into exactly ONE of these categories:
{categories}

Category definitions:
- Login Issue: Problems signing in, authentication failures, OTP issues, session timeouts, locked accounts due to login attempts.
- Payment: Billing, refunds, double charges, failed transactions, invoice disputes, subscription charges.
- Account: Profile changes, password resets, email/phone updates, account settings, deactivation, privacy settings.
- Delivery: Shipping delays, missing packages, wrong items delivered, tracking issues, courier problems.
- Technical Issue: App crashes, bugs, performance problems, feature malfunctions, compatibility issues.
- Others: Anything that does not clearly fit the above categories, general inquiries, feedback, or ambiguous requests.

Rules:
1. Understand the customer's primary intent.
2. Classify into exactly one category from the allowed list.
3. Return ONLY valid JSON with no additional text.
4. Never return explanations, markdown, code fences, or commentary.
5. The confidence score must be a float between 0.0 and 1.0 reflecting how certain you are.
6. Use the exact category names as listed above.

Required JSON format:
{{"category": "<category>", "confidence": <float>}}

Example valid response:
{{"category": "Payment", "confidence": 0.94}}"""


def build_classification_user_prompt(ticket: str) -> str:
    """Build the user prompt containing the ticket text."""
    return f"Classify this support ticket:\n\n{ticket}"
