#!/usr/bin/env python3
"""
AI Module for FRP Freedom
Provides AI-powered device analysis and intelligent bypass recommendations
"""

__all__ = ['AIEngine', 'DeviceProfile', 'AINotificationSystem']


def __getattr__(name):
    """Defer AI imports so package initialization stays lightweight and cycle-free."""
    if name == 'AIEngine':
        from .ai_engine import AIEngine
        return AIEngine
    if name == 'DeviceProfile':
        from .ai_engine import DeviceProfile
        return DeviceProfile
    if name == 'AINotificationSystem':
        from .notification_system import AINotificationSystem
        return AINotificationSystem
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")