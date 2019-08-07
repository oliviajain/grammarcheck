import sys
import requests
import time
import json
# If you are using a Jupyter notebook, uncomment the following line.
# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from io import BytesIO

from grammarbot import GrammarBotClient
from collections import Counter

def convertToText(image_path, overlayImageWithExtractedText = True):
    # Replace <Subscription Key> with your valid subscription key.
    subscription_key = "TODO: FILL IN SUBSCRIPTION KEY"
    assert subscription_key

    vision_base_url = "https://westus.api.cognitive.microsoft.com/vision/v2.0/"

    text_recognition_url = vision_base_url + "read/core/asyncBatchAnalyze"
    mode = "Handwritten"
    analyze_url = vision_base_url + "recognizeText?mode=" + mode

    # Read the image into a byte array
    image_data = open(image_path, "rb").read()
    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/octet-stream'}
    response = requests.post(
        analyze_url, headers=headers, data=image_data)
    response.raise_for_status()

    output_name = "static/output.jpg"
    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()
        time.sleep(1)
        if ("recognitionResult" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'Failed'):
            poll = False

    if overlayImageWithExtractedText == True:
        polygons = []
        if ("recognitionResult" in analysis):
            # Extract the recognized text, with bounding boxes.
            polygons = [(line["boundingBox"], line["text"])
                        for line in analysis["recognitionResult"]["lines"]]

        #Display the image and overlay it with the extracted text.
        plt.figure(figsize=(15, 15))
        image = Image.open(image_path)
        ax = plt.imshow(image)
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i+1])
                        for i in range(0, len(polygon[0]), 2)]
            text = polygon[1]
            patch = Polygon(vertices, closed=True, fill=False, linewidth=2, color='y')
            ax.axes.add_patch(patch)
            plt.text(vertices[0][0], vertices[0][1], text, fontsize=20, va="top")
        plt.show()
        image.save(output_name)

    # get the text and find grammar counts
    text = json.dumps(analysis, indent=4)
    lines = analysis['recognitionResult']['lines']
    lines_of_text = [lines[i]['text'] for i in range(len(lines))]

    return lines_of_text


def grammarAnalysis(linesOfText):
    client = GrammarBotClient(api_key='TODO: FILL IN API KEY')
    text = ''
    for txt in linesOfText: 
        text += (str(txt) + '/')

    # check the text, returns GrammarBotApiResponse object
    res = client.check(text) 

    # get error counts
    metadata = {}
    error_types = []
    for err in res.matches: 
        start_index = err.replacement_offset 
        end_index = start_index + err.replacement_length
        mistake = text[start_index:end_index]
        # format suggestions
        suggestions = ''
        for sugg in err.replacements:
            suggestions += sugg + ', '
        metadata[mistake] = suggestions[:-2]
        error_types.append(err.category)

    line_numbers = []
    for mistake in metadata.keys(): 
        for i, s in enumerate(linesOfText):
            if mistake in s:
                line_numbers.append(i)

    error_counts = dict(Counter(error_types))
    error_counts_list = [(err, count) for err, count in error_counts.items()]
    total_errors = sum(error_counts.values())

    result_string = json.dumps(res.raw_json, indent=4)

    mistake_info = []
    for i, mistake in enumerate(metadata.keys()):
        mistake_info.append((line_numbers[i], mistake, metadata[mistake]))
    

    flag = (total_errors / len(linesOfText) > 1)
    return total_errors, error_counts_list, mistake_info, flag
    
