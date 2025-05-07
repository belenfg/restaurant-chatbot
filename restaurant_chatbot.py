#!/usr/bin/env python3
# Chatbot for Restaurant "The Good Table"
# Manages reservations, FAQs, and maintains conversation context

import re
import json
import datetime
import random
import os
from typing import Dict, List, Tuple, Optional, Any

class RestaurantDB:
    """Database simulation for the restaurant"""
    
    def __init__(self):
        # Structure to store reservations: {date: {time: [list of reservations]}}
        self.reservations = {}
        # Remembered customers
        self.customers = {}
        # Load data if exists
        self._load_data()
    
    def _load_data(self):
        """Load saved data if it exists"""
        try:
            if os.path.exists('reservations.json'):
                with open('reservations.json', 'r') as f:
                    self.reservations = json.load(f)
            if os.path.exists('customers.json'):
                with open('customers.json', 'r') as f:
                    self.customers = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def _save_data(self):
        """Save current data"""
        try:
            with open('reservations.json', 'w') as f:
                json.dump(self.reservations, f)
            with open('customers.json', 'w') as f:
                json.dump(self.customers, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_reservation(self, date: str, time: str, name: str, people: int, phone: str) -> bool:
        """Add a new reservation to the database"""
        if date not in self.reservations:
            self.reservations[date] = {}
        
        if time not in self.reservations[date]:
            self.reservations[date][time] = []
        
        # Check if there are too many reservations for that time (simplified)
        if len(self.reservations[date][time]) >= 5:  # Maximum 5 tables per hour
            return False
        
        # Add the reservation
        self.reservations[date][time].append({
            "name": name,
            "people": people,
            "phone": phone,
            "id": f"{date}-{time}-{len(self.reservations[date][time]) + 1}"
        })
        
        # Save the customer if new
        if name.lower() not in self.customers:
            self.customers[name.lower()] = {
                "name": name,
                "phone": phone,
                "visits": 1,
                "last_visit": date
            }
        else:
            self.customers[name.lower()]["visits"] += 1
            self.customers[name.lower()]["last_visit"] = date
        
        self._save_data()
        return True
    
    def view_reservations(self, date: str) -> Dict:
        """Returns all reservations for a specific date"""
        if date in self.reservations:
            return self.reservations[date]
        return {}
    
    def is_returning_customer(self, name: str) -> bool:
        """Checks if the customer is a returning one"""
        return name.lower() in self.customers and self.customers[name.lower()]["visits"] > 1


class RestaurantValidator:
    """Class for restaurant data validation"""
    
    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, str]:
        """Validates date format and if the restaurant is open that day"""
        try:
            # Try to convert to date
            date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
            day_of_week = date.weekday()
            
            # Restaurant closed Monday and Tuesday (0=Monday, 1=Tuesday)
            if day_of_week in [0, 1]:
                return False, "Sorry, the restaurant is closed on Mondays and Tuesdays."
            
            # Don't allow reservations in the past
            today = datetime.datetime.now().date()
            if date.date() < today:
                return False, "I can't make reservations for past dates."
            
            # Don't allow reservations more than 30 days in advance
            one_month = today + datetime.timedelta(days=30)
            if date.date() > one_month:
                return False, "We only accept reservations with a maximum of 30 days in advance."
                
            return True, ""
        except ValueError:
            return False, "Incorrect date format. Use DD/MM/YYYY (example: 15/05/2025)."
    
    @staticmethod
    def validate_time(time_str: str) -> Tuple[bool, str]:
        """Validates if the time is in the correct range"""
        try:
            # Convert to 24-hour format if it has AM/PM
            if "am" in time_str.lower() or "pm" in time_str.lower():
                time = datetime.datetime.strptime(time_str, "%I:%M %p").time()
            else:
                time = datetime.datetime.strptime(time_str, "%H:%M").time()
            
            # Restaurant hours: 10:00 - 23:30
            opening_time = datetime.time(10, 0)
            closing_time = datetime.time(23, 30)
            
            if time < opening_time or time > closing_time:
                return False, "Our hours are from 10:00 to 23:30."
            
            # Validate that they are 30-minute intervals
            if time.minute not in [0, 30]:
                return False, "Reservations can only be made at 30-minute intervals (XX:00 or XX:30)."
                
            return True, ""
        except ValueError:
            return False, "Incorrect time format. Use HH:MM (example: 19:30)."
    
    @staticmethod
    def validate_people(num_str: str) -> Tuple[bool, str]:
        """Validates if the number of people is valid"""
        try:
            num = int(num_str)
            if num <= 0:
                return False, "The number of people must be positive."
            if num > 10:
                return False, "For groups of more than 10 people, please call us directly."
            return True, ""
        except ValueError:
            return False, "Please provide a valid number of people."


