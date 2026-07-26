import asyncio
import os
from app.services.llm_service import llm_service

async def test():
    try:
        print("Testing STREAMING model...")
        async for token in llm_service.stream_answer("Hello"):
            print(token, end="", flush=True)
        print("\nStream finished.")
    except Exception as e:
        import traceback
        print(f"\nError: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
