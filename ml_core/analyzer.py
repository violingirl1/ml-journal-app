from transformers import pipeline

print("Initializing Customized Hybrid Multi-Emotion Transformer Core...")
# Load the 6-emotion model
emotion_classifier = pipeline("sentiment-analysis", model="bhadresh-savani/distilbert-base-uncased-emotion")

def apply_custom_rules(text: str, emotions_map: dict, dominant_emotion: str) -> tuple:
    """
    Intercepts the text to check for personalized emojis, student slang, 
    and developer context, modifying the emotion mapping accordingly.
    """
    text_lower = text.lower()
    custom_prompt = None
    
    # 1. Developer & Tech Student Context Rules
    dev_stress_keywords = ['internals', 'lab program', 'exam', 'dbms', 'java', 'linear algebra', 'bug', 'error', 'crash']
    if any(keyword in text_lower for keyword in dev_stress_keywords):
        # Academic stress primarily triggers anxiety/vulnerability (Fear) and friction (Anger)
        emotions_map['fear'] = min(100.0, emotions_map.get('fear', 0) + 35.0)
        emotions_map['anger'] = min(100.0, emotions_map.get('anger', 0) + 15.0)
        # Re-evaluate dominant emotion if fear spikes high
        if emotions_map['fear'] > emotions_map.get(dominant_emotion, 0):
            dominant_emotion = 'fear'
        custom_prompt = "Exam and coding cycles can be an absolute mountain to climb, bud. Remember to step away from the screen, give your pup a high-five, and take a deep breath. You've got this!"

    dev_success_keywords = ['mern', 'clone', 'project', 'github', 'push', 'fixed', 'leetcode', 'violin']
    if any(keyword in text_lower for keyword in dev_success_keywords):
        # Wins boost alignment (Joy) and surprise/shifts (Surprise)
        emotions_map['joy'] = min(100.0, emotions_map.get('joy', 0) + 40.0)
        if emotions_map['joy'] > emotions_map.get(dominant_emotion, 0):
            dominant_emotion = 'joy'
        custom_prompt = "Let's gooo! Seeing the code compile or locking down a solid practice run is unmatched. Take a second to appreciate your hard work today, bud! 🚀"

    # 2. Modern Slang & Emoji Conversions
    # Checking for the generation's signature "I'm dead" laugh/stress indicator
    if '💀' in text or 'dead' in text_lower:
        emotions_map['surprise'] = min(100.0, emotions_map.get('surprise', 0) + 20.0)
        
    if '🚀' in text or 'slaying' in text_lower or 'lessgo' in text_lower:
        emotions_map['joy'] = min(100.0, emotions_map.get('joy', 0) + 30.0)
        if emotions_map['joy'] > emotions_map.get(dominant_emotion, 0):
            dominant_emotion = 'joy'

    # Normalize map back to a total percentage threshold if anything overshot 100
    total = sum(emotions_map.values())
    if total > 0:
        for key in emotions_map:
            emotions_map[key] = round((emotions_map[key] / total) * 100, 1)

    return emotions_map, dominant_emotion, custom_prompt

def analyze_journal_entry(text: str) -> dict:
    if not text.strip():
        return {
            "score": 0.0, "mood": "Empty Entry", "tags": [], 
            "prompt": "What's on your mind today, bud?", "emotions": {}
        }

    # 1. Run text through the base neural network
    predictions = emotion_classifier(text)
    
    emotions_map = {"joy": 0.0, "sadness": 0.0, "anger": 0.0, "fear": 0.0, "love": 0.0, "surprise": 0.0}
    dominant_emotion = "joy"
    highest_score = -1

    if isinstance(predictions, list):
        target_list = predictions[0] if isinstance(predictions[0], list) else predictions
    else:
        target_list = [predictions]

    for pred in target_list:
        if isinstance(pred, dict) and 'label' in pred:
            emotion_name = pred['label'].lower()
            percentage = round(pred['score'] * 100, 1)
            emotions_map[emotion_name] = percentage
            
            if pred['score'] > highest_score:
                highest_score = pred['score']
                dominant_emotion = emotion_name

    # 2. 🌟 HYBRID LAYER INTERCEPTION: Apply our custom rule weights!
    emotions_map, dominant_emotion, tailored_prompt = apply_custom_rules(text, emotions_map, dominant_emotion)

    # 3. Create composite score for our Line Chart (-1 to +1)
    positives = emotions_map.get('joy', 0) + emotions_map.get('love', 0) + emotions_map.get('surprise', 0)
    negatives = emotions_map.get('sadness', 0) + emotions_map.get('anger', 0) + emotions_map.get('fear', 0)
    total_spread = positives + negatives
    legacy_score = round((positives - negatives) / (total_spread if total_spread > 0 else 100), 2)

    # 4. Standard Prompts Fallback (if no custom rule prompt was assigned)
    if not tailored_prompt:
        prompts = {
            "joy": "Your space is glowing with joy! What's a small way you can anchor this feeling or share it with someone you care about?",
            "sadness": "I can feel the heavy heart in your words today, bud. Be incredibly gentle with yourself right now.",
            "anger": "There is a lot of valid friction or fire in this entry. Where do you feel this tension holding in your body?",
            "fear": "It sounds like anxiety or uncertainty is taking the driver's seat right now. What is one small thing within your control?",
            "love": "Such a beautiful, warm reflection. Who or what is making you feel this deeply connected today?",
            "surprise": "Wow, an unexpected twist! How are you adjusting to this sudden shift or realization?"
        }
        coaching_prompt = prompts.get(dominant_emotion, "A steady space for reflection. What did today teach you?")
    else:
        coaching_prompt = tailored_prompt

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
    # Test our hybrid context engine
    test_run = "Internals are driving me crazy, trying to get my advanced java lab program working 💀"
    print("\n--- Testing Hybrid Rule Engine ---")
    print(analyze_journal_entry(test_run))