# Press Coverage Analyzer

The second component in The Ignored Signal's intelligence layer. Scans major European news outlets per language and identifies underreported stories based on importance vs. coverage gap.

## What it does

Takes a language and optional category, then:
1. Searches major outlets per language using Claude web search
2. Scores each story for **importance** (affects millions?) and **coverage** (was it widely reported?)
3. Calculates **gap** = importance - coverage (higher gap = more overlooked)
4. Returns 8-12 story candidates ranked by gap score

## Outlets Scanned

### 🇬🇧 English
- BBC, The Guardian, Reuters, Politico Europe, The Times

### 🇫🇷 French
- Le Monde, Le Figaro, Libération, Mediapart, AFP

### 🇩🇪 German
- Der Spiegel, Frankfurter Allgemeine, Süddeutsche Zeitung, Die Zeit, DPA

### 🇮🇹 Italian
- La Repubblica, Corriere della Sera, ANSA, Il Fatto Quotidiano

### 🇷🇴 Romanian
- Digi24, ProTV, G4Media, HotNews, Euractiv Romania

## Scoring System

### Importance Score (1-10)
Measures impact on ordinary Europeans:
- **10** = Affects millions, life-changing consequences
- **8-9** = Major consequence for significant population
- **5-7** = Notable impact, affects tens of thousands
- **1-4** = Minor impact or regional only

### Coverage Score (1-10)
Measures how much mainstream media covered it:
- **10** = Wall-to-wall coverage, headline everywhere
- **8-9** = Major headlines for multiple days
- **5-7** = Mentioned across outlets, secondary story
- **1-4** = Barely covered, disappeared quickly

### Gap Score = Importance - Coverage
The **gap** shows how overlooked a story is:
- **Gap 8-10** = ⚠️ **CRITICAL**: Important but almost nobody reported it
- **Gap 5-7** = **HIGH**: Deserves way more attention
- **Gap 1-4** = Story was appropriately covered

## Categories Supported

- EU Legislation & Policy
- Economic Stories
- Environmental Findings
- Scientific Research
- Historical Context
- Human Interest
- Hybrid War — Russia
- Human Rights Violations
- Corruption

## Output Format

```javascript
{
  language: "en",
  category: "eu_policy",
  stories: [
    {
      headline: "EU quietly passes contentious data law",
      summary: "European Commission amended privacy regulations affecting 450M people...",
      importanceScore: 9,
      coverageScore: 3,
      gapScore: 6,
      sources: ["Politico Europe", "The Guardian"],
      category: "EU Legislation & Policy",
      language: "en"
    },
    // ... more stories sorted by gapScore (highest first)
  ]
}
```

## Integration Flow

1. **Press Analyzer finds stories** → returns list with gap scores
2. **User selects interesting story** → passes to **Verification Engine**
3. **Verification Engine** → verifies sources and credibility
4. **If verified** → passes to **Script Generator** for narration
5. **Script Generator** → creates friend-tone script
6. **Visibility Advisor** → scores for algorithm fit
7. **Content Calendar** → plan publication across languages/platforms
8. **Export** → production-ready script with timestamps

## Usage Notes

- **Cold start**: Select language (English recommended), then "Analyze Coverage"
- **Category filter**: Optional — leave blank to scan all topics or filter by specific category
- **Time intensive**: API calls can take 60-120 seconds depending on outlet complexity
- **Results sorted**: Always sorted by gap score (highest = most overlooked)

## Next Component: Viral Content Scanner

Completes intelligence layer by identifying:
- High-engagement posts from Reddit (r/europe, r/worldnews, country subreddits)
- Trending topics from 9gag
- Community signals that haven't hit mainstream yet
- Feeds into Verification Engine for credibility check

Combined with Verification Engine + Press Analyzer, this triple pipeline ensures:
- **Mainstream sources** (Press Analyzer)
- **Community signals** (Viral Scanner)
- **All verified** (Verification Engine)
- **Before any go to production** (Script Generator)
