/**
 * Voice Interface for Nix for Humanity
 * Uses Web Speech API for voice recognition and synthesis
 */
export declare class VoiceInterface {
    private recognition;
    private synthesis;
    private isListening;
    private onResultCallback?;
    constructor();
    /**
     * Configure speech recognition
     */
    private setupRecognition;
    /**
     * Start listening for voice input
     */
    startListening(callback?: (text: string) => void): void;
    /**
     * Stop listening
     */
    stopListening(): void;
    /**
     * Speak text using speech synthesis
     */
    speak(text: string, options?: {
        rate?: number;
        pitch?: number;
        volume?: number;
    }): Promise<void>;
    /**
     * Check if currently listening
     */
    getIsListening(): boolean;
    /**
     * Get available voices
     */
    getVoices(): SpeechSynthesisVoice[];
    /**
     * Simple voice command handler
     */
    enableVoiceCommands(commandHandler: (command: string) => void): void;
}
export declare const voiceInterface: VoiceInterface;
