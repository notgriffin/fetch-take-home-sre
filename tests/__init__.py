import asyncio
import sys

if sys.platform == 'win32':
    # Required for windows test runners
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())