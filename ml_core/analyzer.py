from textblob import TextBlob

def analyze_journal_entry(text: str) -> dict:
    if not text.strip():
        return {"score": 0.0, "mood": "Empty Entry", "tags": [], "highlights": [], "prompt": "What's on your mind today, bud?"}

    blob = TextBlob(text)
    overall_polarity = blob.sentiment.polarity
    
    # 1. Advanced Processing: Analyze sentence-by-sentence to capture spikes in emotion
    sentence_data = []
    for sentence in blob.sentences:
        score = sentence.sentiment.polarity
        sentence_data.append({
            "text": str(sentence),
            "score": round(score, 2)
        })
    
    # Extract the ultimate high point and low point of the entry
    sorted_sentences = sorted(sentence_data, key=lambda x: x['score'])
    lowlight = sorted_sentences[0]['text'] if sorted_sentences and sorted_sentences[0]['score'] < -0.2 else None
    highlight = sorted_sentences[-1]['text'] if sorted_sentences and sorted_sentences[-1]['score'] > 0.2 else None

    # 2. Map vibe to human emotional contexts
    if overall_polarity > 0.4:
        mood = "Positive & Energized"
        prompt = "That sounds amazing! What or who contributed most to this great feeling?"
    elif overall_polarity < -0.3:
        mood = "Overwhelmed or Anxious"
        prompt = "It sounds like you are carrying a lot right now. What is one small thing within your control that you can let go of today?"
    elif -0.3 <= overall_polarity <= 0.4:
        # Check if there was internal emotional volatility hidden by the average
        if len(sorted_sentences) > 1 and (sorted_sentences[-1]['score'] - sorted_sentences[0]['score']) > 0.8:
            mood = "Emotionally Mixed / Conflicted"
            prompt = "You've got some contrasting emotions here. What do you think is causing this inner tug-of-war?"
        else:
            mood = "Calm & Grounded"
            prompt = "A beautifully steady day. What did a peaceful day allow you to notice about your environment?"
    
    # 3. Dynamic Tagging
    extracted_tags = list(set(blob.noun_phrases))
    
    return {
        "score": round(overall_polarity, 2),
        "mood": mood,
        "tags": extracted_tags[:5],
        "highlight": highlight,
        "lowlight": lowlight,
        "prompt": prompt
    }

if __name__ == "__main__":
    # Test our new Reflection-style multi-sentence logic
    test = "Today started out completely miserable because my code kept crashing. I felt so incompetent. But later, I fixed the bug and went for a beautiful walk outside. Now I feel incredibly proud!"
    print(analyze_journal_entry(test))