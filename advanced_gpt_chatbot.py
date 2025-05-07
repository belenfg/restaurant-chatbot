#!/usr/bin/env python3
# Advanced GPT Chatbot for Restaurant Management

import os
import json
import re
import random
import datetime
from typing import Dict, List, Any, Optional, Tuple

# AI integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AIHandler:
    """Handles integration with AI models (OpenAI or Anthropic)"""
    
    def __init__(self, model_type="openai", api_key=None):
        self.model_type = model_type
        self.api_key = api_key
        self.client = None
        self.initialized = False
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the AI client based on provided credentials"""
        if self.model_type == "openai" and OPENAI_AVAILABLE:
            if self.api_key:
                openai.api_key = self.api_key
                self.client = openai
                self.initialized = True
                print("OpenAI integration enabled.")
            else:
                print("OpenAI API key not provided.")
        elif self.model_type == "anthropic" and ANTHROPIC_AVAILABLE:
            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.initialized = True
                print("Anthropic integration enabled.")
            else:
                print("Anthropic API key not provided.")
        else:
            print(f"AI integration for {self.model_type} not available.")
    
    def generate_response(self, prompt: str, conversation_history: List[Dict[str, str]] = None, 
                          system_message: str = None) -> str:
        """Generate a response using the configured AI model"""
        if not self.initialized:
            return "AI integration not available. Using fallback responses."
        
        try:
            if self.model_type == "openai":
                messages = []
                
                # Add system message if provided
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                
                # Add conversation history
                if conversation_history:
                    for message in conversation_history:
                        messages.append(message)
                
                # Add the current prompt
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Can be updated to newer models
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7
                )
                
                return response.choices[0].message.content
                
            elif self.model_type == "anthropic":
                # Prepare conversation for Claude
                full_prompt = ""
                
                if conversation_history:
                    for message in conversation_history:
                        if message["role"] == "user":
                            full_prompt += f"Human: {message['content']}\n\n"
                        elif message["role"] == "assistant":
                            full_prompt += f"Assistant: {message['content']}\n\n"
                
                full_prompt += f"Human: {prompt}\n\nAssistant: "
                
                response = self.client.completions.create(
                    model="claude-2",  # Can be updated to newer models
                    prompt=full_prompt,
                    max_tokens_to_sample=300,
                    temperature=0.7,
                    system=system_message if system_message else ""
                )
                
                return response.completion
                
        except Exception as e:
            print(f"Error with AI generation: {e}")
            return "I'm having trouble connecting to my AI service. Let me use my standard responses instead."


class RestaurantChatbot:
    """Main chatbot class for restaurant interactions"""
    
    def __init__(self, ai_config: Dict = None):
        # Initialize AI if config provided
        if ai_config and (ai_config.get("model_type") and ai_config.get("api_key")):
            self.ai = AIHandler(
                model_type=ai_config.get("model_type"),
                api_key=ai_config.get("api_key")
            )
        else:
            self.ai = None
        
        # User context
        self.context = {
            "user_name": None,
            "last_topic": None,
            "in_reservation_process": False,
            "reservation_data": {}
        }
        
        # Conversation memory
        self.conversation_history = []
        
        # Import restaurant data from other modules
        # Use conditional import to handle potential file name differences
        try:
            # If the original file was renamed to a proper module name
            from restaurant_chatbot import RestaurantDB, RestaurantInfo
        except ImportError:
            try:
                # If the original file kept its original name
                from paste import RestaurantDB, RestaurantInfo
            except ImportError:
                print("Error: Could not import RestaurantDB and RestaurantInfo classes.")
                print("Make sure restaurant_chatbot.py or paste.py is in the same directory.")
                exit(1)
                
        self.db = RestaurantDB()
        self.info = RestaurantInfo()
        
        # Standard responses
        self.fallback_responses = {
            "greeting": [
                "Welcome to The Good Table! How can I help you today?",
                "Hello! Thanks for reaching out to The Good Table. What can I do for you?",
                "Hi there! I'm the virtual assistant for The Good Table. How may I assist you?"
            ],
            "goodbye": [
                "Thank you for chatting with us! Have a great day!",
                "We hope to see you soon at The Good Table! Goodbye!",
                "Thank you for your interest in The Good Table. Feel free to reach out again!"
            ],
            "thanks": [
                "You're welcome! Is there anything else I can help you with?",
                "My pleasure! Let me know if you need anything else.",
                "Happy to help! Anything else you'd like to know about The Good Table?"
            ],
            "not_understood": [
                "I'm not sure I understand. Could you please rephrase that?",
                "I didn't quite catch that. How else can I help you?",
                "I'm still learning! Could you try asking in a different way?"
            ]
        }
    
    def _add_to_history(self, role: str, content: str):
        """Add a message to the conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        # Keep history manageable (last 10 messages)
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def _get_system_prompt(self) -> str:
        """Create a system prompt for the AI with current context"""
        restaurant_info = f"""
        You are a virtual assistant for {self.info.NAME}, a restaurant located at {self.info.ADDRESS}.
        The restaurant's phone number is {self.info.PHONE} and email is {self.info.EMAIL}.
        
        Opening hours:
        """
        
        for day, hours in self.info.SCHEDULE.items():
            restaurant_info += f"- {day}: {hours}\n"
        
        restaurant_info += "\nMenu categories include: "
        for category, items in self.info.MENU_CATEGORIES.items():
            restaurant_info += f"\n- {category}: {', '.join(items)}"
        
        system_prompt = f"""
        {restaurant_info}
        
        Your role is to help customers with information and reservations. Be friendly, helpful, and concise.
        """
        
        # Add personalization if we know the user
        if self.context["user_name"]:
            returning = self.db.is_returning_customer(self.context["user_name"])
            if returning:
                system_prompt += f"\nYou're speaking with {self.context['user_name']}, a returning customer."
            else:
                system_prompt += f"\nYou're speaking with {self.context['user_name']}."
        
        return system_prompt
    
    def _extract_user_name(self, message: str) -> Optional[str]:
        """Try to extract user name from introduction messages"""
        name_patterns = [
            r"my name is ([\w\s]+)",
            r"i am ([\w\s]+)",
            r"i'm ([\w\s]+)",
            r"call me ([\w\s]+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message.lower())
            if match:
                # Clean up extracted name
                name = match.group(1).strip()
                # Remove trailing punctuation or words like "and", "I", etc.
                name = re.sub(r'\s+and\s+.*$|\s+i\s+.*$|[,.!?]$', '', name)
                return name.title()
        
        return None
    
    def _detect_intent(self, message: str) -> str:
        """Detect the primary intent of the user message"""
        message = message.lower()
        
        if re.search(r'(hi|hello|hey|greetings)', message):
            return "greeting"
            
        if re.search(r'(bye|goodbye|see you|farewell)', message):
            return "goodbye"
            
        if re.search(r'(thanks|thank you|appreciate)', message):
            return "thanks"
            
        if re.search(r'(reserve|reservation|book|table)', message):
            return "reservation"
            
        if re.search(r'(menu|food|eat|dish|cuisine)', message):
            return "menu"
            
        if re.search(r'(hour|open|close|schedule|time)', message):
            return "hours"
            
        if re.search(r'(where|location|address|direction)', message):
            return "location"
            
        if re.search(r'(call|phone|contact|email)', message):
            return "contact"
            
        return "general"
    
    def _handle_reservation_intent(self, message: str) -> str:
        """Handle reservation-related intents"""
        # Extract date (YYYY-MM-DD)
        date_match = re.search(r'(\d{4}-\d{2}-\d{2}|tomorrow|today|next \w+)', message.lower())
        if date_match:
            date_str = date_match.group(1)
            if date_str == "today":
                date = datetime.date.today()
            elif date_str == "tomorrow":
                date = datetime.date.today() + datetime.timedelta(days=1)
            elif date_str.startswith("next"):
                # Handle "next Wednesday" etc.
                day_name = date_str.split(" ")[1]
                day_mapping = {
                    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                    "friday": 4, "saturday": 5, "sunday": 6
                }
                today = datetime.date.today()
                target_day = day_mapping.get(day_name.lower())
                if target_day is not None:
                    days_ahead = (target_day - today.weekday()) % 7
                    if days_ahead == 0:  # If today is the target day, go to next week
                        days_ahead = 7
                    date = today + datetime.timedelta(days=days_ahead)
            else:
                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    date = None
            
            if date:
                self.context["reservation_data"]["date"] = date.strftime("%Y-%m-%d")
        
        # Extract time (HH:MM)
        time_match = re.search(r'(\d{1,2}:\d{2}|\d{1,2}(?:\s?[ap]m)?)', message.lower())
        if time_match:
            time_str = time_match.group(1)
            # Convert to 24-hour format if needed
            if "pm" in time_str.lower() and ":" in time_str:
                hour, minute = time_str.lower().replace("pm", "").strip().split(":")
                if int(hour) < 12:
                    time_str = f"{int(hour) + 12}:{minute}"
            elif "pm" in time_str.lower():
                hour = time_str.lower().replace("pm", "").strip()
                if int(hour) < 12:
                    time_str = f"{int(hour) + 12}:00"
            elif "am" in time_str.lower() and ":" in time_str:
                time_str = time_str.lower().replace("am", "").strip()
            elif "am" in time_str.lower():
                hour = time_str.lower().replace("am", "").strip()
                time_str = f"{hour}:00"
            elif ":" not in time_str:
                time_str = f"{time_str}:00"
            
            self.context["reservation_data"]["time"] = time_str
        
        # Extract number of people
        people_match = re.search(r'(\d+)\s+(?:people|persons|guests)', message.lower())
        if people_match:
            self.context["reservation_data"]["people"] = int(people_match.group(1))
        
        # Check if we have all required information
        required_fields = ["date", "time", "people"]
        missing_fields = [field for field in required_fields if field not in self.context["reservation_data"]]
        
        if not missing_fields:
            # All required fields are present
            self.context["in_reservation_process"] = False
            
            # Validate the reservation data
            date_str = self.context["reservation_data"]["date"]
            time_str = self.context["reservation_data"]["time"]
            people = self.context["reservation_data"]["people"]
            
            # Check date is valid (restaurant open)
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            day_name = date_obj.strftime("%A")
            if self.info.SCHEDULE.get(day_name) == "Closed":
                return f"I'm sorry, but we're closed on {day_name}s. Would you like to choose another day?"
            
            # Check time is within opening hours
            if day_name in self.info.SCHEDULE:
                hours = self.info.SCHEDULE[day_name]
                if hours != "Closed":
                    opening, closing = hours.split(" - ")
                    opening_hour = int(opening.split(":")[0])
                    closing_hour, closing_minute = map(int, closing.split(":"))
                    
                    # Convert reservation time to comparable format
                    res_hour, res_minute = map(int, time_str.split(":"))
                    
                    # Check if time is within opening hours
                    if (res_hour < opening_hour or 
                        (res_hour == closing_hour and res_minute > closing_minute) or
                        res_hour > closing_hour):
                        return f"I'm sorry, but our opening hours on {day_name} are {hours}. Would you like to choose another time?"
            
            # Check people count
            if people > 10:
                return "I'm sorry, but we can only accommodate groups of up to 10 people. For larger groups, please call us directly."
            
            # If everything is valid, create the reservation
            name = self.context["user_name"] if self.context["user_name"] else "Guest"
            phone = "N/A"  # In a real scenario, you'd collect this
            
            success = self.db.add_reservation(date_str, time_str, name, people, phone)
            
            if success:
                response = f"Great! I've booked a table for {people} on {date_str} at {time_str} under the name {name}."
                if self.context["user_name"] and self.db.is_returning_customer(self.context["user_name"]):
                    response += f" It's always a pleasure to have you back, {self.context['user_name']}!"
                else:
                    response += " We look forward to seeing you!"
                
                # Reset reservation data
                self.context["reservation_data"] = {}
                return response
            else:
                return "I'm sorry, but that time slot is fully booked. Would you like to try another time?"
        else:
            # Need more information
            self.context["in_reservation_process"] = True
            
            if "date" not in self.context["reservation_data"]:
                return "What day would you like to make a reservation for?"
            elif "time" not in self.context["reservation_data"]:
                return f"What time would you like to reserve a table on {self.context['reservation_data']['date']}?"
            elif "people" not in self.context["reservation_data"]:
                return "How many people will be dining?"
    
    def _handle_menu_intent(self) -> str:
        """Provide information about the menu"""
        menu_response = "Here's a brief overview of our menu:\n\n"
        
        for category, items in self.info.MENU_CATEGORIES.items():
            menu_response += f"*{category}*: {', '.join(items)}\n"
        
        menu_response += "\nIs there a specific dish you'd like to know more about?"
        return menu_response
    
    def _handle_hours_intent(self) -> str:
        """Provide information about opening hours"""
        hours_response = "Our opening hours are:\n\n"
        
        for day, hours in self.info.SCHEDULE.items():
            hours_response += f"- {day}: {hours}\n"
        
        today = datetime.datetime.today().strftime("%A")
        hours_today = self.info.SCHEDULE.get(today)
        hours_response += f"\nToday ({today}) we're {hours_today}."
        
        return hours_response
    
    def _handle_location_intent(self) -> str:
        """Provide location information"""
        return f"We're located at {self.info.ADDRESS}. You can find us on our website: {self.info.WEBSITE}"
    
    def _handle_contact_intent(self) -> str:
        """Provide contact information"""
        return f"You can reach us by phone at {self.info.PHONE} or by email at {self.info.EMAIL}."
    
    def _fallback_response(self, intent: str) -> str:
        """Return a fallback response for the given intent"""
        if intent in self.fallback_responses:
            return random.choice(self.fallback_responses[intent])
        return random.choice(self.fallback_responses["not_understood"])
    
    def process_message(self, message: str) -> str:
        """Process a user message and return a response"""
        # Try to extract user name if not known yet
        if not self.context["user_name"]:
            name = self._extract_user_name(message)
            if name:
                self.context["user_name"] = name
        
        # Add user message to history
        self._add_to_history("user", message)
        
        # Check if we're in the middle of a reservation process
        if self.context["in_reservation_process"]:
            response = self._handle_reservation_intent(message)
            self._add_to_history("assistant", response)
            return response
        
        # Detect intent
        intent = self._detect_intent(message)
        self.context["last_topic"] = intent
        
        # Try to use AI if available
        if self.ai and self.ai.initialized:
            try:
                ai_response = self.ai.generate_response(
                    prompt=message,
                    conversation_history=self.conversation_history,
                    system_message=self._get_system_prompt()
                )
                
                self._add_to_history("assistant", ai_response)
                return ai_response
            except Exception as e:
                print(f"AI error: {e}. Falling back to rule-based responses.")
                # Continue with rule-based responses
        
        # Rule-based response generation
        if intent == "greeting":
            greeting = self._fallback_response("greeting")
            if self.context["user_name"]:
                greeting = f"Hello, {self.context['user_name']}! " + greeting.split("! ", 1)[1]
            self._add_to_history("assistant", greeting)
            return greeting
            
        elif intent == "goodbye":
            goodbye = self._fallback_response("goodbye")
            self._add_to_history("assistant", goodbye)
            return goodbye
            
        elif intent == "thanks":
            thanks = self._fallback_response("thanks")
            self._add_to_history("assistant", thanks)
            return thanks
            
        elif intent == "reservation":
            response = self._handle_reservation_intent(message)
            self._add_to_history("assistant", response)
            return response
            
        elif intent == "menu":
            response = self._handle_menu_intent()
            self._add_to_history("assistant", response)
            return response
            
        elif intent == "hours":
            response = self._handle_hours_intent()
            self._add_to_history("assistant", response)
            return response
            
        elif intent == "location":
            response = self._handle_location_intent()
            self._add_to_history("assistant", response)
            return response
            
        elif intent == "contact":
            response = self._handle_contact_intent()
            self._add_to_history("assistant", response)
            return response
            
        else:
            # General query we don't have a specific handler for
            fallback = self._fallback_response("not_understood")
            self._add_to_history("assistant", fallback)
            return fallback


def run_chatbot_cli():
    """Function to run the chatbot CLI - separated from main for modularity"""
    print("===== The Good Table Restaurant Chatbot =====")
    print("Loading AI capabilities...")
    
    # Check for API keys in environment variables
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    ai_config = None
    if openai_key:
        ai_config = {"model_type": "openai", "api_key": openai_key}
        print("OpenAI API key found.")
    elif anthropic_key:
        ai_config = {"model_type": "anthropic", "api_key": anthropic_key}
        print("Anthropic API key found.")
    else:
        print("No AI API keys found. Running in standard mode.")
    
    # Initialize chatbot
    chatbot = RestaurantChatbot(ai_config)
    
    print("\nWelcome to The Good Table virtual assistant!")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    # Initial greeting
    print("Chatbot: " + random.choice(chatbot.fallback_responses["greeting"]))
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print("\nChatbot: " + random.choice(chatbot.fallback_responses["goodbye"]))
            break
        
        response = chatbot.process_message(user_input)
        print("\nChatbot:", response)

# This code only runs if this file is executed directly, not when imported