/**
 * Voice Interface for Nix for Humanity
 * Uses Web Speech API for voice recognition and synthesis
 */
export class VoiceInterface {
    constructor() {
        this.isListening = false;
        // Check for Web Speech API support
        const SpeechRecognition = window.SpeechRecognition ||
            window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            throw new Error('Speech recognition not supported in this browser');
        }
        this.recognition = new SpeechRecognition();
        this.synthesis = window.speechSynthesis;
        this.setupRecognition();
    }
    /**
     * Configure speech recognition
     */
    setupRecognition() {
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 3;
        this.recognition.lang = 'en-US';
        this.recognition.onstart = () => {
            this.isListening = true;
            console.log('🎤 Listening...');
        };
        this.recognition.onresult = (event) => {
            const last = event.results.length - 1;
            const transcript = event.results[last][0].transcript;
            const isFinal = event.results[last].isFinal;
            if (isFinal && this.onResultCallback) {
                console.log('🗣️ Heard:', transcript);
                this.onResultCallback(transcript);
            }
        };
        this.recognition.onerror = (event) => {
            console.error('❌ Speech recognition error:', event.error);
            this.isListening = false;
            // Restart on recoverable errors
            if (['no-speech', 'audio-capture'].includes(event.error)) {
                setTimeout(() => this.startListening(), 1000);
            }
        };
        this.recognition.onend = () => {
            this.isListening = false;
            console.log('🔇 Stopped listening');
        };
    }
    /**
     * Start listening for voice input
     */
    startListening(callback) {
        if (callback) {
            this.onResultCallback = callback;
        }
        if (!this.isListening) {
            try {
                this.recognition.start();
            }
            catch (error) {
                console.error('Failed to start recognition:', error);
            }
        }
    }
    /**
     * Stop listening
     */
    stopListening() {
        if (this.isListening) {
            this.recognition.stop();
        }
    }
    /**
     * Speak text using speech synthesis
     */
    speak(text, options) {
        // Cancel any ongoing speech
        this.synthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        // Apply options
        utterance.rate = options?.rate || 0.9; // Slightly slower for clarity
        utterance.pitch = options?.pitch || 1.0;
        utterance.volume = options?.volume || 1.0;
        // Use a clear voice if available
        const voices = this.synthesis.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google') ||
            v.name.includes('Microsoft') ||
            v.name.includes('Samantha') // macOS
        );
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }
        // Speak
        this.synthesis.speak(utterance);
        return new Promise((resolve) => {
            utterance.onend = () => resolve();
            utterance.onerror = () => resolve();
        });
    }
    /**
     * Check if currently listening
     */
    getIsListening() {
        return this.isListening;
    }
    /**
     * Get available voices
     */
    getVoices() {
        return this.synthesis.getVoices();
    }
    /**
     * Simple voice command handler
     */
    enableVoiceCommands(commandHandler) {
        // Activate on wake word
        this.recognition.continuous = true;
        this.recognition.onresult = (event) => {
            const last = event.results.length - 1;
            const transcript = event.results[last][0].transcript.toLowerCase();
            const isFinal = event.results[last].isFinal;
            if (isFinal) {
                // Check for wake word
                if (transcript.includes('hey nix') ||
                    transcript.includes('okay nix') ||
                    transcript.includes('nix help')) {
                    // Extract command after wake word
                    const wakeWords = ['hey nix', 'okay nix', 'nix help'];
                    let command = transcript;
                    for (const wake of wakeWords) {
                        if (transcript.includes(wake)) {
                            command = transcript.split(wake)[1]?.trim() || '';
                            break;
                        }
                    }
                    if (command) {
                        this.speak('Yes?', { rate: 1.1 }).then(() => {
                            commandHandler(command);
                        });
                    }
                    else {
                        this.speak('How can I help?', { rate: 1.1 });
                    }
                }
            }
        };
        this.startListening();
    }
}
// Singleton instance
export const voiceInterface = new VoiceInterface();
//# sourceMappingURL=voice-interface.js.map