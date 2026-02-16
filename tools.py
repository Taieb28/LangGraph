# tools.py
from langchain.tools import tool

# 1. defenition of tool
@tool
def multiply(a: int, b: int) -> int:
    """يضرب رقمين ويعيد الناتج."""
    return a * b
