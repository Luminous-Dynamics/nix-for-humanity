/**
 * Test script for intent recognition
 */

import { intentEngine } from './intent-engine';
import { nixWrapper } from './nix-wrapper';

// Test cases representing our 5 personas
const testCases = [
  // Grandma Rose
  "I need a web browser",
  "Install firefox please",
  "My internet isn't working",
  "Make the text bigger",
  
  // Maya (teenager)
  "install vscode",
  "i want that programming thing",
  "update my system",
  "what programs do i have",
  
  // David (restaurant owner)
  "Show me installed programs",
  "Is my system up to date?",
  "Install libreoffice",
  "Fix my printer",
  
  // Dr. Sarah (researcher)
  "Install python3",
  "Configure development environment",
  "What is nixpkgs",
  "Show system status",
  
  // Alex (blind developer)
  "Install screen reader",
  "Make text larger",
  "What is installed",
  "Help me with audio"
];

console.log("🧪 Testing Intent Recognition Engine\n");

testCases.forEach((input, index) => {
  console.log(`\n📝 Test ${index + 1}: "${input}"`);
  
  // Recognize intent
  const intent = intentEngine.recognize(input);
  console.log(`✨ Intent: ${intent.type} (confidence: ${(intent.confidence * 100).toFixed(0)}%)`);
  
  if (intent.entities.length > 0) {
    console.log(`📦 Entities:`, intent.entities.map(e => `${e.type}:${e.value}`).join(', '));
  }
  
  // Convert to command
  const command = nixWrapper.intentToCommand(intent);
  if (command) {
    console.log(`🔧 Command: ${command.command} ${command.args.join(' ')}`);
    
    // Simulate execution
    nixWrapper.execute(command).then(result => {
      console.log(`💬 Response: ${result.naturalLanguageResponse}`);
    });
  } else {
    console.log(`❓ No command mapping for intent type: ${intent.type}`);
  }
});

// Interactive test function
export async function interactiveTest(userInput: string) {
  console.log(`\n👤 User: "${userInput}"`);
  
  const intent = intentEngine.recognize(userInput);
  console.log(`🤖 Understanding: ${intent.type} intent with ${(intent.confidence * 100).toFixed(0)}% confidence`);
  
  const command = nixWrapper.intentToCommand(intent);
  if (command) {
    const result = await nixWrapper.execute(command);
    console.log(`🤖 Nix: ${result.naturalLanguageResponse}`);
    return result;
  } else {
    console.log(`🤖 Nix: I'm not sure how to help with that. Can you tell me more about what you're trying to do?`);
    return null;
  }
}