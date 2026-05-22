from transformers import pipeline

print("Initializing Advanced Deep Learning Transformer Core...")
# Load the model once globally when the app boots up so it stays incredibly fast
classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_journal_entry(text: str) -> dict:
    if not text.strip():
        return {"score": 0.0, "mood": "Empty Entry", "tags": [], "highlight": None, "lowlight": None, "prompt": "What's on your mind today, bud?"}

    # 1. Run the entire text block through the Transformer neural network
    prediction = classifier(text)[0]
    label = prediction['label']
    confidence = prediction['score']

    # 2. Math Converter: Convert POSITIVE/NEGATIVE + Confidence into a clean -1.0 to +1.0 scale
    # If NEGATIVE and 99% confident -> score becomes -0.99
    # If POSITIVE and 95% confident -> score becomes +0.95
    if label == "NEGATIVE":
        overall_score = -confidence
    else:
        overall_score = confidence

    overall_score = round(overall_score, 2)

    # 3. Use basic sentence splitting for highlights/lowlights extraction
    # We slice by periods to keep it lightweight without needing textblob anymore
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    highlight = None
    lowlight = None
    
    if len(sentences) > 1:
        # Run each sentence through the transformer to pinpoint exact emotional spikes
        sentence_results = []
        for s in sentences:
            pred = classifier(s)[0]
            s_score = -pred['score'] if pred['label'] == "NEGATIVE" else pred['score']
            sentence_results.append({"text": s, "score": s_score})
        
        sorted_sentences = sorted(sentence_results, key=lambda x: x['score'])
        if sorted_sentences[0]['score'] < -0.5:
            lowlight = sorted_sentences[0]['text']
        if sorted_sentences[-1]['score'] > 0.5:
            highlight = sorted_sentences[-1]['text']

    # 4. Map the score to intelligent coaching prompts based on Transformer accuracy
    if overall_score > 0.4:
        mood = "Positive & Energized"
        prompt = "Your entry radiates great energy! What or who contributed most to this breakthrough moment?"
    elif overall_score < -0.4:
        mood = "Heavy or Overwhelmed"
        prompt = "It sounds like you're navigating a heavy headspace right now. What's one small boundary you can set for your peace today?"
    else:
        mood = "Calm & Neutral"
        prompt = "A beautifully grounded space. What did a steady day allow you to notice about yourself?"

    # Extract clean pseudo-tags from the text (using basic split logic since textblob is removed)
    # This keeps our dependencies purely deep learning focused!
    words = [w.strip(",.?!()\"").lower() for w in text.split() if len(w) > 4]
    unique_tags = list(set(words))[:3]

    return {
        "score": overall_score,
        "mood": mood,
        "tags": unique_tags,
        "highlight": highlight,
        "lowlight": lowlight,
        "prompt": prompt
    }

if __name__ == "__main__":
    # Quick sanity check test
    test_run = "I'm genuinely having an incredibly stressful night with code errors, but hanging out with my pup made it manageable."
    print("\n--- Testing Transformer Core ---")
    print(analyze_journal_entry(test_run))