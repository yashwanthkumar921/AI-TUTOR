import json
import os
import re
import anthropic
from typing import Optional, Dict, Any, List
import sys

# SECURITY: Use environment variables for API keys
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("Please set ANTHROPIC_API_KEY environment variable")

# Initialize Claude client
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Define directories and master files
BASE_DIR = os.path.dirname(__file__)
LESSONS_DIR = os.path.join(BASE_DIR, "lessons")
QUIZZES_DIR = os.path.join(BASE_DIR, "quizzes")
CHAT_HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")

# Ensure directories exist
os.makedirs(LESSONS_DIR, exist_ok=True)
os.makedirs(QUIZZES_DIR, exist_ok=True)

# Available topics for learning
AVAILABLE_TOPICS = [
    "Introduction to Python",
    "Variables and Data Types", 
    "Conditionals",
    "Loops",
    "Functions",
    "Lists and Tuples",
    "Dictionaries",
    "File Handling",
    "Error Handling",
    "Object-Oriented Programming"
]

class PythonLearningChatbot:
    def __init__(self):
        self.chat_history = self.load_chat_history()
        self.current_topic = None
        
    def load_chat_history(self) -> List[Dict]:
        """Load chat history from file."""
        if os.path.exists(CHAT_HISTORY_FILE):
            try:
                with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_chat_history(self):
        """Save chat history to file."""
        try:
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history[-50:], f, indent=2)  # Keep last 50 messages
        except Exception as e:
            print(f"Warning: Could not save chat history: {e}")
    
    def add_to_history(self, role: str, content: str):
        """Add message to chat history."""
        self.chat_history.append({"role": role, "content": content})
        self.save_chat_history()
    
    def get_claude_response(self, user_message: str) -> str:
        """Get response from Claude API."""
        try:
            # Build conversation context
            messages = []
            
            # Add recent chat history (last 10 messages for context)
            recent_history = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # System prompt for the chatbot
            system_prompt = f"""You are a helpful Python programming tutor chatbot. Your goal is to:

1. Help users learn Python programming concepts
2. Answer questions about Python clearly and concisely
3. Provide code examples when helpful
4. Be encouraging and supportive
5. Suggest topics to learn if users seem lost

Available topics you can teach:
{', '.join(AVAILABLE_TOPICS)}

Current topic being discussed: {self.current_topic or 'None'}

Guidelines:
- Keep responses conversational and friendly
- Use simple language for beginners
- Provide practical examples
- If asked about topics outside Python, politely redirect to Python learning
- If someone asks for a lesson or quiz, offer to create structured content
- Always be encouraging and patient"""

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.3,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def generate_lesson(self, topic: str) -> Dict[str, Any]:
        """Generate a structured lesson for a topic."""
        prompt = f"""Create a comprehensive Python lesson about "{topic}". 
        
        Provide the response as a JSON object with this structure:
        {{
            "title": "{topic}",
            "content": [
                "Introduction paragraph",
                "Key concepts explanation",
                "Code example with comments",
                "Practice exercise",
                "Summary"
            ]
        }}
        
        Make sure the content is beginner-friendly and includes working Python code examples."""
        
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                json_str = json_match.group(0)
                lesson_data = json.loads(json_str)
                
                # Save lesson to file
                filename = f"{topic.lower().replace(' ', '_')}_lesson.json"
                filepath = os.path.join(LESSONS_DIR, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(lesson_data, f, indent=4)
                
                return lesson_data
            else:
                return {"error": "Could not extract lesson data"}
                
        except Exception as e:
            return {"error": f"Failed to generate lesson: {str(e)}"}
    
    def generate_quiz(self, topic: str, num_questions: int = 5) -> Dict[str, Any]:
        """Generate a quiz for a topic."""
        prompt = f"""Create a Python quiz about "{topic}" with {num_questions} multiple choice questions.
        
        Provide the response as a JSON object with this structure:
        {{
            "title": "{topic} Quiz",
            "questions": [
                {{
                    "question": "Question text here?",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "answer": "A) Option 1",
                    "explanation": "Brief explanation of why this is correct"
                }}
            ]
        }}
        
        Make questions practical and test real understanding of {topic}."""
        
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                json_str = json_match.group(0)
                quiz_data = json.loads(json_str)
                
                # Save quiz to file
                filename = f"{topic.lower().replace(' ', '_')}_quiz.json"
                filepath = os.path.join(QUIZZES_DIR, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(quiz_data, f, indent=4)
                
                return quiz_data
            else:
                return {"error": "Could not extract quiz data"}
                
        except Exception as e:
            return {"error": f"Failed to generate quiz: {str(e)}"}
    
    def detect_intent(self, user_message: str) -> Dict[str, Any]:
        """Detect user intent from their message."""
        message_lower = user_message.lower()
        
        # Check for lesson requests
        if any(word in message_lower for word in ['lesson', 'teach', 'learn', 'explain', 'tutorial']):
            for topic in AVAILABLE_TOPICS:
                if topic.lower() in message_lower:
                    return {"intent": "lesson", "topic": topic}
            return {"intent": "lesson", "topic": None}
        
        # Check for quiz requests
        if any(word in message_lower for word in ['quiz', 'test', 'questions', 'practice']):
            for topic in AVAILABLE_TOPICS:
                if topic.lower() in message_lower:
                    return {"intent": "quiz", "topic": topic}
            return {"intent": "quiz", "topic": None}
        
        # Check for topic selection
        for topic in AVAILABLE_TOPICS:
            if topic.lower() in message_lower:
                return {"intent": "topic", "topic": topic}
        
        return {"intent": "chat", "topic": None}
    
    def handle_user_input(self, user_message: str) -> str:
        """Process user input and return appropriate response."""
        # Add user message to history
        self.add_to_history("user", user_message)
        
        # Detect intent
        intent_data = self.detect_intent(user_message)
        intent = intent_data["intent"]
        topic = intent_data["topic"]
        
        response = ""
        
        if intent == "lesson" and topic:
            # Generate lesson
            self.current_topic = topic
            lesson_data = self.generate_lesson(topic)
            
            if "error" not in lesson_data:
                response = f"Great! I've created a lesson on {topic} for you.\n\n"
                response += f"**{lesson_data['title']}**\n\n"
                for i, content_item in enumerate(lesson_data['content'], 1):
                    response += f"{i}. {content_item}\n\n"
                response += f"The complete lesson has been saved to your lessons folder. Would you like to take a quiz on {topic} next?"
            else:
                response = f"I had trouble creating the lesson: {lesson_data['error']}. Let me give you a general overview instead."
                response = self.get_claude_response(f"Explain {topic} in Python programming")
        
        elif intent == "quiz" and topic:
            # Generate quiz
            self.current_topic = topic
            quiz_data = self.generate_quiz(topic)
            
            if "error" not in quiz_data:
                response = f"Here's a quiz on {topic}!\n\n"
                response += f"**{quiz_data['title']}**\n\n"
                for i, q in enumerate(quiz_data['questions'], 1):
                    response += f"**Question {i}:** {q['question']}\n"
                    for option in q['options']:
                        response += f"  {option}\n"
                    response += f"\n*Answer: {q['answer']}*\n"
                    if 'explanation' in q:
                        response += f"*Explanation: {q['explanation']}*\n\n"
                response += "The complete quiz has been saved to your quizzes folder!"
            else:
                response = f"I had trouble creating the quiz: {quiz_data['error']}. Let me ask you some questions about {topic} instead."
                response = self.get_claude_response(f"Ask me a few questions about {topic} in Python")
        
        elif intent == "topic" and topic:
            # Set current topic and provide overview
            self.current_topic = topic
            response = self.get_claude_response(f"The user wants to learn about {topic} in Python. Give them an encouraging overview and ask what they'd like to do - learn with a lesson, practice with a quiz, or ask specific questions.")
        
        else:
            # General chat response
            response = self.get_claude_response(user_message)
        
        # Add bot response to history
        self.add_to_history("assistant", response)
        
        return response
    
    def start_chat(self):
        """Start the interactive chat session."""
        print("🐍 Python Learning Chatbot")
        print("=" * 50)
        print("Hi! I'm your Python programming tutor. I can help you:")
        print("• Learn Python concepts with interactive lessons")
        print("• Practice with quizzes and exercises") 
        print("• Answer your Python programming questions")
        print("• Guide you through coding problems")
        print("\nAvailable topics:")
        for i, topic in enumerate(AVAILABLE_TOPICS, 1):
            print(f"  {i}. {topic}")
        print("\nType 'quit' or 'exit' to end the conversation.")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n🤖 Bot: Happy coding! Feel free to come back anytime to continue learning Python! 🚀")
                    break
                
                if not user_input:
                    continue
                
                print("\n🤖 Bot: ", end="")
                response = self.handle_user_input(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n🤖 Bot: Goodbye! Keep practicing Python! 👋")
                break
            except Exception as e:
                print(f"\n🤖 Bot: I encountered an error: {e}. Please try again.")

def main():
    """Main function to start the chatbot."""
    try:
        chatbot = PythonLearningChatbot()
        chatbot.start_chat()
    except Exception as e:
        print(f"Error starting chatbot: {e}")
        print("Make sure you have set the ANTHROPIC_API_KEY environment variable.")

if __name__ == "__main__":
    # Install required package if not already installed
    try:
        import anthropic
    except ImportError:
        print("Installing required package...")
        os.system("pip install anthropic")
        import anthropic
    
    main()