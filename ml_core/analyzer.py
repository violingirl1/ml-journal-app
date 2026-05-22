from transformers import pipeline

print("Initializing Advanced Multi-Emotion Transformer Core...")
# Loading the highly accurate 6-emotion classification model
emotion_classifier = pipeline("sentiment-analysis", model="bhadresh-savani/distilbert-base-uncased-emotion")

def analyze_journal_entry(text: str) -> dict:
    if not text.strip():
        return {
            "score": 0.0, "mood": "Empty Entry", "tags": [], 
            "prompt": "What's on your mind today, bud?", "emotions": {}
        }

    # 1. Run text through the Multi-Emotion Neural Network
    predictions = emotion_classifier(text)
    
    # Base structure for all 6 emotions initialized to 0%
    emotions_map = {"joy": 0.0, "sadness": 0.0, "anger": 0.0, "fear": 0.0, "love": 0.0, "surprise": 0.0}
    dominant_emotion = "joy"
    highest_score = -1

    # 2. Robust Parsing: Handle list of lists, list of dicts, or single dict
    if isinstance(predictions, list):
        if isinstance(predictions[0], list):
            # It's a nested list [[{...}, {...}]]
            target_list = predictions[0]
        else:
            # It's a single list [{...}, {...}]
            target_list = predictions
    else:
        # It's a single raw dictionary
        target_list = [predictions]

    # Populate our map with the percentages
    for pred in target_list:
        if isinstance(pred, dict) and 'label' in pred:
            emotion_name = pred['label'].lower()
            percentage = round(pred['score'] * 100, 1)
            emotions_map[emotion_name] = percentage
            
            if pred['score'] > highest_score:
                highest_score = pred['score']
                dominant_emotion = emotion_name

    # 3. Create a pseudo-sentiment score (-1 to +1) for our line graph
    positives = emotions_map.get('joy', 0) + emotions_map.get('love', 0) + emotions_map.get('surprise', 0)
    negatives = emotions_map.get('sadness', 0) + emotions_map.get('anger', 0) + emotions_map.get('fear', 0)
    
    # Prevent divide by zero if map elements are empty
    total_spread = positives + negatives
    legacy_score = round((positives - negatives) / (total_spread if total_spread > 0 else 100), 2)

    # 4. Craft targeted, high-empathy coaching prompts
    prompts = {
        "joy": "Your space is glowing with joy! What's a small way you can anchor this feeling or share it with someone you care about?",
        "sadness": "I can feel the heavy heart in your words today, bud. Be incredibly gentle with yourself right now. What does comfort look like for you tonight?",
        "anger": "There is a lot of valid frustration or fire in this entry. Where do you feel this tension holding in your body, and how can you let it safely vent?",
        "fear": "It sounds like anxiety or uncertainty is taking the driver's seat right now. Let's ground ourselves: what is one true thing about your present moment that is safe?",
        "love": "Such a beautiful, warm reflection. Who or what is making you feel this deeply connected today?",
        "surprise": "Wow, an unexpected twist! How are you adjusting to this sudden shift or realization?"
    }
    
    coaching_prompt = prompts.get(dominant_emotion, "A steady space for reflection. What did today teach you about your inner world?")

    # Extract clean pseudo-tags
    words = [w.strip(",.?!()\"").lower() for w in text.split() if len(w) > 4]
    unique_tags = list(set(words))[:3]

    return {
        "score": legacy_score,
        "mood": dominant_emotion.capitalize(),
        "tags": unique_tags,
        "prompt": coaching_prompt,
        "emotions": emotions_map
    }

if __name__ == "__main__":
    test_text = "I am super anxious about my upcoming presentation, what if I completely lock up and ruin everything?!"
    print("\n--- Testing Multi-Emotion Core ---")
    print(analyze_journal_entry(test_text))