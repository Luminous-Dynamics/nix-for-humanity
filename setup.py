#!/usr/bin/env python3
"""
Backward compatibility setup.py

This file exists for compatibility with older tools that don't support
pyproject.toml directly. All configuration is in pyproject.toml.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()
