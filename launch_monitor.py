#!/usr/bin/env python3
"""
Launch Day Monitoring Script
Tracks all metrics in real-time
"""

import requests
import json
import time
from datetime import datetime
import subprocess

class LaunchMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.github_repo = "Luminous-Dynamics/luminous-nix"
        self.discord_invite = "https://discord.gg/TWSVAXHC"
        self.initial_stars = None
        
    def get_github_stats(self):
        """Fetch GitHub statistics"""
        try:
            response = requests.get(f"https://api.github.com/repos/{self.github_repo}")
            data = response.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "watchers": data.get("watchers_count", 0),
                "issues": data.get("open_issues_count", 0)
            }
        except:
            return {"stars": 0, "forks": 0, "watchers": 0, "issues": 0}
    
    def get_hn_position(self, story_id=None):
        """Check Hacker News position"""
        try:
            # Get front page
            response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            top_stories = response.json()[:30]  # Top 30
            
            if story_id and story_id in top_stories:
                position = top_stories.index(story_id) + 1
                return position
            return None
        except:
            return None
    
    def create_dashboard(self):
        """Create live dashboard HTML"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Luminous Nix Launch Dashboard</title>
            <meta http-equiv="refresh" content="30">
            <style>
                body {
                    font-family: 'SF Pro Display', -apple-system, Arial;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                h1 {
                    text-align: center;
                    font-size: 3em;
                    margin-bottom: 30px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .metrics {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .metric {
                    background: rgba(255,255,255,0.1);
                    backdrop-filter: blur(10px);
                    padding: 30px;
                    border-radius: 20px;
                    text-align: center;
                    transition: transform 0.3s;
                }
                .metric:hover {
                    transform: translateY(-5px);
                }
                .metric .value {
                    font-size: 3em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .metric .label {
                    font-size: 1.2em;
                    opacity: 0.9;
                }
                .metric .change {
                    font-size: 1em;
                    margin-top: 10px;
                    color: #4CAF50;
                }
                .metric.highlight {
                    background: rgba(76, 175, 80, 0.3);
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                .timeline {
                    background: rgba(255,255,255,0.1);
                    backdrop-filter: blur(10px);
                    padding: 20px;
                    border-radius: 20px;
                    margin-top: 20px;
                }
                .event {
                    padding: 10px;
                    margin: 10px 0;
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                    border-left: 4px solid #4CAF50;
                }
                .actions {
                    margin-top: 30px;
                    text-align: center;
                }
                .button {
                    display: inline-block;
                    padding: 15px 30px;
                    margin: 10px;
                    background: rgba(255,255,255,0.2);
                    border: 2px solid white;
                    border-radius: 30px;
                    text-decoration: none;
                    color: white;
                    transition: all 0.3s;
                }
                .button:hover {
                    background: white;
                    color: #667eea;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Luminous Nix Launch Dashboard</h1>
                <div class="metrics">
                    <div class="metric highlight">
                        <div class="value">⭐ {stars}</div>
                        <div class="label">GitHub Stars</div>
                        <div class="change">+{star_change} since launch</div>
                    </div>
                    <div class="metric">
                        <div class="value">🍴 {forks}</div>
                        <div class="label">Forks</div>
                    </div>
                    <div class="metric">
                        <div class="value">#{hn_position}</div>
                        <div class="label">HN Position</div>
                    </div>
                    <div class="metric">
                        <div class="value">⏱️ {hours}h {minutes}m</div>
                        <div class="label">Since Launch</div>
                    </div>
                </div>
                
                <div class="timeline">
                    <h2>📊 Launch Timeline</h2>
                    <div class="event">✅ 9:00 AM - Posted to Hacker News</div>
                    <div class="event">✅ 9:15 AM - 10 upvotes reached</div>
                    <div class="event">✅ 9:30 AM - First comment response</div>
                    <div class="event">🔄 {current_time} - Monitoring...</div>
                </div>
                
                <div class="actions">
                    <a href="https://news.ycombinator.com" class="button">Check HN</a>
                    <a href="https://github.com/{repo}" class="button">View GitHub</a>
                    <a href="{discord}" class="button">Join Discord</a>
                </div>
                
                <p style="text-align: center; margin-top: 30px; opacity: 0.7;">
                    Auto-refreshes every 30 seconds | Last update: {update_time}
                </p>
            </div>
        </body>
        </html>
        """
        
        stats = self.get_github_stats()
        if self.initial_stars is None:
            self.initial_stars = stats["stars"]
        
        elapsed = datetime.now() - self.start_time
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        
        html = html.format(
            stars=stats["stars"],
            star_change=stats["stars"] - self.initial_stars,
            forks=stats["forks"],
            hn_position=self.get_hn_position() or "?",
            hours=hours,
            minutes=minutes,
            current_time=datetime.now().strftime("%I:%M %p"),
            repo=self.github_repo,
            discord=self.discord_invite,
            update_time=datetime.now().strftime("%I:%M:%S %p")
        )
        
        with open("launch_dashboard.html", "w") as f:
            f.write(html)
        
        return stats
    
    def send_milestone_alert(self, milestone, value):
        """Send alerts for milestones"""
        print(f"🎉 MILESTONE: {milestone} reached {value}!")
        
        # Post to Discord webhook if configured
        webhook_url = "YOUR_DISCORD_WEBHOOK"
        if webhook_url != "YOUR_DISCORD_WEBHOOK":
            requests.post(webhook_url, json={
                "content": f"🎉 **MILESTONE REACHED!**\n{milestone}: {value}"
            })
    
    def monitor(self):
        """Main monitoring loop"""
        print("🚀 Launch Monitor Started!")
        print("=" * 50)
        
        milestones = {
            "stars": [10, 25, 50, 100, 200, 500, 1000],
            "forks": [5, 10, 25, 50]
        }
        
        reached_milestones = set()
        
        while True:
            stats = self.create_dashboard()
            
            # Check milestones
            for metric, thresholds in milestones.items():
                current_value = stats.get(metric, 0)
                for threshold in thresholds:
                    milestone_key = f"{metric}_{threshold}"
                    if current_value >= threshold and milestone_key not in reached_milestones:
                        self.send_milestone_alert(f"{metric.title()}", threshold)
                        reached_milestones.add(milestone_key)
            
            # Console output
            print(f"\r⭐ Stars: {stats['stars']} | 🍴 Forks: {stats['forks']} | 👁️ Watchers: {stats['watchers']}", end="")
            
            time.sleep(30)

if __name__ == "__main__":
    monitor = LaunchMonitor()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║            LUMINOUS NIX LAUNCH MONITOR                       ║
    ╚══════════════════════════════════════════════════════════════╝
    
    This will track:
    • GitHub stars, forks, watchers
    • Hacker News position
    • Time since launch
    • Milestone alerts
    
    Dashboard available at: launch_dashboard.html
    Open in browser for live view!
    
    Press Ctrl+C to stop monitoring.
    """)
    
    try:
        monitor.monitor()
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped. Good luck with the launch!")