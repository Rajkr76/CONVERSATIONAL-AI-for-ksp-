import asyncio
import json
import httpx
import traceback

async def test_full_flow():
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        # 1. Login to get token
        print("Logging in...")
        resp = await client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        
        token = resp.json()["access_token"]
        print(f"Got token: {token[:20]}...")
        
        # 2. Call stream endpoint
        print("Calling chat stream...")
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "question": "How many FIRs were registered in 2024?",
            "language": "en"
        }
        
        try:
            async with client.stream("POST", "/api/chat/stream", json=payload, headers=headers, timeout=120.0) as stream_resp:
                print(f"Stream status: {stream_resp.status_code}")
                if stream_resp.status_code != 200:
                    print(f"Error body: {await stream_resp.aread()}")
                    return
                async for line in stream_resp.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    print(f"LINE: {line}")
        except Exception as e:
            print(f"Error during stream: {type(e).__name__}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_flow())
