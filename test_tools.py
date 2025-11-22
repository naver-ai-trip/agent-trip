"""Test suite for AI Travel Agent tools."""

import asyncio
import json
from typing import Any, Dict


# Test configuration
AUTH_TOKEN = "7|SXQRsdEG9gmd0PdtqHfwHegZYSYXqfEbRmPrMwFE63756727"


class ToolTester:
    """Test class for individual agent tools."""
    
    def __init__(self, auth_token: str = AUTH_TOKEN):
        self.auth_token = auth_token
    
    def print_result(self, title: str, result: Any, success: bool = True):
        """Print formatted test result."""
        status = "✅" if success else "❌"
        print(f"\n{status} {title}")
        print("-" * 60)
        
        if isinstance(result, (dict, list)):
            result_str = json.dumps(result, indent=2, ensure_ascii=False)
            # Truncate if too long
            if len(result_str) > 1000:
                result_str = result_str[:1000] + "\n... (truncated)"
            print(result_str)
        else:
            print(str(result)[:500])
        print("-" * 60)
    
    async def test_backend_api_client(self):
        """Test Backend API Client methods."""
        print("\n" + "="*60)
        print("TEST SUITE 1: Backend API Client")
        print("="*60)
        
        from src.utils.api_client import BackendAPIClient
        
        client = BackendAPIClient()
        
        # Use session 3 which we have access to
        test_session_id = 3
        
        try:
            # Test 1: Get chat session
            print(f"\n[1.1] Testing get_chat_session...")
            try:
                session = await client.get_chat_session(test_session_id, self.auth_token)
                self.print_result(f"get_chat_session(session_id={test_session_id})", session)
            except Exception as e:
                self.print_result(f"get_chat_session ERROR: {e}", str(e), False)
            
            # Test 2: Get chat messages
            print("\n[1.2] Testing get_chat_messages...")
            try:
                messages = await client.get_chat_messages(test_session_id, self.auth_token)
                self.print_result(f"get_chat_messages(session_id={test_session_id})", messages)
            except Exception as e:
                self.print_result(f"get_chat_messages ERROR: {e}", str(e), False)
            
            # Test 3: Search places
            print("\n[1.3] Testing search_places...")
            try:
                places = await client.search_places("Seoul Tower", self.auth_token)
                self.print_result("search_places('Seoul Tower')", places)
            except Exception as e:
                self.print_result(f"search_places ERROR: {e}", str(e), False)
            
            # Test 4: Search nearby places
            print("\n[1.4] Testing search_nearby_places...")
            try:
                # Gangnam Station coordinates
                nearby = await client.search_nearby_places(
                    latitude=37.4979,
                    longitude=127.0276,
                    auth_token=self.auth_token,
                    radius=1000
                )
                self.print_result("search_nearby_places(Gangnam)", nearby)
            except Exception as e:
                self.print_result(f"search_nearby_places ERROR: {e}", str(e), False)
            
            # Test 5: Send message
            print("\n[1.5] Testing send_message...")
            try:
                message = await client.send_message(
                    session_id=test_session_id,
                    message="Test message from tool tester",
                    auth_token=self.auth_token,
                    from_role="assistant",
                    message_type="text",
                    metadata={"test": True},
                    references=[{"type": "place", "id": 123}]
                )
                self.print_result("send_message()", message)
            except Exception as e:
                self.print_result(f"send_message ERROR: {e}", str(e), False)
                
        finally:
            await client.close()
    
    async def test_place_tools(self):
        """Test Place search tools."""
        print("\n" + "="*60)
        print("TEST SUITE 2: Place Search Tools")
        print("="*60)
        
        from src.tools.place_tools import (
            search_places_by_text,
            search_nearby_places,
            scrape_korea_tourist_spots,
            get_place_details_by_korean_name
        )
        from src.utils.context import set_auth_token
        
        # Set auth token in context for tools to use
        set_auth_token(self.auth_token)
        
        # Test 1: Search places by text
        print("\n[2.1] Testing search_places_by_text...")
        try:
            result = await search_places_by_text.ainvoke({
                "query": "Gyeongbokgung Palace"
            })
            self.print_result("search_places_by_text('Gyeongbokgung Palace')", result)
        except Exception as e:
            self.print_result(f"search_places_by_text ERROR: {e}", str(e), False)
        
        # Test 2: Search places by text (Korean)
        print("\n[2.2] Testing search_places_by_text (Korean)...")
        try:
            result = await search_places_by_text.ainvoke({
                "query": "명동"  # Myeongdong
            })
            self.print_result("search_places_by_text('명동')", result)
        except Exception as e:
            self.print_result(f"search_places_by_text (Korean) ERROR: {e}", str(e), False)
        
        # Test 3: Search nearby places
        print("\n[2.3] Testing search_nearby_places...")
        try:
            result = await search_nearby_places.ainvoke({
                "latitude": 37.5665,
                "longitude": 126.9780,
                "radius": 2000,
                "place_type": "restaurant"
            })
            self.print_result("search_nearby_places(Seoul City Hall)", result)
        except Exception as e:
            self.print_result(f"search_nearby_places ERROR: {e}", str(e), False)
        
        # Test 4: Scrape Korea tourist spots
        print("\n[2.4] Testing scrape_korea_tourist_spots...")
        try:
            result = await scrape_korea_tourist_spots.ainvoke({
                "region": "Seoul"
            })
            self.print_result("scrape_korea_tourist_spots('Seoul')", result)
        except Exception as e:
            self.print_result(f"scrape_korea_tourist_spots ERROR: {e}", str(e), False)
        
        # Test 5: Get place details by Korean name
        print("\n[2.5] Testing get_place_details_by_korean_name...")
        try:
            result = await get_place_details_by_korean_name.ainvoke({
                "korean_name": "경복궁"  # Gyeongbokgung
            })
            self.print_result("get_place_details_by_korean_name('경복궁')", result)
        except Exception as e:
            self.print_result(f"get_place_details_by_korean_name ERROR: {e}", str(e), False)
    
    async def test_translator(self):
        """Test Language detector and translator."""
        print("\n" + "="*60)
        print("TEST SUITE 3: Language Detector & Translator")
        print("="*60)
        
        from src.utils.translator import LanguageDetector
        
        detector = LanguageDetector()
        
        # Test 1: Detect English
        print("\n[3.1] Testing detect_language (English)...")
        text_en = "Find hotels in Seoul"
        lang = detector.detect_language(text_en)
        self.print_result(f"detect_language('{text_en}')", {"language": lang})
        
        # Test 2: Detect Korean
        print("\n[3.2] Testing detect_language (Korean)...")
        text_ko = "서울에서 호텔 찾아줘"
        lang = detector.detect_language(text_ko)
        self.print_result(f"detect_language('{text_ko}')", {"language": lang})
        
        # Test 3: Detect Japanese
        print("\n[3.3] Testing detect_language (Japanese)...")
        text_ja = "東京のホテルを探して"
        lang = detector.detect_language(text_ja)
        self.print_result(f"detect_language('{text_ja}')", {"language": lang})
        
        # Test 4: Translate to Korean
        print("\n[3.4] Testing translate_to_korean...")
        try:
            translated = await detector.translate_to_korean("Seoul Tower")
            self.print_result("translate_to_korean('Seoul Tower')", {
                "original": "Seoul Tower",
                "translated": translated
            })
        except Exception as e:
            self.print_result(f"translate_to_korean ERROR: {e}", str(e), False)
        
        # Test 5: Translate to language
        print("\n[3.5] Testing translate_to_language...")
        try:
            translated = await detector.translate_to_language(
                "경복궁은 아름다운 궁전입니다",
                "en"
            )
            self.print_result("translate_to_language(Korean->English)", {
                "original": "경복궁은 아름다운 궁전입니다",
                "translated": translated
            })
        except Exception as e:
            self.print_result(f"translate_to_language ERROR: {e}", str(e), False)
        
        # Test 6: Extract Korean name
        print("\n[3.6] Testing extract_korean_name...")
        result = detector.extract_korean_name("Visit 경복궁 (Gyeongbokgung Palace) today")
        self.print_result("extract_korean_name", {
            "input": "Visit 경복궁 (Gyeongbokgung Palace) today",
            "extracted": result
        })
    
    async def test_trip_planner(self):
        """Test Trip planner utilities."""
        print("\n" + "="*60)
        print("TEST SUITE 4: Trip Planner Utilities")
        print("="*60)
        
        from src.utils.trip_planner import TripPlanner
        from datetime import datetime, timedelta
        
        planner = TripPlanner()
        
        # Test 1: Calculate days
        print("\n[4.1] Testing calculate_days...")
        start = datetime(2025, 12, 20)
        end = datetime(2025, 12, 23)
        days = planner.calculate_days(start, end)
        self.print_result("calculate_days(3 nights)", {
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "days": days
        })
        
        # Test 2: Generate time slots
        print("\n[4.2] Testing generate_time_slots...")
        slots = planner.generate_time_slots()
        self.print_result("generate_time_slots()", {"time_slots": slots})
        
        # Test 3: Create itinerary
        print("\n[4.3] Testing create_itinerary...")
        places = [
            {"name": "Gyeongbokgung Palace", "type": "tourist_attraction"},
            {"name": "Bukchon Hanok Village", "type": "tourist_attraction"},
            {"name": "Insadong", "type": "shopping"},
            {"name": "Myeongdong", "type": "shopping"},
            {"name": "N Seoul Tower", "type": "tourist_attraction"},
            {"name": "Gangnam", "type": "entertainment"}
        ]
        itinerary = planner.create_itinerary(places, days=3)
        self.print_result("create_itinerary(3 days, 6 places)", itinerary)
    
    async def test_response_formatter(self):
        """Test Response formatter."""
        print("\n" + "="*60)
        print("TEST SUITE 5: Response Formatter")
        print("="*60)
        
        from src.graph.response_formatter import ResponseFormatter
        
        formatter = ResponseFormatter()
        
        # Test 1: Format places response
        print("\n[5.1] Testing format_places_response...")
        places = [
            {
                "name": "Gyeongbokgung Palace",
                "description": "Beautiful royal palace",
                "rating": 4.8,
                "address": "Seoul, South Korea"
            },
            {
                "name": "N Seoul Tower",
                "description": "Iconic observation tower",
                "rating": 4.7,
                "address": "Namsan, Seoul"
            }
        ]
        response = formatter.format_places_response(places, "Seoul attractions")
        self.print_result("format_places_response(2 places)", response)
        
        # Test 2: Format trip plan response
        print("\n[5.2] Testing format_trip_plan_response...")
        itinerary = {
            "Day 1": [
                {"time": "09:00", "activity": "Gyeongbokgung Palace"},
                {"time": "14:00", "activity": "Bukchon Hanok Village"}
            ],
            "Day 2": [
                {"time": "10:00", "activity": "N Seoul Tower"},
                {"time": "15:00", "activity": "Myeongdong Shopping"}
            ]
        }
        response = formatter.format_trip_plan_response(itinerary, 2, "Seoul")
        self.print_result("format_trip_plan_response(2 days)", response)
        
        # Test 3: Format image translation trigger
        print("\n[5.3] Testing format_image_translation_trigger...")
        response = formatter.format_image_translation_trigger()
        self.print_result("format_image_translation_trigger()", response)
        
        # Test 4: Format error response
        print("\n[5.4] Testing format_error_response...")
        response = formatter.format_error_response("Something went wrong")
        self.print_result("format_error_response()", response)
    
    async def test_agent_graph(self):
        """Test Agent graph execution."""
        print("\n" + "="*60)
        print("TEST SUITE 6: Agent Graph Execution")
        print("="*60)
        
        from src.graph.agent import agent_graph
        from src.graph.state import AgentState
        
        # Test 1: Simple query
        print("\n[6.1] Testing agent graph with simple query...")
        try:
            initial_state: AgentState = {
                "messages": [],
                "auth_token": self.auth_token,
                "session_id": 1,
                "trip_id": None,
                "user_message": "Find tourist attractions in Seoul",
                "places_found": [],
                "actions_taken": [],
                "next_suggestions": [],
                "iteration_count": 0,
                "user_language": "en",
                "trigger_image_translation": False
            }
            
            result = await agent_graph.ainvoke(initial_state)
            
            self.print_result("agent_graph execution", {
                "final_response": result.get("final_response", {}),
                "actions_taken": result.get("actions_taken", []),
                "places_found_count": len(result.get("places_found", []))
            })
        except Exception as e:
            self.print_result(f"agent_graph ERROR: {e}", str(e), False)


