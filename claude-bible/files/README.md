# Selah Bible Write-Up Generator

Generates rich, pastoral study write-ups for every verse of the Bible
using the Claude API. Each write-up includes a headline, word study,
historical context, meaning, application, cross-reference, and prayer prompt.

## Output Example

```json
{
  "reference": "John 15:5",
  "book": "John",
  "chapter": 15,
  "verse": 5,
  "text": "I am the vine, you are the branches...",
  "genre": "gospel",
  "headline": "Apart from Jesus, spiritual fruit is impossible",
  "word_study": "The Greek 'menō' (remain/abide) appears 11 times in John 15 alone...",
  "context": "Jesus speaks these words the night before his crucifixion...",
  "meaning": "Jesus is claiming to be the true source of all spiritual life...",
  "application": "Before striving to be more patient or loving, ask first...",
  "connection": "Galatians 5:22-23 lists the fruit of the Spirit — qualities...",
  "prayer_prompt": "Lord, help me stay connected to you today instead of straining alone."
}
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get a key at: https://console.anthropic.com

---

## Usage

### Generate one book (recommended starting point)

```bash
python generate.py --book John
```

### Generate specific chapters

```bash
python generate.py --book John --start 14 --end 17
```

### Generate the entire Bible

```bash
python generate.py --all
```

### List all available books

```bash
python generate.py --list-books
```

---

## Output Structure

Results are saved to the `output/` directory, one JSON file per book:

```
output/
  john.json
  genesis.json
  psalms.json
  ...
```

Each file is an array of verse objects, sorted by chapter and verse.

### Resuming

If the script is interrupted, it automatically resumes from where it left off.
Already-generated verses are never re-processed.

---

## Cost Estimate

| Scope | Verses | Est. Cost |
|---|---|---|
| One book (John) | 879 | ~$1–2 |
| New Testament | 7,959 | ~$10–15 |
| Entire Bible | 31,102 | ~$50–100 |

Costs vary based on verse length and output length.

---

## Speed

With `MAX_WORKERS = 5` (default), expect roughly:
- ~100 verses per minute
- John (879 verses): ~9 minutes
- Entire Bible: ~5–6 hours

You can increase `MAX_WORKERS` up to 10 if your API tier allows higher rate limits.

---

## Recommended Starting Workflow

1. Start with John — it's the most relevant for the Abide series
2. Review ~20 outputs across different chapters
3. Tune the prompt in `generate.py` if needed
4. Run Psalms next (poetry genre, very different style)
5. Then run the full New Testament
6. Finally the Old Testament

---

## Tuning the Prompt

The prompt is in `generate.py` in the `build_prompt()` function.
The system prompt is in `SYSTEM_PROMPT`.

Tips for tuning:
- Adjust the tone instruction in `SYSTEM_PROMPT`
- Change word counts in the prompt for longer/shorter outputs
- Modify the JSON fields to add/remove sections
- Adjust `GENRE_INSTRUCTIONS` per genre for different emphasis

---

## Integrating into Selah

Each verse write-up is keyed by `book + chapter + verse`.
Import the JSON files into your database (Supabase, Firebase, etc.)
and query by reference when a user opens a verse for study.

Suggested database schema:
```sql
CREATE TABLE verse_writeups (
  id SERIAL PRIMARY KEY,
  book TEXT NOT NULL,
  chapter INT NOT NULL,
  verse INT NOT NULL,
  text TEXT,
  genre TEXT,
  headline TEXT,
  word_study TEXT,
  context TEXT,
  meaning TEXT,
  application TEXT,
  connection TEXT,
  prayer_prompt TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(book, chapter, verse)
);
```
