from textblob import TextBlob

def analyze_journal_entry(text: str) -> dict:
    """
    Takes a raw journal entry string and uses NLP to calculate 
    the mood score and extract key topic tags.
    """
    # 1. Feed the text into TextBlob to create a smart NLP object
    blob = TextBlob(text)
    
    # 2. Calculate Sentiment Polarity
    # This is a floating-point number ranging from -1.0 to +1.0.
    # -1.0 is extremely negative, 0.0 is dead neutral, and +1.0 is highly positive.
    polarity = blob.sentiment.polarity
    
    # 3. Translate that math score into a human-readable mood string
    if polarity > 0.3:
        mood = "Positive & Bright"
    elif polarity < -0.3:
        mood = "Heavy or Stressed"
    elif -0.3 <= polarity <= 0.3 and text.strip() != "":
        mood = "Calm & Neutral"
    else:
        mood = "Empty Entry"
        
    # 4. Extract "Noun Phrases" to act as tags (what the user is writing about)
    # TextBlob automatically parses the sentence grammar to find core subjects.
    extracted_tags = list(blob.noun_phrases)
    
    # Remove any duplicate tags by converting to a set, then back to a clean list
    unique_tags = list(set(extracted_tags))
    
    # Pack everything into a neat dictionary package to send to our frontend later
    return {
        "score": round(polarity, 2),
        "mood": mood,
        "tags": unique_tags[:5]  # Limit to top 5 tags so the UI stays clean
    }

# --- LOCAL QUICK TEST ---
# This block only runs when you execute this file directly in your terminal.
if __name__ == "__main__":
    sample_text = "Had a rough morning and a huge headache, but then I spent time playing with my puppy and it made me feel so much better. I love relaxing days."
    print("\n--- Testing our ML Logic ---")
    results = analyze_journal_entry(sample_text)
    print(results)
    print("----------------------------\n")