async def run_all_tests():
    """Run all tool tests."""
    print("\n" + "🧪"*30)
    print("AI TRAVEL AGENT - TOOL TEST SUITE")
    print("🧪"*30)
    print(f"\nAuth Token: {AUTH_TOKEN[:20]}...")
    
    tester = ToolTester()
    
    try:
        # Test 1: Backend API Client
        await tester.test_backend_api_client()
        
        # Test 2: Place Tools
        await tester.test_place_tools()
        
        # Test 3: Translator
        await tester.test_translator()
        
        # Test 4: Trip Planner
        await tester.test_trip_planner()
        
        # Test 5: Response Formatter
        await tester.test_response_formatter()
        
        # Test 6: Agent Graph
        await tester.test_agent_graph()
        
        print("\n" + "="*60)
        print("✅ ALL TOOL TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TOOL TEST SUITE FAILED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()


async def run_single_suite(suite_name: str):
    """Run a single test suite."""
    tester = ToolTester()
    
    suites = {
        "api": tester.test_backend_api_client,
        "places": tester.test_place_tools,
        "translator": tester.test_translator,
        "planner": tester.test_trip_planner,
        "formatter": tester.test_response_formatter,
        "graph": tester.test_agent_graph,
    }
    
    if suite_name in suites:
        await suites[suite_name]()
    else:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(suites.keys())}")