class RestaurantInfo:
    """Static information about the restaurant"""
    
    NAME = "The Good Table"
    ADDRESS = "123 Flavors Street, Gastronomic City"
    PHONE = "+1 123 456 7890"
    EMAIL = "info@thegoodtable.com"
    WEBSITE = "www.thegoodtable.com"
    
    SCHEDULE = {
        "Wednesday": "10:00 - 23:30",
        "Thursday": "10:00 - 23:30",
        "Friday": "10:00 - 23:30",
        "Saturday": "10:00 - 23:30",
        "Sunday": "10:00 - 23:30",
        "Monday": "Closed",
        "Tuesday": "Closed"
    }
    
    MENU_CATEGORIES = {
        "Starters": ["Mediterranean salad", "Homemade croquettes", "Andalusian gazpacho", "Cheese board"],
        "Main Courses": ["Valencian paella", "Whiskey sirloin steak", "Cod confit", "Mushroom risotto"],
        "Desserts": ["Cheesecake", "Chocolate coulant", "Homemade tiramisu", "Lemon sorbet"],
        "Drinks": ["House wines", "Craft beers", "Soft drinks", "Special cocktails"]
    }
    
    FAQ = {
        "schedule": "Our restaurant is open Wednesday to Sunday, from 10:00 to 23:30. We are closed on Mondays and Tuesdays.",
        "location": f"We are located at {ADDRESS}. We're a 5-minute walk from the Main Square and we have parking for customers.",
        "reservations": f"You can make your reservation right here with me, or by calling {PHONE}.",
        "menu": "We offer Mediterranean cuisine with fusion touches. We have options for vegetarians and vegans. Our most popular dishes are the Valencian paella and the whiskey sirloin steak.",
        "events": "We organize private events and celebrations. For more information, write to events@thegoodtable.com",
        "payments": "We accept cash and all major credit cards. We also work with mobile payments.",
        "contact": f"You can contact us by phone ({PHONE}) or email ({EMAIL})."
    }


