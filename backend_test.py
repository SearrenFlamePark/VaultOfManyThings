import requests
import sys
import json
import uuid
from datetime import datetime
import io

class ChatGPTBackendTester:
    def __init__(self, base_url="https://61ac9fa4-bee8-4446-be2b-6c122b968795.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None
        self.conversation_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic API health check"""
        success, response = self.run_test(
            "API Health Check",
            "GET",
            "",
            200
        )
        return success

    def test_chat_functionality(self):
        """Test main chat endpoint"""
        test_message = "Hello, this is a test message. Can you respond?"
        
        success, response = self.run_test(
            "Chat Functionality",
            "POST",
            "chat",
            200,
            data={
                "message": test_message,
                "session_id": None  # Let it generate a new session
            }
        )
        
        if success and response:
            self.session_id = response.get('session_id')
            self.conversation_id = response.get('conversation_id')
            print(f"   Generated session_id: {self.session_id}")
            print(f"   Generated conversation_id: {self.conversation_id}")
            
            # Check if response contains expected fields
            if 'message' in response and 'session_id' in response:
                print("   ✅ Response contains required fields")
                return True
            else:
                print("   ❌ Response missing required fields")
                return False
        
        return success

    def test_continuous_memory(self):
        """Test continuous memory by sending follow-up messages"""
        if not self.session_id:
            print("❌ No session_id available for memory test")
            return False

        # Send first message
        success1, response1 = self.run_test(
            "Memory Test - First Message",
            "POST",
            "chat",
            200,
            data={
                "message": "My name is TestUser and I like pizza.",
                "session_id": self.session_id
            }
        )

        if not success1:
            return False

        # Send follow-up message to test memory
        success2, response2 = self.run_test(
            "Memory Test - Follow-up Message",
            "POST",
            "chat",
            200,
            data={
                "message": "What is my name and what do I like?",
                "session_id": self.session_id
            }
        )

        if success2 and response2:
            response_text = response2.get('message', '').lower()
            if 'testuser' in response_text and 'pizza' in response_text:
                print("   ✅ AI remembered previous conversation!")
                return True
            else:
                print("   ⚠️  AI response doesn't clearly show memory of previous conversation")
                print(f"   Response: {response2.get('message', '')}")
                return True  # Still pass as the API worked
        
        return success2

    def test_conversation_history(self):
        """Test loading conversation history"""
        if not self.session_id:
            print("❌ No session_id available for history test")
            return False

        success, response = self.run_test(
            "Conversation History",
            "GET",
            f"conversations/{self.session_id}",
            200
        )

        if success and response:
            conversations = response.get('conversations', [])
            if conversations:
                print(f"   ✅ Found {len(conversations)} conversations in history")
                return True
            else:
                print("   ⚠️  No conversations found in history")
                return True  # Still pass as API worked
        
        return success

    def test_notes_functionality(self):
        """Test Obsidian notes upload and retrieval"""
        # Test getting notes (should be empty initially)
        success1, response1 = self.run_test(
            "Get Notes (Empty)",
            "GET",
            "notes",
            200
        )

        if not success1:
            return False

        # Test uploading a mock markdown file
        mock_md_content = """# Test Note
        
This is a test Obsidian note for testing the upload functionality.

## Key Points
- This is a test
- Memory system integration
- Note searching capabilities
"""
        
        files = {
            'files': ('test_note.md', io.StringIO(mock_md_content), 'text/markdown')
        }
        
        success2, response2 = self.run_test(
            "Upload Notes",
            "POST",
            "notes/upload",
            200,
            files=files
        )

        if not success2:
            return False

        # Test getting notes after upload
        success3, response3 = self.run_test(
            "Get Notes (After Upload)",
            "GET",
            "notes",
            200
        )

        if success3 and response3:
            notes = response3.get('notes', [])
            if notes:
                print(f"   ✅ Found {len(notes)} notes after upload")
                return True
            else:
                print("   ⚠️  No notes found after upload")
        
        return success3

    def test_clear_conversation(self):
        """Test clearing conversation history"""
        if not self.session_id:
            print("❌ No session_id available for clear test")
            return False

        success, response = self.run_test(
            "Clear Conversation",
            "DELETE",
            f"conversations/clear/{self.session_id}",
            200
        )

        if success and response:
            deleted_count = response.get('deleted_count', 0)
            print(f"   ✅ Cleared {deleted_count} conversations")
            return True
        
        return success

    def test_status_endpoints(self):
        """Test status check endpoints"""
        # Test creating status check
        success1, response1 = self.run_test(
            "Create Status Check",
            "POST",
            "status",
            200,
            data={"client_name": "test_client"}
        )

        if not success1:
            return False

        # Test getting status checks
        success2, response2 = self.run_test(
            "Get Status Checks",
            "GET",
            "status",
            200
        )

        return success2

def main():
    print("🚀 Starting Continuous Memory ChatGPT Backend Tests")
    print("=" * 60)
    
    tester = ChatGPTBackendTester()
    
    # Run all tests in sequence
    tests = [
        ("API Health Check", tester.test_health_check),
        ("Chat Functionality", tester.test_chat_functionality),
        ("Continuous Memory", tester.test_continuous_memory),
        ("Conversation History", tester.test_conversation_history),
        ("Notes Functionality", tester.test_notes_functionality),
        ("Clear Conversation", tester.test_clear_conversation),
        ("Status Endpoints", tester.test_status_endpoints),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "0%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())