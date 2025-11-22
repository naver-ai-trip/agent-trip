"""Request context management for passing auth tokens to tools."""

from contextvars import ContextVar
from typing import Optional

# Context variable to store auth token for current request
auth_token_ctx: ContextVar[Optional[str]] = ContextVar('auth_token', default=None)


def set_auth_token(token: str) -> None:
    """Set the auth token for the current context.
    
    Args:
        token: Authentication token
    """
    auth_token_ctx.set(token)


def get_auth_token() -> Optional[str]:
    """Get the auth token from the current context.
    
    Returns:
        Authentication token or None if not set
    """
    return auth_token_ctx.get()
