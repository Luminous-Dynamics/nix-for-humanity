# 🌍 Multi-Language Support Guide - Nix for Humanity

## Vision

Natural language means ALL natural languages. Nix for Humanity aims to understand every user in their native language.

## Current Status

### ✅ Fully Supported
- **English** (US, UK, AU, CA, IN)
  - Full intent recognition
  - All commands supported
  - Accent adaptation

### 🚧 In Development
- **Spanish** (ES, MX, AR)
- **French** (FR, CA)  
- **German** (DE, AT, CH)
- **Mandarin Chinese** (CN, TW)
- **Japanese** (JP)
- **Portuguese** (BR, PT)

### 📋 Planned
- Arabic, Hindi, Russian, Korean, Italian, Dutch, Swedish, Polish

## How Multi-Language Works

### 1. Voice Recognition
Each language uses appropriate Whisper model:
```yaml
Languages:
  English: whisper-base.en (140MB)
  Spanish: whisper-base.es (140MB)
  French: whisper-base.fr (140MB)
  German: whisper-base.de (140MB)
  Multilingual: whisper-base (140MB) # Supports 99 languages
```

### 2. Natural Language Understanding
Each language has its own intent patterns:
```typescript
// Spanish patterns
const SPANISH_PATTERNS = {
  install: ["instalar", "agregar", "poner", "necesito"],
  remove: ["quitar", "eliminar", "borrar", "desinstalar"],
  update: ["actualizar", "mejorar", "renovar"],
  help: ["ayuda", "ayúdame", "socorro", "no entiendo"]
};

// French patterns
const FRENCH_PATTERNS = {
  install: ["installer", "ajouter", "mettre", "j'ai besoin de"],
  remove: ["supprimer", "enlever", "désinstaller", "retirer"],
  update: ["mettre à jour", "actualiser", "rafraîchir"],
  help: ["aide", "aidez-moi", "au secours", "je ne comprends pas"]
};
```

### 3. Response Generation
Responses in user's language:
```typescript
const RESPONSES = {
  en: {
    installing: "Installing {package}...",
    success: "Successfully installed {package}",
    error: "Could not install {package}"
  },
  es: {
    installing: "Instalando {package}...",
    success: "{package} instalado correctamente",
    error: "No se pudo instalar {package}"
  },
  fr: {
    installing: "Installation de {package}...",
    success: "{package} installé avec succès",
    error: "Impossible d'installer {package}"
  }
};
```

## Adding a New Language

### Step 1: Add Language Configuration
```typescript
// config/languages/hindi.ts
export const HINDI_CONFIG = {
  code: 'hi',
  name: 'हिन्दी',
  whisperModel: 'whisper-base.hi',
  direction: 'ltr',
  numberFormat: 'en-IN',
  dateFormat: 'dd/mm/yyyy'
};
```

### Step 2: Create Intent Patterns
```typescript
// nlp/patterns/hindi.ts
export const HINDI_PATTERNS = {
  install: ["इंस्टॉल करें", "डालें", "चाहिए", "लगाएं"],
  remove: ["हटाएं", "निकालें", "डिलीट करें"],
  update: ["अपडेट करें", "नया करें", "ताज़ा करें"],
  // ... more patterns
};
```

### Step 3: Add Response Templates
```typescript
// responses/hindi.ts
export const HINDI_RESPONSES = {
  installing: "{package} इंस्टॉल हो रहा है...",
  success: "{package} सफलतापूर्वक इंस्टॉल हो गया",
  error: "{package} इंस्टॉल नहीं हो सका",
  // ... more responses
};
```

### Step 4: Add Number/Date Formatting
```typescript
// formatters/hindi.ts
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('hi-IN').format(num);
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('hi-IN').format(date);
}
```

### Step 5: Test Thoroughly
```typescript
// tests/languages/hindi.test.ts
describe('Hindi Language Support', () => {
  test('recognizes install commands', () => {
    const inputs = [
      "firefox इंस्टॉल करें",
      "मुझे firefox चाहिए",
      "firefox डालें"
    ];
    
    inputs.forEach(input => {
      const intent = recognizeIntent(input, 'hi');
      expect(intent.action).toBe('install');
      expect(intent.package).toBe('firefox');
    });
  });
});
```

## Language Detection

### Automatic Detection
```typescript
// Auto-detect from system
const systemLang = process.env.LANG || 'en_US';
const language = systemLang.split('_')[0];

// Auto-detect from input
const detectedLang = detectLanguage(userInput);
if (detectedLang.confidence > 0.8) {
  switchLanguage(detectedLang.language);
}
```

### Manual Selection
```
User: "switch to Spanish"
Nix: "Cambiando a español. ¡Hola!"

User: "cambiar a inglés"  
Nix: "Switching to English. Hello!"
```

## Cultural Considerations

### Formal vs Informal
```typescript
// Spanish - formal/informal variants
const SPANISH_FORMAL = {
  greeting: "¿Cómo puedo ayudarle?",
  confirm: "¿Está seguro?"
};

const SPANISH_INFORMAL = {
  greeting: "¿Cómo puedo ayudarte?",
  confirm: "¿Estás seguro?"
};
```

### Right-to-Left Languages
```typescript
// Arabic configuration
const ARABIC_CONFIG = {
  direction: 'rtl',
  textAlign: 'right',
  mirrorUI: true
};
```

### Cultural Phrases
```typescript
// Japanese politeness levels
const JAPANESE_POLITENESS = {
  casual: "インストールする",
  polite: "インストールします",
  formal: "インストールいたします"
};
```

## Testing Multi-Language Support

### Automated Tests
```bash
# Run language tests
npm test -- --lang=all

# Test specific language
npm test -- --lang=es
```

### Manual Testing Checklist
- [ ] Voice recognition works
- [ ] Intent detection accurate
- [ ] Responses in correct language
- [ ] Numbers formatted correctly
- [ ] Dates formatted correctly
- [ ] RTL languages display properly
- [ ] Cultural variants respected

## Common Challenges

### 1. Package Name Translation
```typescript
// Don't translate package names
"instalar firefox" → install firefox ✓
"instalar zorro de fuego" → install ??? ✗

// Keep technical terms
"actualizar el kernel" → update kernel ✓
```

### 2. Mixed Language Input
```typescript
// Handle code-switching
"instalar el firefox y después update system"
// Recognized as: install firefox, then update system
```

### 3. Regional Variations
```typescript
// Mexican Spanish vs Spain Spanish
MX: "computadora" 
ES: "ordenador"
// Both recognized as "computer"
```

## Accessibility in Multiple Languages

### Screen Reader Support
- Language tags for proper pronunciation
- Phonetic descriptions where needed
- Language switching announcements

### Voice Variations
- Multiple accent models per language
- Dialect-specific recognition
- Speech impediment tolerance

## Contributing Translations

### What We Need
1. **Native speakers** to verify natural patterns
2. **Technical terms** in your language
3. **Common phrases** people use
4. **Error messages** that make sense
5. **Cultural adaptations**

### How to Contribute
1. Fork the repository
2. Add your language files
3. Include tests
4. Submit PR with examples
5. Help review other translations

## Future Plans

### Advanced Features
- Context-aware language switching
- Multi-language households
- Regional preference learning
- Dialect-specific models
- Sign language support (via camera)

### Community Features
- Crowdsourced translations
- Regional pattern sharing
- Accent training data
- Cultural adaptation guides

---

*"Every language is a unique way of seeing the world. Nix for Humanity aims to see through all of them."*

**Current language requests? Add an issue on GitHub!**