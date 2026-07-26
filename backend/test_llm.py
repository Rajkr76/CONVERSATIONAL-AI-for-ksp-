import asyncio
import os
from app.services.llm_service import llm_service

async def test():
    try:
        print("Testing SQL model...")
        sql = await llm_service.generate_sql("Hello")
        print(f"Result: {sql}")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
