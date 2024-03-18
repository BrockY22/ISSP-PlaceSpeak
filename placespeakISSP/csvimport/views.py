# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from io import StringIO
import requests
import csv
import re
import json

def remove_non_printable_chars(text):
    # Define the pattern to match only printable characters
    printable_pattern = re.compile(r'[^\x20-\x7E]')
    # Substitute non-printable characters with an empty string
    clean_text = re.sub(printable_pattern, '', text)
    return clean_text

@csrf_exempt  # Temporarily disable CSRF for this view to simplify the example
def send_csv_to_api(request):
    standard_query = """"Generate the result in csv format without any explaination. Do not include a header for the data. For each response,
                    column 1:Report id
                    column 2:Give me phrases to summarize the response
                    column 3:Generate a sentimental analysis of the response from positive, neutral, or negative
                    column 4:Generate a confidence score in a percentage
                    column 5:Determine the reaction/emotion
                    column 6:Generate a narrative summary of the all the data and responses
                    Format the data as: ID, Key Words, Sentiment, Confidence Score, Reaction/Emotion, Summary
                    """
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']
        csv_data = remove_non_printable_chars(csv_file.read().decode('utf-8-sig'))
        #print("Size of csv_data in characters:", len(csv_file))
        # Combine CSV data with the standard query
        combined_data = "{}\n{}".format(standard_query, csv_data)

        # Prepare data to send to the OpenAI API
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": "Bearer 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",  # Replace with your actual API key
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_data}
            ],
            "max_tokens": 4096,
        }

        # Send the request to the OpenAI API
        response = requests.post(api_url, headers=headers, json=data)
    

        if response.status_code == 200:
            response_data = response.json()
        
            result = response_data.get("choices")[0].get("message").get("content")
            entries = []
            for line in csv.reader(StringIO(result.strip())):
                # Create a dictionary for each line and append to entries
                entry = {
                    'ID': line[0].strip(),
                    'KeyPhrases': line[1].strip(),
                    'Sentiment': line[2].strip(),
                    'ConfidenceScore': line[3].strip(),
                    'ReactionEmotion': line[4].strip(),
                    'Summary': line[5].strip(),
                }  
                entries.append(entry)
            request.session['api_response'] = entries
            return redirect('home')
        else:
            return JsonResponse({'error': response.text}, status=response.status_code)

    return JsonResponse({'error': 'Invalid request'}, status=400)
    
def download_data(request):
    # Create the HttpResponse object with the appropriate CSV header.
    print("Download data view was called")
    response = HttpResponse(content_type='text/csv  ; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_data_{}.csv"'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
   # response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID','KeyPhrases', 'Sentiment', 'ConfidenceScore', 'ReactionEmotion', 'Summary'])

    entries = request.session.get('api_response',None)
    if entries:  # Check if entries is not None or empty
        for entry in entries:
            writer.writerow([
                entry.get('ID', ''),
                entry.get('KeyPhrases', ''),
                entry.get('Sentiment', ''),
                entry.get('ConfidenceScore', ''),
                entry.get('ReactionEmotion', ''),
                entry.get('Summary', '')
            ])
        del request.session['api_response']
    else:
        # Handle the case where there are no entries, perhaps write a row that indicates no data
        writer.writerow(['No data available.'])
    
    return response

def home(request):
    # Fetch actual data from the API or other sources here
    api_response = request.session.get('api_response', None)
    # print(api_response)
    if api_response:
        entries = api_response
        # Convert the string response to JSON
        #del request.session['api_response']
    else:
        entries = None
    return render(request, 'report.html', {'entries': entries})