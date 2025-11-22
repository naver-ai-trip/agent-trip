"""Quick test for send_message API fix."""
import asyncio
from src.utils.api_client import BackendAPIClient


async def test_send_message():
    """Test send_message with corrected payload format."""
    client = BackendAPIClient()
    
    # Your token - update if needed
    auth_token = "7|SXQRsdEG9gmd0PdtqHfwHegZYSYXqfEbRmPrMwFE63756727"
    
    try:
        print("Testing send_message with corrected format...")
        print("=" * 60)
        
        result = await client.send_message(
            session_id=3,
            message="Test from fixed API client - correct format",
            auth_token=auth_token,
            from_role="assistant",
            message_type="text",
            metadata={
                "model": "gpt-4",
                "confidence": 0.95,
                "test": True
            },
            references=[
                {"type": "place", "id": 123}
            ]
        )
        
        print("✅ SUCCESS!")
        print("Response:", result)
        
    except Exception as e:
        print("❌ ERROR!")
        print(f"Error: {e}")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_send_message())
