#!/usr/bin/env python3
"""
from typing import Dict
Example Plugin: Weather Integration for Nix for Humanity
Shows how to extend the headless core with custom functionality
"""

import re
import json
import random
from typing import Dict, Any, Optional
from datetime import datetime

# Plugin metadata
PLUGIN_INFO = {
    'name': 'Weather Plugin',
    'version': '1.0.0',
    'description': 'Adds weather-related responses to Nix queries',
    'author': 'Example Developer',
    'capabilities': ['weather', 'environment']
}


class WeatherPlugin:
    """
    Example plugin that handles weather-related queries
    
    This demonstrates:
    - Intent detection for custom domains
    - Integration with external services (mocked here)
    - Context-aware responses
    - Visual output for GUIs
    """
    
    def __init__(self):
        self.name = PLUGIN_INFO['name']
        self.weather_patterns = [
            r'\bweather\b',
            r'\btemperature\b',
            r'\brain\b.*\btoday\b',
            r'\bforecast\b',
            r'\bhumidity\b',
            r'\bsnow\b.*\btomorrow\b'
        ]
        
        # Mock weather data (in real plugin, would call weather API)
        self.mock_weather = {
            'temperature': 22,
            'condition': 'partly cloudy',
            'humidity': 65,
            'wind': 15,
            'forecast': ['sunny', 'cloudy', 'rainy', 'partly cloudy']
        }
    
    def can_handle(self, intent: Dict[str, Any]) -> bool:
        """
        Check if this plugin can handle the given intent
        
        Args:
            intent: Intent dictionary from the core engine
            
        Returns:
            True if this plugin should handle the query
        """
        query = intent.get('query', '').lower()
        
        # Check if query matches weather patterns
        for pattern in self.weather_patterns:
            if re.search(pattern, query):
                return True
        
        # Also handle if explicitly categorized as weather
        if intent.get('action') == 'weather_query':
            return True
        
        return False
    
    def handle(self, intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the weather-related query
        
        Args:
            intent: Intent dictionary
            context: Context including session, personality, etc.
            
        Returns:
            Response dictionary
        """
        query = intent.get('query', '')
        personality = context.get('personality', 'friendly')
        
        # Determine specific weather request
        if 'temperature' in query:
            response = self._handle_temperature(personality)
        elif 'forecast' in query or 'tomorrow' in query:
            response = self._handle_forecast(personality)
        elif 'rain' in query:
            response = self._handle_rain_query(personality)
        else:
            response = self._handle_general_weather(personality)
        
        # Add visual data if GUI capabilities
        if 'visual' in context.get('capabilities', []):
            response['visual'] = self._generate_visual()
        
        # Mark as successful plugin handling
        response['success'] = True
        response['plugin'] = self.name
        
        return response
    
    def _handle_temperature(self, personality: str) -> Dict[str, Any]:
        """Handle temperature queries"""
        temp = self.mock_weather['temperature']
        
        if personality == 'minimal':
            text = f"{temp}°C"
        elif personality == 'friendly':
            text = f"The current temperature is {temp}°C. Perfect for a walk!"
        elif personality == 'technical':
            text = f"Temperature: {temp}°C ({temp * 9/5 + 32:.1f}°F), measured at {datetime.now().strftime('%H:%M')}"
        else:
            text = f"It's {temp}°C outside"
        
        return {
            'response': text,
            'data': {'temperature': temp},
            'confidence': 0.95
        }
    
    def _handle_forecast(self, personality: str) -> Dict[str, Any]:
        """Handle forecast queries"""
        tomorrow = random.choice(self.mock_weather['forecast'])
        
        if personality == 'minimal':
            text = f"Tomorrow: {tomorrow}"
        elif personality == 'encouraging':
            text = f"Tomorrow will be {tomorrow}! Great day to work on your NixOS configuration! 🌟"
        else:
            text = f"Tomorrow's forecast is {tomorrow}"
        
        return {
            'response': text,
            'data': {'forecast': tomorrow},
            'confidence': 0.85
        }
    
    def _handle_rain_query(self, personality: str) -> Dict[str, Any]:
        """Handle rain-specific queries"""
        will_rain = random.choice([True, False])
        
        if personality == 'symbiotic':
            text = "I'm checking the weather patterns... " + \
                   ("It looks like rain is possible. Maybe a good day for indoor NixOS learning?" if will_rain 
                    else "No rain expected! Though weather prediction isn't my specialty 🤝")
        else:
            text = "Rain is expected today" if will_rain else "No rain expected today"
        
        return {
            'response': text,
            'data': {'rain_expected': will_rain},
            'confidence': 0.7
        }
    
    def _handle_general_weather(self, personality: str) -> Dict[str, Any]:
        """Handle general weather queries"""
        condition = self.mock_weather['condition']
        temp = self.mock_weather['temperature']
        
        if personality == 'minimal':
            text = f"{temp}°C, {condition}"
        elif personality == 'friendly':
            text = f"It's {temp}°C and {condition} outside. How can I help with your NixOS needs today?"
        else:
            text = f"Current weather: {temp}°C, {condition}"
        
        return {
            'response': text,
            'data': self.mock_weather,
            'confidence': 0.9
        }
    
    def _generate_visual(self) -> Dict[str, Any]:
        """Generate visual representation for GUIs"""
        return {
            'type': 'weather_card',
            'data': {
                'temperature': self.mock_weather['temperature'],
                'condition': self.mock_weather['condition'],
                'humidity': f"{self.mock_weather['humidity']}%",
                'wind': f"{self.mock_weather['wind']} km/h",
                'icon': self._get_weather_icon(self.mock_weather['condition'])
            }
        }
    
    def _get_weather_icon(self, condition: str) -> str:
        """Get weather icon based on condition"""
        icons = {
            'sunny': '☀️',
            'partly cloudy': '⛅',
            'cloudy': '☁️',
            'rainy': '🌧️',
            'snow': '❄️'
        }
        return icons.get(condition, '🌤️')
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return PLUGIN_INFO
    
    def shutdown(self):
        """Clean shutdown (if needed)"""
        pass


# Plugin registration functions
def initialize():
    """Initialize the plugin"""
    return WeatherPlugin()


def get_plugin_info():
    """Get plugin metadata"""
    return PLUGIN_INFO


# Test the plugin
if __name__ == "__main__":
    plugin = WeatherPlugin()
    
    test_queries = [
        "What's the weather today?",
        "Will it rain tomorrow?",
        "Current temperature",
        "Weather forecast"
    ]
    
    print("🌤️  Weather Plugin Test\n")
    
    for query in test_queries:
        intent = {'query': query, 'action': 'unknown'}
        context = {'personality': 'friendly', 'capabilities': ['text', 'visual']}
        
        if plugin.can_handle(intent):
            result = plugin.handle(intent, context)
            print(f"Query: {query}")
            print(f"Response: {result['response']}")
            if result.get('visual'):
                print(f"Visual: {result['visual']['data']['icon']}")
            print()
        else:
            print(f"Cannot handle: {query}\n")