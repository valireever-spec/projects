const SOURCE_CREDIBILITY = {
  // Tier 1: Official institutions (highest)
  official_eu: { tier: 1, score: 10, label: "Official EU Document" },
  court_record: { tier: 1, score: 10, label: "Court Record" },
  government: { tier: 1, score: 10, label: "Government Official" },

  // Tier 2: International bodies
  un_report: { tier: 2, score: 9, label: "UN Report" },
  nato_report: { tier: 2, score: 9, label: "NATO Report" },
  council_europe: { tier: 2, score: 9, label: "Council of Europe" },

  // Tier 3: NGOs and watchdogs
  amnesty: { tier: 3, score: 8, label: "Amnesty International" },
  hrw: { tier: 3, score: 8, label: "Human Rights Watch" },
  transparency_org: { tier: 3, score: 8, label: "Transparency Organization" },

  // Tier 4: Statistics and research
  statistics_office: { tier: 4, score: 7, label: "National Statistics Office" },
  research_peer_reviewed: { tier: 4, score: 7, label: "Peer-Reviewed Research" },

  // Tier 5: Named officials
  named_official: { tier: 5, score: 6, label: "Named Official on Record" },

  // Rejected
  anonymous: { tier: 0, score: 0, label: "Anonymous Account" },
  social_media: { tier: 0, score: 0, label: "Social Media (unverified)" },
  unnamed_source: { tier: 0, score: 0, label: "Unnamed Source" },
};

const RUSSIA_FLAG_KEYWORDS = [
  "russia", "ukraine", "belarus", "nato", "election interference",
  "disinformation", "hybrid war", "energy dependency", "wagner",
  "kremlin", "fsb", "svr", "gia", "putin", "kremlin",
];

export function detectRussiaFlag(text) {
  const lower = text.toLowerCase();
  return RUSSIA_FLAG_KEYWORDS.some(keyword => lower.includes(keyword));
}

export function classifySource(sourceInfo) {
  const { name, type, url, description } = sourceInfo;
  const lower = name.toLowerCase();

  // Official EU/Government
  if (lower.includes("eu ") || lower.includes("european commission") ||
      lower.includes("court of justice") || lower.includes("ecb")) {
    return SOURCE_CREDIBILITY.official_eu;
  }

  if (lower.includes("government") || lower.includes("ministry") ||
      lower.includes("parliament") || lower.includes("court")) {
    return SOURCE_CREDIBILITY.government;
  }

  // International
  if (lower.includes("united nations") || lower.includes("un report")) {
    return SOURCE_CREDIBILITY.un_report;
  }
  if (lower.includes("nato")) {
    return SOURCE_CREDIBILITY.nato_report;
  }
  if (lower.includes("council of europe")) {
    return SOURCE_CREDIBILITY.council_europe;
  }

  // NGOs
  if (lower.includes("amnesty")) {
    return SOURCE_CREDIBILITY.amnesty;
  }
  if (lower.includes("human rights watch")) {
    return SOURCE_CREDIBILITY.hrw;
  }
  if (lower.includes("transparency")) {
    return SOURCE_CREDIBILITY.transparency_org;
  }

  // Statistics
  if (lower.includes("statistics") || lower.includes("statista") ||
      lower.includes("eurostat")) {
    return SOURCE_CREDIBILITY.statistics_office;
  }

  // Research
  if (lower.includes("research") || lower.includes("journal") ||
      lower.includes("peer-reviewed") || lower.includes("study")) {
    return SOURCE_CREDIBILITY.research_peer_reviewed;
  }

  // Rejected patterns
  if (lower.includes("anonymous") || lower.includes("unnamed")) {
    return SOURCE_CREDIBILITY.unnamed_source;
  }
  if (lower.includes("twitter") || lower.includes("facebook") ||
      lower.includes("instagram") || lower.includes("tiktok")) {
    return SOURCE_CREDIBILITY.social_media;
  }

  // Default to named official if we can't classify
  return SOURCE_CREDIBILITY.named_official;
}

export function scoreVerification(sources, hasRussiaFlag) {
  const validSources = sources.filter(s => s.credibility && s.credibility.score > 0);

  if (hasRussiaFlag) {
    // Enhanced rules: 3+ sources, 2+ institutional
    const institutionalSources = validSources.filter(s => s.credibility.tier <= 2);

    if (validSources.length >= 3 && institutionalSources.length >= 2) {
      return {
        status: "verified",
        requiresHold: true,
        message: "Verified with enhanced rules (Russia flag). 24-hour hold required.",
      };
    } else if (validSources.length >= 2) {
      return {
        status: "partial",
        requiresHold: false,
        message: `Needs institutional backing for Russia-related stories. Found ${institutionalSources.length}/${2} institutional sources needed.`,
      };
    }
    return {
      status: "unverified",
      requiresHold: false,
      message: "Russia-related stories require 3+ sources with 2+ institutional backing.",
    };
  }

  // Standard verification: 2+ independent sources
  if (validSources.length >= 2) {
    return {
      status: "verified",
      requiresHold: false,
      message: "Verified with 2+ independent sources.",
    };
  } else if (validSources.length === 1) {
    return {
      status: "partial",
      requiresHold: false,
      message: "Found 1 source. Needs verification from second independent source.",
    };
  }

  return {
    status: "unverified",
    requiresHold: false,
    message: "No legitimate sources found. Cannot publish.",
  };
}