class RestaurantChatbot:
    """Main chatbot class"""
    
    def __init__(self, use_ai=False, api_key=None):
        self.db = RestaurantDB()
        self.validator = RestaurantValidator()
        self.info = RestaurantInfo()
        
        # Conversation state
        self.context = {
            "user_name": None,
            "in_reservation_process": False,
            "reservation_data": {},
            "last_topic": None
        }
        
        # AI integration (optional)
        self.use_ai = use_ai
        self.api_key = api_key
        if use_ai:
            try:
                self._configure_ai()
            except Exception as e:
                print(f"Could not configure AI integration: {e}")
                self.use_ai = False
                
    def _configure_ai(self):
        """Configure OpenAI/GPT integration"""
        if self.use_ai:
            try:
                import openai
                openai.api_key = self.api_key
                self.openai = openai
            except ImportError:
                print("To use AI integration, install the openai package with: pip install openai")
                self.use_ai = False
    
    def generate_ai_response(self, user_message: str, context: Dict) -> str:
        """Generate a response using OpenAI API"""
        if not self.use_ai:
            return None
            
        try:
            # Create a prompt with context
            prompt = f"You are a friendly chatbot for the restaurant {self.info.NAME}.\n"
            
            if context["user_name"]:
                prompt += f"You're talking to {context['user_name']}. "
                
                if self.db.is_returning_customer(context["user_name"]):
                    prompt += "They're a returning customer, be friendly and familiar. "
                else:
                    prompt += "They're a new customer, be welcoming. "
            
            if context["last_topic"]:
                prompt += f"The last conversation topic was: {context['last_topic']}. "
                
            prompt += f"\nUser message: {user_message}\n\nYour response (friendly and concise):"
            
            # Call the API
            response = self.openai.Completion.create(
                engine="text-davinci-003",  # or your preferred model
                prompt=prompt,
                max_tokens=150,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return None
    
    def process_message(self, message: str) -> str:
        """Process the user's message and generate a response"""
        message = message.strip()
        
        # If we have AI integration, try to use it first
        if self.use_ai:
            ai_response = self.generate_ai_response(message, self.context)
            if ai_response:
                return ai_response
        
        # Detect greeting and introduce yourself
        if self._is_greeting(message):
            return self._generate_greeting()
        
        # Reservation process in progress
        if self.context["in_reservation_process"]:
            return self._continue_reservation_process(message)
        
        # Detect intention
        if self._is_about_reservation(message):
            self.context["in_reservation_process"] = True
            self.context["last_topic"] = "reservation"
            self.context["reservation_data"] = {}
            return "Perfect! Let's make your reservation. What date would you like to reserve? (format DD/MM/YYYY)"
        
        # Detect questions about restaurant information
        info_response = self._answer_info_question(message)
        if info_response:
            return info_response
        
        # Detect if they're giving their name
        detected_name = self._detect_name(message)
        if detected_name:
            self.context["user_name"] = detected_name
            if self.db.is_returning_customer(detected_name):
                return f"Great to see you again, {detected_name}! How can I help you today?"
            else:
                return f"Nice to meet you, {detected_name}! How can I help you?"
        
        # Detect farewell
        if self._is_farewell(message):
            return self._generate_farewell()
        
        # Default answer
        return self._default_response()
    
    def _is_greeting(self, message: str) -> bool:
        """Detect if the message is a greeting"""
        greetings = ["hello", "hi", "good morning", "good afternoon", "good evening", "hey", "greetings"]
        return any(greeting in message.lower() for greeting in greetings)
    
    def _generate_greeting(self) -> str:
        """Generate a personalized greeting"""
        current_hour = datetime.datetime.now().hour
        
        if current_hour < 12:
            base_greeting = "Good morning"
        elif current_hour < 20:
            base_greeting = "Good afternoon"
        else:
            base_greeting = "Good evening"
        
        if self.context["user_name"]:
            greeting = f"{base_greeting}, {self.context['user_name']}! "
            if self.db.is_returning_customer(self.context["user_name"]):
                greeting += "It's a pleasure to have you back. "
        else:
            greeting = f"{base_greeting}! I'm the virtual assistant at {self.info.NAME}. "
            greeting += "Could you tell me your name so I can assist you better? "
        
        greeting += "How can I help you today?"
        return greeting
    
    def _is_about_reservation(self, message: str) -> bool:
        """Detect if the message is about making a reservation"""
        keywords = ["reservation", "reserve", "book", "table", "make a booking"]
        return any(word in message.lower() for word in keywords)
    
    def _continue_reservation_process(self, message: str) -> str:
        """Continue the reservation process according to the current state"""
        data = self.context["reservation_data"]
        
        # Ask for date
        if "date" not in data:
            valid, error = self.validator.validate_date(message)
            if valid:
                data["date"] = message
                return "What time would you like to reserve? (Format HH:MM, for example 19:30)"
            else:
                return f"{error} What date would you like to reserve? (format DD/MM/YYYY)"
        
        # Ask for time
        if "time" not in data:
            valid, error = self.validator.validate_time(message)
            if valid:
                data["time"] = message
                return "How many people will be in your party?"
            else:
                return f"{error} What time would you like to reserve? (Format HH:MM)"
        
        # Ask for number of people
        if "people" not in data:
            valid, error = self.validator.validate_people(message)
            if valid:
                data["people"] = int(message)
                
                # If we don't have the name yet
                if not self.context["user_name"]:
                    return "Under what name should I make the reservation?"
                else:
                    data["name"] = self.context["user_name"]
                    return "Could you provide a contact phone number?"
            else:
                return f"{error} How many people will be in your party?"
        
        # Ask for name if we don't have it
        if "name" not in data:
            data["name"] = message
            self.context["user_name"] = message  # Save the name in the context
            return "Could you provide a contact phone number?"
        
        # Ask for phone
        if "phone" not in data:
            # A simple phone validation
            if re.match(r'^\+?[\d\s]{9,15}$', message):
                data["phone"] = message
                
                # Confirm reservation
                confirmation = (
                    f"Perfect. I confirm your reservation:\n"
                    f"- Date: {data['date']}\n"
                    f"- Time: {data['time']}\n"
                    f"- People: {data['people']}\n"
                    f"- Name: {data['name']}\n"
                    f"- Phone: {data['phone']}\n\n"
                    f"Is this information correct? (yes/no)"
                )
                self.context["last_topic"] = "reservation_confirmation"
                return confirmation
            else:
                return "The phone format doesn't seem correct. Please enter a valid number."
        
        # Confirm reservation
        if self.context["last_topic"] == "reservation_confirmation":
            if message.lower() in ["yes", "correct", "perfect"]:
                # Save the reservation
                success = self.db.add_reservation(
                    data["date"], 
                    data["time"], 
                    data["name"], 
                    data["people"], 
                    data["phone"]
                )
                
                if success:
                    self.context["in_reservation_process"] = False
                    self.context["last_topic"] = "reservation_completed"
                    
                    if self.db.is_returning_customer(data["name"]):
                        return f"Reservation confirmed, {data['name']}! Thank you for trusting us again. We look forward to seeing you on {data['date']} at {data['time']}. Can I help you with anything else?"
                    else:
                        return f"Reservation confirmed, {data['name']}! We look forward to seeing you on {data['date']} at {data['time']}. It will be a pleasure to welcome you to {self.info.NAME}. Do you need anything else?"
                else:
                    self.context["in_reservation_process"] = False
                    return "I'm sorry, it seems there's no availability for that date and time. Would you like to try another time?"
            
            elif message.lower() in ["no", "incorrect"]:
                self.context["reservation_data"] = {}
                return "Alright, let's start over. What date would you like to reserve? (format DD/MM/YYYY)"
            
            else:
                return "Please confirm if the reservation information is correct by answering 'yes' or 'no'."
    
    def _answer_info_question(self, message: str) -> Optional[str]:
        """Answer questions about the restaurant"""
        message_lower = message.lower()
        
        # Schedule
        if any(word in message_lower for word in ["schedule", "hours", "open", "closed"]):
            self.context["last_topic"] = "schedule"
            return self.info.FAQ["schedule"]
        
        # Location
        if any(word in message_lower for word in ["location", "address", "where", "directions"]):
            self.context["last_topic"] = "location"
            return self.info.FAQ["location"]
        
        # Menu
        if any(word in message_lower for word in ["menu", "food", "dishes", "eat"]):
            self.context["last_topic"] = "menu"
            return self.info.FAQ["menu"]
        
        # Contact
        if any(word in message_lower for word in ["contact", "phone", "call", "email"]):
            self.context["last_topic"] = "contact"
            return self.info.FAQ["contact"]
        
        # Events
        if any(word in message_lower for word in ["event", "celebration", "party", "birthday"]):
            self.context["last_topic"] = "events"
            return self.info.FAQ["events"]
        
        # Payment methods
        if any(word in message_lower for word in ["payment", "card", "cash", "pay"]):
            self.context["last_topic"] = "payments"
            return self.info.FAQ["payments"]
        
        return None
    
    def _detect_name(self, message: str) -> Optional[str]:
        """Try to detect if the user is providing their name"""
        name_patterns = [
            r"my name is (\w+)",
            r"i am (\w+)",
            r"i'm (\w+)",
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message.lower())
            if match:
                name = match.group(1)
                return name.capitalize()
        
        # If the message is short and has no common verbs, it might be just a name
        if len(message.split()) <= 2 and not any(word in message.lower() for word in ["is", "are", "have", "can", "do"]):
            return message.strip().split()[0].capitalize()
        
        return None
    
    def _is_farewell(self, message: str) -> bool:
        """Detect if the message is a farewell"""
        farewells = ["goodbye", "bye", "see you", "cya", "farewell", "I'm leaving"]
        return any(farewell in message.lower() for farewell in farewells)
    
    def _generate_farewell(self) -> str:
        """Generate a personalized farewell"""
        farewells = [
            "See you soon!",
            "Have an excellent day!",
            "Hope to see you soon at our restaurant!",
            "Thank you for contacting us!"
        ]
        
        farewell = random.choice(farewells)
        
        if self.context["user_name"]:
            farewell = f"Goodbye, {self.context['user_name']}! {farewell}"
        
        return farewell
    
    def _default_response(self) -> str:
        """Generate a default response when the intention is not understood"""
        responses = [
            "I'm not sure I understand what you need. Can you be more specific?",
            "I can help you with reservations or information about our restaurant. What would you like to know?",
            "Sorry, I didn't understand well. Would you like to make a reservation or learn about our restaurant?"
        ]
        
        if self.context["user_name"]:
            return f"{self.context['user_name']}, {random.choice(responses)}"
        else:
            return random.choice(responses)


def main():
    """Main function to run the chatbot"""
    print("\n" + "=" * 50)
    print(f"  Welcome to the {RestaurantInfo.NAME} Chatbot")
    print("=" * 50)
    
    # Check if AI should be used
    use_ai = False
    try:
        response = input("\nDo you want to activate OpenAI integration for more natural responses? (y/n): ").lower()
        if response in ['y', 'yes']:
            api_key = input("Enter your OpenAI API key (leave blank to skip): ").strip()
            if api_key:
                use_ai = True
                print("OpenAI integration activated.")
            else:
                print("No API key provided. Using basic mode.")
        else:
            print("Using basic mode without AI.")
    except Exception:
        print("Error configuring AI. Using basic mode.")
    
    # Start chatbot
    chatbot = RestaurantChatbot(use_ai=use_ai, api_key=api_key if use_ai else None)
    
    print("\nYou can start chatting now. Type 'exit' to end.\n")
    
    # Welcome message
    print("Chatbot:", chatbot.process_message("hello"))
    
    # Main loop
    while True:
        try:
            user_message = input("\nYou: ")
            
            if user_message.lower() in ['exit', 'quit']:
                print("Chatbot:", chatbot._generate_farewell())
                break
            
            response = chatbot.process_message(user_message)
            print("Chatbot:", response)
            
        except KeyboardInterrupt:
            print("\n\nChatbot:", chatbot._generate_farewell())
            break
        except Exception as e:
            print(f"\nError in chatbot: {e}")
            print("Chatbot: I'm sorry, an error occurred. Can you try again?")

