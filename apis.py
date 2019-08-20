import sys
import requests
import time
import json
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from matplotlib.patches import Polygon
from grammarbot import GrammarBotClient
from collections import Counter

def convert_to_text(image_path, overlay_image = True):

    subscription_key = "TODO: FILL IN SUBSCRIPTION KEY"
    assert subscription_key

    mode = "Handwritten"
    vision_base_url = "https://westus.api.cognitive.microsoft.com/vision/v2.0/"
    text_recognition_url = vision_base_url + "read/core/asyncBatchAnalyze"
    analyze_url = vision_base_url + "recognizeText?mode=" + mode

    # Read the image into a byte array
    image_data = open(image_path, "rb").read()
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream'
    }
    response = requests.post(
        analyze_url, 
        headers=headers, 
        data=image_data)
    response.raise_for_status()

    output_name = "static/output.jpg"
    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], 
            headers=headers)
        analysis = response_final.json()
        time.sleep(1)
        if ("recognitionResult" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'Failed'):
            poll = False

    if overlay_image == True:
        polygons = []
        if ("recognitionResult" in analysis):
            # Extract the recognized text, with bounding boxes.
            polygons = [(line["boundingBox"], line["text"])
                        for line in analysis["recognitionResult"]["lines"]]

        # Display the image and overlay it with the extracted text.
        plt.figure(figsize=(15, 15))
        image = Image.open(image_path)
        ax = plt.imshow(image)
        
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i+1])
                        for i in range(0, len(polygon[0]), 2)]
            text = polygon[1]
            
            patch = Polygon(
                        vertices, 
                        closed=True, 
                        fill=False, 
                        linewidth=2, 
                        color='y')
            ax.axes.add_patch(patch)
            
            plt.text(
                vertices[0][0], 
                vertices[0][1], 
                text, 
                fontsize=20, 
                va="top")
        
        plt.show()
        image.save(output_name)

    # get the text and find grammar counts
    text = json.dumps(analysis, indent=4)
    lines = analysis['recognitionResult']['lines']
    lines_of_text = [lines[i]['text'] for i in range(len(lines))]

    return lines_of_text


def grammar_analysis(lines_of_text):
    client = GrammarBotClient(api_key='TODO: FILL IN API KEY')
    all_text = ''
    for txt in lines_of_text: 
        all_text += (str(txt) + '/')

    # check the text, returns GrammarBotApiResponse object
    errors = client.check(text) 

    # get error counts
    metadata = {}
    error_types = []
    for err in errors.matches: 
        start = err.replacement_offset 
        end = start + err.replacement_length
        mistake = allText[start:end]
        
        # format suggestions
        suggestions = ''
        for suggestion in err.replacements:
            suggestions += suggestion + ', '
        metadata[mistake] = suggestions[:-2] # take off last comma
        error_types.append(err.category)

    # get line numbers for help
    line_numbers = []
    for mistake in metadata.keys(): 
        for i, s in enumerate(linesOfText):
            if mistake in s:
                line_numbers.append(i)


    type_counts = dict(Counter(errorTypes))
    type_counts_list = type_counts.items()
    total_errors = sum(types_counts.values())

    result_string = json.dumps(res.raw_json, indent=4)

    mistake_info = []
    for i, mistake in enumerate(metadata.keys()):
        mistake_info.append((
            line_numbers[i], 
            mistake, 
            metadata[mistake]))
    
    flag = (total_errors / len(lines_of_text) > 1)
    return total_errors, type_counts_list, mistake_info, flag
    
