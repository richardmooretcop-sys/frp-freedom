#!/usr/bin/env python3
"""
Bypass module for FRP Freedom
Contains all FRP bypass methods and management functionality
"""

__all__ = [
    'BypassManager',
    'BypassMethod',
    'BypassResult',
    'ADBExploitManager',
    'InterfaceExploitManager',
    'SystemExploitManager',
    'HardwareExploitManager'
]


def __getattr__(name):
    """Lazily import bypass submodules to avoid circular imports and reduce startup cost."""
    if name == 'BypassManager':
        from .bypass_manager import BypassManager
        return BypassManager
    if name in {'BypassMethod', 'BypassResult'}:
        from .types import BypassMethod, BypassResult
        return {
            'BypassMethod': BypassMethod,
            'BypassResult': BypassResult,
        }[name]
    if name == 'ADBExploitManager':
        from .adb_exploits import ADBExploitManager
        return ADBExploitManager
    if name == 'InterfaceExploitManager':
        from .interface_exploits import InterfaceExploitManager
        return InterfaceExploitManager
    if name == 'SystemExploitManager':
        from .system_exploits import SystemExploitManager
        return SystemExploitManager
    if name == 'HardwareExploitManager':
        from .hardware_exploits import HardwareExploitManager
        return HardwareExploitManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")