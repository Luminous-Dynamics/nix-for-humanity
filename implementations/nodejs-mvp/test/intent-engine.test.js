// 🧪 Intent Engine Tests
const IntentEngine = require('../services/intent-engine');

describe('IntentEngine', () => {
  let engine;

  beforeEach(() => {
    engine = new IntentEngine();
  });

  describe('recognize()', () => {
    test('recognizes search intent', async () => {
      const testCases = [
        'search firefox',
        'find firefox',
        'look for firefox',
        'what packages are available for firefox',
        'show me firefox packages'
      ];

      for (const input of testCases) {
        const result = await engine.recognize(input);
        expect(result.action).toBe('search');
        expect(result.package).toBe('firefox');
        expect(result.confidence).toBeGreaterThan(0.9);
      }
    });

    test('recognizes list intent', async () => {
      const testCases = [
        'list installed',
        'show installed packages',
        "what's installed",
        'my packages'
      ];

      for (const input of testCases) {
        const result = await engine.recognize(input);
        expect(result.action).toBe('list');
        expect(result.confidence).toBeGreaterThan(0.9);
      }
    });

    test('handles typos', async () => {
      const result = await engine.recognize('serach fire fox');
      expect(result.action).toBe('search');
      expect(result.package).toBe('firefox');
    });

    test('returns low confidence for unclear input', async () => {
      const result = await engine.recognize('do something with stuff');
      expect(result.confidence).toBeLessThan(0.5);
    });
  });

  describe('normalize()', () => {
    test('corrects common typos', () => {
      expect(engine.normalize('isntall package')).toBe('install package');
      expect(engine.normalize('serach something')).toBe('search something');
    });

    test('handles extra spaces', () => {
      expect(engine.normalize('  search   firefox  ')).toBe('search firefox');
    });

    test('converts to lowercase', () => {
      expect(engine.normalize('SEARCH FIREFOX')).toBe('search firefox');
    });
  });
});