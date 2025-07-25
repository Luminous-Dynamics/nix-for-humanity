/**
 * Unit tests for typo correction
 * Tests Levenshtein distance and common typo patterns
 */

const { typoCorrector, levenshteinDistance } = require('../../../js/nlp/dist-cjs/typo-corrector.js');

describe('Typo Corrector', () => {
  
  describe('Levenshtein Distance', () => {
    test.each([
      ['kitten', 'sitting', 3],
      ['saturday', 'sunday', 3],
      ['', '', 0],
      ['a', '', 1],
      ['', 'a', 1],
      ['abc', 'abc', 0],
      ['firefox', 'firefox', 0],
      ['firefox', 'fierfix', 2],
      ['install', 'instal', 1],
      ['install', 'isntall', 2]
    ])('distance between "%s" and "%s" is %d', (str1, str2, expected) => {
      expect(levenshteinDistance(str1, str2)).toBe(expected);
    });
  });

  describe('Common Typo Patterns', () => {
    test.each([
      // Command typos
      ['instal firefox', 'install firefox'],
      ['intall vscode', 'install vscode'],
      ['isntall git', 'install git'],
      ['instlal package', 'install package'],
      ['udpate system', 'update system'],
      ['updtae everything', 'update everything'],
      ['upadte now', 'update now'],
      ['upgrad system', 'upgrade system'],
      
      // Package name typos
      ['fierfix', 'firefox'],
      ['firfox', 'firefox'],
      ['chorme', 'chrome'],
      ['chorome', 'chrome'],
      ['vscod', 'vscode'],
      ['vsocde', 'vscode'],
      ['vs cod', 'vscode'],
      ['spotifi', 'spotify'],
      ['sptoify', 'spotify'],
      ['dicord', 'discord'],
      ['disocrd', 'discord'],
      ['pyhton', 'python'],
      ['pyton', 'python'],
      ['pytohn', 'python'],
      
      // Common keyboard proximity errors
      ['teh', 'the'],
      ['taht', 'that'],
      ['wiht', 'with'],
      ['waht', 'what'],
      ['cna', 'can'],
      
      // Missing apostrophes
      ['dont', "don't"],
      ['wont', "won't"],
      ['cant', "can't"],
      ['isnt', "isn't"],
      ['arent', "aren't"],
      ['doesnt', "doesn't"],
      ['wouldnt', "wouldn't"],
      ['couldnt', "couldn't"],
      ['shouldnt', "shouldn't"]
    ])('corrects "%s" to "%s"', (typo, corrected) => {
      expect(typoCorrector.correct(typo)).toBe(corrected);
    });
  });

  describe('Word Correction', () => {
    test('corrects single words with small edit distance', () => {
      // These should be corrected (distance <= 2)
      expect(typoCorrector.correct('instal')).toBe('install');
      expect(typoCorrector.correct('updae')).toBe('update');
      expect(typoCorrector.correct('firefox')).toBe('firefox'); // Already correct
    });
    
    test('does not overcorrect words with large edit distance', () => {
      // These are too different (distance > 2)
      expect(typoCorrector.correct('xyz123')).toBe('xyz123');
      expect(typoCorrector.correct('asdfghjkl')).toBe('asdfghjkl');
    });
  });

  describe('Phrase Correction', () => {
    test('corrects multiple typos in a phrase', () => {
      expect(typoCorrector.correct('i neeed fierfix')).toBe('i need firefox');
      expect(typoCorrector.correct('instal vscod plz')).toBe('install vscode please');
      expect(typoCorrector.correct('cna you isntall spotify')).toBe('can you install spotify');
    });
    
    test('preserves correct words in mixed phrases', () => {
      expect(typoCorrector.correct('please instal firefox now')).toBe('please install firefox now');
      expect(typoCorrector.correct('i want vscod installed')).toBe('i want vscode installed');
    });
  });

  describe('Suggestion Generation', () => {
    test('suggests corrections for misspelled words', () => {
      const suggestions = typoCorrector.suggestCorrections('instal');
      
      expect(suggestions).toContain('install');
      expect(suggestions.length).toBeLessThanOrEqual(5);
      expect(suggestions.length).toBeGreaterThan(0);
    });
    
    test('suggests package names for typos', () => {
      const suggestions = typoCorrector.suggestCorrections('fierfix');
      expect(suggestions).toContain('firefox');
      
      const vscodeSuggestions = typoCorrector.suggestCorrections('vscod');
      expect(vscodeSuggestions).toContain('vscode');
    });
    
    test('returns empty array for very different words', () => {
      const suggestions = typoCorrector.suggestCorrections('zzzzzzzzz');
      expect(suggestions.length).toBe(0);
    });
  });

  describe('Case Handling', () => {
    test('preserves original casing when possible', () => {
      expect(typoCorrector.correct('INSTAL')).toBe('install'); // Normalizes to lowercase
      expect(typoCorrector.correct('Firefox')).toBe('Firefox'); // Already correct
    });
  });

  describe('Special Characters', () => {
    test('handles commands with special characters', () => {
      expect(typoCorrector.correct('instal fire-fox')).toBe('install fire-fox');
      expect(typoCorrector.correct('update_system')).toBe('update_system');
    });
  });

  describe('Performance', () => {
    test('handles long input efficiently', () => {
      const longInput = 'instal ' + 'a'.repeat(100);
      const start = Date.now();
      typoCorrector.correct(longInput);
      const duration = Date.now() - start;
      
      expect(duration).toBeLessThan(100); // Should complete in < 100ms
    });
    
    test('handles many corrections efficiently', () => {
      const manyTypos = 'instal fierfix and vscod and spotifi and pyhton';
      const start = Date.now();
      const corrected = typoCorrector.correct(manyTypos);
      const duration = Date.now() - start;
      
      expect(corrected).toBe('install firefox and vscode and spotify and python');
      expect(duration).toBeLessThan(50); // Should be fast
    });
  });

  describe('Edge Cases', () => {
    test('handles empty input', () => {
      expect(typoCorrector.correct('')).toBe('');
    });
    
    test('handles single character input', () => {
      expect(typoCorrector.correct('a')).toBe('a');
    });
    
    test('handles repeated characters', () => {
      expect(typoCorrector.correct('innnstall')).toBe('install');
    });
    
    test('handles mixed typos and correct words', () => {
      const input = 'please instal firefox and update system';
      const expected = 'please install firefox and update system';
      expect(typoCorrector.correct(input)).toBe(expected);
    });
  });

  describe('Integration with Intent Engine', () => {
    test('typo correction improves intent recognition', () => {
      const { intentEngine } = require('../../../js/nlp/dist-cjs/intent-engine.js');
      
      // Without typo correction, these might fail
      const typoInputs = [
        'instal firefox',
        'i neeed vscode',
        'udpate my system',
        'fierfix install please'
      ];
      
      typoInputs.forEach(input => {
        const intent = intentEngine.recognize(input);
        expect(intent.type).not.toBe('unknown');
        expect(intent.confidence).toBeGreaterThan(0.7);
      });
    });
  });
});