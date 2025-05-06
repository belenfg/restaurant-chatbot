# Restaurant Chatbot

A Python-based restaurant chatbot system that can handle reservations, answer common questions, and maintain personalized conversations with customers.

## Key Features

1. **AI Integration**:
   * Supports both OpenAI and Anthropic (Claude) APIs
   * Graceful fallback to rule-based responses when AI is unavailable

2. **Reservation Management**:
   * Extracts date, time, and party size from natural language
   * Validates reservations against restaurant opening hours
   * Manages the reservation conversation flow

3. **Natural Language Understanding**:
   * Intent detection for common restaurant queries
   * Context tracking throughout the conversation
   * Name extraction from user introductions

4. **Restaurant Information**:
   * Menu details
   * Opening hours with today's status
   * Location and contact info

5. **Personalization**:
   * Remembers user names
   * Different responses for returning customers
   * Maintains conversation history for context

## How to Use

1. Set your AI API keys as environment variables:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # or
   export ANTHROPIC_API_KEY="your-key-here"
   ```

2. Run the chatbot from the command line:
   ```bash
   python advanced_gpt_chatbot.py
   ```

3. Interact through the command line interface

## Example Interactions

```
===== The Good Table Restaurant Chatbot =====
Loading AI capabilities...
OpenAI API key found.
OpenAI integration enabled.

Welcome to The Good Table virtual assistant!
Type 'exit' or 'quit' to end the conversation.

Chatbot: Welcome to The Good Table! How can I help you today?

You: Hi, my name is Maria

Chatbot: Hello, Maria! Welcome to The Good Table. How can I assist you today?

You: I'd like to book a table for Saturday

Chatbot: What time would you like to reserve a table on Saturday?

You: Around 8pm for 4 people

Chatbot: Great! I've booked a table for 4 on 2025-05-10 at 20:00 under the name Maria. We look forward to seeing you!

You: What kind of food do you serve?

Chatbot: Here's a brief overview of our menu:

*Starters*: Mediterranean salad, Homemade croquettes, Andalusian gazpacho, Cheese board
*Main Courses*: Valencian paella, Whiskey sirloin steak, Cod confit, Mushroom risotto
*Desserts*: Cheesecake, Chocolate coulant, Homemade tiramisu, Lemon sorbet
*Drinks*: House wines, Craft beers, Soft drinks, Special cocktails

Is there a specific dish you'd like to know more about?

You: goodbye

Chatbot: Thank you for chatting with us! Have a great day!
```

## Requirements

- Python 3.6+
- Optional: OpenAI API key or Anthropic API key for enhanced responses

## Files

- `advanced_gpt_chatbot.py`: Main chatbot implementation with AI integration
- `paste.py`: Core database and restaurant information classes
