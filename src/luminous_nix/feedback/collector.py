#!/usr/bin/env python3
"""
Feedback Collector for Luminous Nix
Helps improve the neural HRM through user feedback
"""

import json
import time
from pathlib import Path
from typing import Optional


class FeedbackCollector:
    def __init__(self, feedback_file: str = "data/feedback.jsonl"):
        self.feedback_file = Path(feedback_file)
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)

    def collect(self, query: str, response: str, confidence: float) -> Optional[bool]:
        """Collect feedback for a query-response pair"""

        # Only ask for feedback on low-confidence responses
        if confidence < 0.6:
            print("\n🤔 I'm not very confident about this answer.")
            print("Did it work? (y/n/skip): ", end="")

            feedback = input().strip().lower()

            if feedback == "y":
                worked = True
            elif feedback == "n":
                worked = False
            else:
                return None

            # Store feedback
            self.store(query, response, worked, confidence)

            if worked:
                print("✅ Great! I'll remember that.")
            else:
                print("❌ Sorry it didn't work. I'll learn from this.")

            return worked

        return None

    def store(self, query: str, response: str, worked: bool, confidence: float):
        """Store feedback for training"""

        entry = {
            "query": query,
            "response": response,
            "worked": worked,
            "confidence": confidence,
            "timestamp": time.time(),
        }

        with open(self.feedback_file, "a") as f:
            json.dump(entry, f)
            f.write("\n")

    def get_statistics(self) -> dict:
        """Get feedback statistics"""

        if not self.feedback_file.exists():
            return {"total": 0, "successful": 0, "failed": 0}

        total = 0
        successful = 0
        failed = 0

        with open(self.feedback_file) as f:
            for line in f:
                entry = json.loads(line)
                total += 1
                if entry["worked"]:
                    successful += 1
                else:
                    failed += 1

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
        }


# Global instance
feedback_collector = FeedbackCollector()
