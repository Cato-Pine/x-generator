"""Virtue-specific prompt templates."""

from src.llm.prompts.wisdom import (
    WISDOM_SYSTEM_PROMPT,
    WISDOM_SHORT_TEMPLATE,
    WISDOM_THREAD_TEMPLATE,
)
from src.llm.prompts.courage import (
    COURAGE_SYSTEM_PROMPT,
    COURAGE_SHORT_TEMPLATE,
    COURAGE_THREAD_TEMPLATE,
)
from src.llm.prompts.justice import (
    JUSTICE_SYSTEM_PROMPT,
    JUSTICE_SHORT_TEMPLATE,
    JUSTICE_THREAD_TEMPLATE,
)
from src.llm.prompts.temperance import (
    TEMPERANCE_SYSTEM_PROMPT,
    TEMPERANCE_SHORT_TEMPLATE,
    TEMPERANCE_THREAD_TEMPLATE,
)
from src.llm.prompts.general import (
    GENERAL_SYSTEM_PROMPT,
    GENERAL_SHORT_TEMPLATE,
    GENERAL_THREAD_TEMPLATE,
    AMOR_FATI_TEMPLATE,
    MEMENTO_MORI_TEMPLATE,
    PREMEDITATIO_TEMPLATE,
    DICHOTOMY_TEMPLATE,
)

VIRTUE_SYSTEM_PROMPTS = {
    "wisdom": WISDOM_SYSTEM_PROMPT,
    "courage": COURAGE_SYSTEM_PROMPT,
    "justice": JUSTICE_SYSTEM_PROMPT,
    "temperance": TEMPERANCE_SYSTEM_PROMPT,
    "general": GENERAL_SYSTEM_PROMPT,
}

VIRTUE_SHORT_TEMPLATES = {
    "wisdom": WISDOM_SHORT_TEMPLATE,
    "courage": COURAGE_SHORT_TEMPLATE,
    "justice": JUSTICE_SHORT_TEMPLATE,
    "temperance": TEMPERANCE_SHORT_TEMPLATE,
    "general": GENERAL_SHORT_TEMPLATE,
}

VIRTUE_THREAD_TEMPLATES = {
    "wisdom": WISDOM_THREAD_TEMPLATE,
    "courage": COURAGE_THREAD_TEMPLATE,
    "justice": JUSTICE_THREAD_TEMPLATE,
    "temperance": TEMPERANCE_THREAD_TEMPLATE,
    "general": GENERAL_THREAD_TEMPLATE,
}


def get_virtue_system_prompt(virtue: str) -> str:
    """Get the system prompt for a specific virtue."""
    return VIRTUE_SYSTEM_PROMPTS.get(virtue, GENERAL_SYSTEM_PROMPT)


def get_virtue_short_template(virtue: str) -> str:
    """Get the short tweet template for a specific virtue."""
    return VIRTUE_SHORT_TEMPLATES.get(virtue, GENERAL_SHORT_TEMPLATE)


def get_virtue_thread_template(virtue: str) -> str:
    """Get the thread template for a specific virtue."""
    return VIRTUE_THREAD_TEMPLATES.get(virtue, GENERAL_THREAD_TEMPLATE)
