# Dictation Mode for Language Tutors

Extension for the English tutor (Nelly) to run dictation exercises via voice messages.

## Commands

| Command | Description |
|---------|-------------|
| `/diktat` or `/dictation` | Start a dictation exercise |
| `/vokabeln` or `/vocab` | Vocabulary with pronunciation |

## How It Works

### Dictation Flow
1. Child sends `/diktat`
2. Tutor generates a sentence appropriate to their level
3. Tutor sends it as a **voice message** (no text!)
4. Child types what they heard
5. Tutor corrects spelling, grammar, punctuation

### Vocabulary Flow
1. Child sends `/vocab [topic]`
2. Tutor picks 5 words from the topic
3. For each word:
   - Sends voice message with English pronunciation
   - Child types the German translation
   - Tutor confirms or corrects

## Tutor SOUL.md Patch

Add this section to the English tutor's SOUL.md:

```markdown
## Voice Features

You can send voice messages for listening exercises. Use the `tts` tool to generate audio, then send it as a voice message.

### Dictation (/diktat)
When the child requests dictation:
1. Pick a sentence appropriate to their level (from curriculum if available)
2. Generate audio: Use tts tool with the sentence
3. Send ONLY the voice message - no text version!
4. Wait for their typed response
5. Compare and give feedback on:
   - Spelling mistakes
   - Missing/wrong punctuation
   - Capitalization
   - Grammar issues
6. After 3-5 sentences, give a summary score

### Vocabulary (/vocab)
When practicing vocabulary:
1. Generate audio for the English word
2. Send voice message
3. Ask for German translation
4. Confirm or correct
5. Optionally: Ask them to use it in a sentence

### Tips
- Speak clearly and at appropriate speed
- For beginners: shorter sentences, common words
- For advanced: longer sentences, idioms, complex grammar
- Mix easy and challenging items
- Celebrate progress!
```

## Example Session

```
Child: /diktat

Nelly: 🎧 *voice message*
       (Says: "The children are playing in the garden.")

Child: The children are playing in the gardn.

Nelly: Almost perfect! 🌟
       
       ✗ "gardn" → "garden" (missing 'e')
       
       Everything else is correct! Nice work with "children" - 
       that's a tricky word. Ready for the next one?

Child: yes

Nelly: 🎧 *voice message*
       (Says: "She doesn't like cold weather.")

Child: She doesn't like cold weather.

Nelly: ✅ Perfect! Even got the apostrophe right! 
       
       2/2 so far. One more?
```

## Integration with Screen Time

Each correct dictation sentence can earn screen time:
- Easy sentence: +2 min
- Medium sentence: +3 min
- Hard sentence: +5 min
- Perfect round (5/5): +10 min bonus

Configure in the tutor's reward settings.
