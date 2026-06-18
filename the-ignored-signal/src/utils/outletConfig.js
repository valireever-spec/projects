export const OUTLETS_BY_LANGUAGE = {
  en: {
    name: 'English',
    flag: '🇬🇧',
    outlets: [
      { name: 'BBC', url: 'bbc.com', focus: 'News' },
      { name: 'The Guardian', url: 'theguardian.com', focus: 'News' },
      { name: 'Reuters', url: 'reuters.com', focus: 'News' },
      { name: 'Politico Europe', url: 'politico.eu', focus: 'EU Policy' },
      { name: 'The Times', url: 'thetimes.co.uk', focus: 'News' },
    ],
  },
  fr: {
    name: 'French',
    flag: '🇫🇷',
    outlets: [
      { name: 'Le Monde', url: 'lemonde.fr', focus: 'News' },
      { name: 'Le Figaro', url: 'lefigaro.fr', focus: 'News' },
      { name: 'Libération', url: 'liberation.fr', focus: 'News' },
      { name: 'Mediapart', url: 'mediapart.fr', focus: 'Investigation' },
      { name: 'AFP', url: 'afp.com', focus: 'News' },
    ],
  },
  de: {
    name: 'German',
    flag: '🇩🇪',
    outlets: [
      { name: 'Der Spiegel', url: 'spiegel.de', focus: 'News' },
      { name: 'Frankfurter Allgemeine', url: 'faz.net', focus: 'News' },
      { name: 'Süddeutsche Zeitung', url: 'sueddeutsche.de', focus: 'News' },
      { name: 'Die Zeit', url: 'zeit.de', focus: 'Analysis' },
      { name: 'DPA', url: 'dpa.de', focus: 'News' },
    ],
  },
  it: {
    name: 'Italian',
    flag: '🇮🇹',
    outlets: [
      { name: 'La Repubblica', url: 'repubblica.it', focus: 'News' },
      { name: 'Corriere della Sera', url: 'corriere.it', focus: 'News' },
      { name: 'ANSA', url: 'ansa.it', focus: 'News' },
      { name: 'Il Fatto Quotidiano', url: 'ilfattoquotidiano.it', focus: 'Investigation' },
    ],
  },
  ro: {
    name: 'Romanian',
    flag: '🇷🇴',
    outlets: [
      { name: 'Digi24', url: 'digi24.ro', focus: 'News' },
      { name: 'ProTV', url: 'protv.ro', focus: 'News' },
      { name: 'G4Media', url: 'g4media.ro', focus: 'Analysis' },
      { name: 'HotNews', url: 'hotnews.ro', focus: 'News' },
      { name: 'Euractiv Romania', url: 'euractiv.ro', focus: 'EU Policy' },
    ],
  },
};

export const CATEGORIES = [
  { id: 'eu_policy', label: 'EU Legislation & Policy' },
  { id: 'economic', label: 'Economic Stories' },
  { id: 'environment', label: 'Environmental Findings' },
  { id: 'science', label: 'Scientific Research' },
  { id: 'history', label: 'Historical Context' },
  { id: 'human_interest', label: 'Human Interest' },
  { id: 'russia', label: 'Hybrid War — Russia' },
  { id: 'human_rights', label: 'Human Rights Violations' },
  { id: 'corruption', label: 'Corruption' },
];

export function getOutletsString(language) {
  const config = OUTLETS_BY_LANGUAGE[language];
  if (!config) return '';
  return config.outlets.map(o => `${o.name} (${o.url})`).join(', ');
}
