from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import nltk
from nltk.chat.util import Chat, reflections
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


# Initialize NLTK
def initialize_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        nltk.download('punkt')


initialize_nltk()

# Chat configuration
pairs = [
    [r'hi|hello|hey', ['Hello!', 'Hi there!', 'How can I help you?']],
    [r'what is your name?', ["I'm your website assistant!", "You can call me ChatBot."]],
    [r'how are you?', ["I'm just a program, but I'm functioning well!", "All systems operational!"]],
    [r'(.*) help (.*)',
     ["I can help with general questions about this website.", "What specifically do you need help with?"]],
    [r'(.*) contact (.*)', ["You can reach us at contact@example.com", "Our support email is support@example.com"]],
    [r'(.*) hours(.*)', ["We're available Monday-Friday, 9am-5pm", "Our operating hours are 9-5 weekdays"]],
    [r'quit|bye|goodbye', ["Goodbye!", "Have a great day!", "Come back soon!"]],
    [r'(.*)', ["I'm not sure I understand. Could you rephrase that?", "I'm still learning. Can you ask differently?"]]
]

chatbot = Chat(pairs, reflections)


@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            user_message = request.POST.get('message', '').lower().strip()
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)

            logger.info(f"Received message: {user_message}")
            response = chatbot.respond(user_message) or "I didn't understand that. Could you rephrase?"

            # Save to database if model exists
            if apps.is_installed('chatbot'):
                try:
                    ChatHistory = apps.get_model('chatbot', 'ChatHistory')
                    ChatHistory.objects.create(
                        user_message=user_message[:1000],
                        bot_response=response[:1000]
                    )
                except Exception as e:
                    logger.error(f"Failed to save chat history: {str(e)}")

            return JsonResponse({'response': response})

        except Exception as e:
            logger.error(f"Error in chat_api: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'response': "Sorry, I encountered an error processing your request"
            }, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def chat_page(request):
    return render(request, 'chat.html')