async def quick_test():
    """Quick test - essential tools only."""
    print("\n" + "⚡"*30)
    print("QUICK TOOL TEST")
    print("⚡"*30)
    
    tester = ToolTester()
    
    print("\n[Quick] Testing Backend API...")
    from src.utils.api_client import BackendAPIClient
    client = BackendAPIClient()
    try:
        session = await client.get_chat_session(1, tester.auth_token)
        tester.print_result("Backend API Client", {"status": "working", "session": session})
    except Exception as e:
        tester.print_result(f"Backend API Client", str(e), False)
    finally:
        await client.close()
    
    print("\n[Quick] Testing Place Search...")
    from src.tools.place_tools import search_places_by_text
    try:
        result = await search_places_by_text.ainvoke({"query": "Seoul"})
        tester.print_result("Place Search Tool", {"status": "working", "results": len(result)})
    except Exception as e:
        tester.print_result(f"Place Search Tool", str(e), False)
    
    print("\n[Quick] Testing Language Detector...")
    from src.utils.translator import LanguageDetector
    try:
        detector = LanguageDetector()
        lang = detector.detect_language("Find hotels in Seoul")
        tester.print_result("Language Detector", {"status": "working", "detected": lang})
    except Exception as e:
        tester.print_result(f"Language Detector", str(e), False)
    
    print("\n✅ Quick tool test completed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            # Quick test
            asyncio.run(quick_test())
        else:
            # Run specific suite
            asyncio.run(run_single_suite(sys.argv[1]))
    else:
        # Run all tests
        asyncio.run(run_all_tests())
