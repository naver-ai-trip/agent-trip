"""Test that auth token context is properly set."""
import asyncio
from src.utils.context import set_auth_token, get_auth_token
from src.tools.place_tools import search_places_by_text


async def test_context():
    """Test auth token context."""
    
    # Set token
    token = "7|SXQRsdEG9gmd0PdtqHfwHegZYSYXqfEbRmPrMwFE63756727"
    set_auth_token(token)
    
    # Verify it's set
    retrieved = get_auth_token()
    print(f"✅ Token set in context: {retrieved[:20]}...")
    
    # Test tool
    print("\nTesting search_places_by_text with context token...")
    result = await search_places_by_text.ainvoke({"query": "Gyeongbokgung"})
    
    if result:
        print(f"✅ SUCCESS! Found {len(result)} places")
        print(f"First place: {result[0].get('name')}")
    else:
        print("❌ No results found")


if __name__ == "__main__":
    asyncio.run(test_context())
