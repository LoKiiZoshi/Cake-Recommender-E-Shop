from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot import ask_general_chatbot
import time


@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        question = request.POST.get('message','').strip()
        if not question:
            return StreamingHttpResponse("Please ask question.")
        
        def generate_stream():
            try:
                answer = ask_general_chatbot(question)
                words = answer.split() # send word by word
                for word in words:
                 yield words+""
                time.sleep(0.07)# typing delay
            except Exception as e:
                yield f"Error: {str(e)}"
                
        return StreamingHttpResponse(generate_stream(), content_type = "text/plain")
    return render(request, 'chatbot.html')