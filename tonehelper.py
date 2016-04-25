import json
from watson_developer_cloud import ToneAnalyzerV3Beta

class ToneHelper:
    def __init__(self, database):
        self.db = database
        self.bluemix_credentials = json.load(open('bluemix_credentials.json'))
        self.tone_analyzer = ToneAnalyzerV3Beta(
            username=self.bluemix_credentials["username"],
            password=self.bluemix_credentials["password"],
            version="2016-02-11")

    def analyze(self, comment_id):
        # Get comment text
        comment = self.db.get_comment(comment_id)
        if comment is None:
            return
        elif len(comment) < 10:
            return
        #temp = self.tone_analyzer.tone(text=comment)
        # print("temp: {}".format(temp))
        raw_data = self.tone_analyzer.tone(text=comment)
        # raw_data = json.load(open('example.json'))

        tone_keys = ['anger', 'disgust', 'fear', 'joy', 'sadness', 'analytical', 'confident', 'tentative',
                     'openness', 'conscientiousness', 'extraversion', 'agreeeableness', 'neuroticism']

        if 'document_tone' in raw_data:
            # print(raw_data)
            document_tone = raw_data['document_tone']
            if 'tone_categories' in document_tone:
                values = {}
                tone_categories = document_tone['tone_categories']
                for tones in tone_categories:
                    for key in tones:
                        if isinstance(tones[key], list):
                            for tone_val in tones[key]:
                                tone_id = tone_val['tone_id']
                                tone_id = str(tone_id).strip("_big5")
                                score = tone_val['score']
                                values[tone_id] = score
                print("values:\n{}".format(values))
                # Add document tone to database
                self.db.add_document_tone(comment_id, comment, values)

        if 'sentences_tone' in raw_data:
            sentences_tone = raw_data['sentences_tone']
            for sentences in sentences_tone:
                values = {}
                tone_categories = sentences['tone_categories']
                for tones in tone_categories:
                    for key in tones:
                        if isinstance(tones[key], list):
                            for tone_val in tones[key]:
                                tone_id = tone_val['tone_id']
                                tone_id = str(tone_id).strip("_big5")
                                score = tone_val['score']
                                values[tone_id] = score
                raw_text = sentences['text']
                self.db.add_comment_sentence_tone(comment_id, raw_text, values)
                print("values:\n{}".format(values))
                print(raw_text)



