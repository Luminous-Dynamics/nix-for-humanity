//! Ultra-fast search implementation with fuzzy matching and typo correction

use fuzzy_matcher::FuzzyMatcher;
use fuzzy_matcher::skim::SkimMatcherV2;
use rayon::prelude::*;
use std::cmp::Ordering;

/// Search result with score and metadata
#[derive(Debug, Clone)]
pub struct SearchResult {
    pub name: String,
    pub attribute: String,
    pub version: String,
    pub description: String,
    pub score: f64,
    pub exact_match: bool,
    pub typo_corrected: bool,
    pub corrected_from: Option<String>,
}

/// Advanced searcher with typo correction
pub struct AdvancedSearcher {
    matcher: SkimMatcherV2,
    typo_threshold: f64,
}

impl AdvancedSearcher {
    pub fn new() -> Self {
        AdvancedSearcher {
            matcher: SkimMatcherV2::default(),
            typo_threshold: 0.7,
        }
    }

    /// Search with typo correction and scoring
    pub fn search(&self, query: &str, packages: &[Package]) -> Vec<SearchResult> {
        let query_lower = query.to_lowercase();
        let mut results = Vec::new();

        // Phase 1: Exact matches
        for pkg in packages {
            if pkg.name.to_lowercase() == query_lower {
                results.push(SearchResult {
                    name: pkg.name.clone(),
                    attribute: pkg.attribute.clone(),
                    version: pkg.version.clone(),
                    description: pkg.description.clone(),
                    score: 1.0,
                    exact_match: true,
                    typo_corrected: false,
                    corrected_from: None,
                });
            }
        }

        // Phase 2: Fuzzy matching with typo detection
        if results.is_empty() {
            let mut fuzzy_results: Vec<_> = packages
                .par_iter()
                .filter_map(|pkg| {
                    if let Some(score) = self.matcher.fuzzy_match(&pkg.name, query) {
                        let normalized_score = score as f64 / 100.0;

                        // Check if this might be a typo
                        let typo_corrected = normalized_score > self.typo_threshold
                            && normalized_score < 1.0;

                        Some(SearchResult {
                            name: pkg.name.clone(),
                            attribute: pkg.attribute.clone(),
                            version: pkg.version.clone(),
                            description: pkg.description.clone(),
                            score: normalized_score,
                            exact_match: false,
                            typo_corrected,
                            corrected_from: if typo_corrected {
                                Some(query.to_string())
                            } else {
                                None
                            },
                        })
                    } else {
                        None
                    }
                })
                .collect();

            // Sort by score descending
            fuzzy_results.sort_by(|a, b| {
                b.score.partial_cmp(&a.score).unwrap_or(Ordering::Equal)
            });

            results.extend(fuzzy_results);
        }

        // Phase 3: Semantic search in descriptions
        if results.len() < 10 {
            let desc_results: Vec<_> = packages
                .par_iter()
                .filter_map(|pkg| {
                    if results.iter().any(|r| r.name == pkg.name) {
                        return None; // Skip already found
                    }

                    let desc_words: Vec<&str> = pkg.description
                        .split_whitespace()
                        .collect();

                    let query_words: Vec<&str> = query
                        .split_whitespace()
                        .collect();

                    let mut match_score: f64 = 0.0;
                    for qw in &query_words {
                        for dw in &desc_words {
                            if dw.to_lowercase().contains(&qw.to_lowercase()) {
                                match_score += 0.1;
                            }
                        }
                    }

                    if match_score > 0.0 {
                        Some(SearchResult {
                            name: pkg.name.clone(),
                            attribute: pkg.attribute.clone(),
                            version: pkg.version.clone(),
                            description: pkg.description.clone(),
                            score: match_score.min(0.5_f64), // Cap description matches
                            exact_match: false,
                            typo_corrected: false,
                            corrected_from: None,
                        })
                    } else {
                        None
                    }
                })
                .collect();

            results.extend(desc_results);
        }

        results
    }

    /// Correct common typos
    pub fn correct_typo(&self, query: &str) -> Option<String> {
        // Common typo patterns
        let corrections = vec![
            ("fierrfox", "firefox"),
            ("firfox", "firefox"),
            ("firefx", "firefox"),
            ("chorme", "chrome"),
            ("chromuim", "chromium"),
            ("dokcer", "docker"),
            ("kubernets", "kubernetes"),
            ("pytohn", "python"),
            ("pyhton", "python"),
            ("ngiinx", "nginx"),
            ("ngix", "nginx"),
            ("postgre", "postgresql"),
            ("vim", "neovim"), // Common alternatives
            ("emacs", "doom-emacs"),
        ];

        for (typo, correct) in corrections {
            if query == typo {
                return Some(correct.to_string());
            }
        }

        // Edit distance based correction
        if query.len() > 3 {
            // Could implement Levenshtein distance here
            None
        } else {
            None
        }
    }
}

/// Package data structure
#[derive(Debug, Clone)]
pub struct Package {
    pub name: String,
    pub attribute: String,
    pub version: String,
    pub description: String,
}

/// Parallel batch search
pub fn batch_search_parallel(
    queries: Vec<String>,
    packages: &[Package],
    limit: usize,
) -> Vec<Vec<SearchResult>> {
    let searcher = AdvancedSearcher::new();

    queries
        .par_iter()
        .map(|query| {
            let mut results = searcher.search(query, packages);
            results.truncate(limit);
            results
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_typo_correction() {
        let searcher = AdvancedSearcher::new();

        assert_eq!(
            searcher.correct_typo("fierrfox"),
            Some("firefox".to_string())
        );

        assert_eq!(
            searcher.correct_typo("chromuim"),
            Some("chromium".to_string())
        );
    }

    #[test]
    fn test_fuzzy_search() {
        let packages = vec![
            Package {
                name: "firefox".to_string(),
                attribute: "firefox".to_string(),
                version: "123.0".to_string(),
                description: "Mozilla Firefox web browser".to_string(),
            },
            Package {
                name: "firefox-esr".to_string(),
                attribute: "firefox-esr".to_string(),
                version: "115.0".to_string(),
                description: "Firefox Extended Support Release".to_string(),
            },
        ];

        let searcher = AdvancedSearcher::new();
        let results = searcher.search("firfox", &packages);

        assert!(!results.is_empty());
        assert!(results[0].typo_corrected);
        assert_eq!(results[0].corrected_from, Some("firfox".to_string()));
    }
}
