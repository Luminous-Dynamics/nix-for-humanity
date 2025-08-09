#!/usr/bin/env python3
"""
Enhancement script to add learning integration to ask-nix
Shows where to add learning hooks in the unified command
"""

# The key integration points for learning:

INTEGRATION_POINTS = """
# 1. In UnifiedNixAssistant.__init__, add:
self.learning_enabled = self.check_learning_enabled()

# 2. Add this method to UnifiedNixAssistant:
def check_learning_enabled(self):
    '''Check if learning is enabled in config'''
    config_file = Path.home() / ".config" / "nix-humanity" / "config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('learning_enabled', False)
    return False

# 3. In the answer() method, after getting the intent:
if self.learning_enabled and hasattr(self, 'learning_system'):
    # Record the query and intent
    self.current_command_id = self.learning_system.record_command(
        intent=intent['action'],
        query=query,
        command=f"ask-nix {query}",
        executed=False
    )

# 4. In execute_install(), after successful execution:
if self.learning_enabled and hasattr(self, 'learning_system') and hasattr(self, 'current_command_id'):
    self.learning_system.record_outcome(self.current_command_id, success=True)
    # Learn preferences
    self.learning_system.learn_user_preference('install_method', method)

# 5. In execute_install(), on error:
if self.learning_enabled and hasattr(self, 'learning_system') and hasattr(self, 'current_command_id'):
    self.learning_system.record_outcome(self.current_command_id, success=False, error=str(e))
    # Try to find a learned solution
    solution = self.learning_system.get_error_solution(str(e))
    if solution:
        print(f"\\n💡 Learned solution: {solution}")

# 6. Similar hooks for execute_list() and execute_remove()

# 7. In the answer() method, check for learned suggestions:
if self.learning_enabled and hasattr(self, 'learning_system'):
    learned = self.learning_system.get_learned_suggestions(intent['action'], query)
    if learned:
        print("\\n🧠 Based on your history:")
        for suggestion in learned[:2]:
            print(f"   • {suggestion['command']} ({suggestion['learned_from']})")
"""

def generate_integration_patch():
    """Generate a patch file for integrating learning"""
    patch = '''
--- a/bin/ask-nix
+++ b/bin/ask-nix
@@ -120,6 +120,7 @@ class UnifiedNixAssistant:
         self.cache = IntelligentPackageCache()
         self.learning_system = CommandLearningSystem()
+        self.learning_enabled = self.check_learning_enabled()
         
         # Visual settings
         self.visual_mode = True
@@ -140,6 +141,16 @@ class UnifiedNixAssistant:
         # Education system
         self.education = self.EducationSystem()
         
+    def check_learning_enabled(self):
+        """Check if learning is enabled in config"""
+        config_file = Path.home() / ".config" / "nix-humanity" / "config.json"
+        if config_file.exists():
+            import json
+            with open(config_file, 'r') as f:
+                config = json.load(f)
+                return config.get('learning_enabled', False)
+        return False
+        
     def enhance_response(self, response: str, query: str, personality: str) -> str:
         """Add personality to the factual response"""
@@ -760,6 +771,14 @@ class UnifiedNixAssistant:
         # Step 1: Extract intent using modern engine
         intent = self.modern_knowledge.extract_intent(query)
         
+        # Record command for learning
+        if self.learning_enabled and hasattr(self, 'learning_system'):
+            self.current_command_id = self.learning_system.record_command(
+                intent=intent['action'],
+                query=query,
+                command=f"ask-nix {query}",
+                executed=True
+            )
+        
         if self.show_intent:
             print(f"\\n🎯 Intent detected: {intent['action']}")
@@ -731,11 +740,21 @@ class UnifiedNixAssistant:
             
         if self.use_bridge:
             success = self.execute_with_bridge(package, command)
+            # Record outcome for learning
+            if self.learning_enabled and hasattr(self, 'current_command_id'):
+                self.learning_system.record_outcome(self.current_command_id, success=success)
+                if success:
+                    self.learning_system.learn_user_preference('install_method', method)
         else:
             # Execute and handle outcome
             try:
                 self.run_install_command(command, package)
+                # Record success
+                if self.learning_enabled and hasattr(self, 'current_command_id'):
+                    self.learning_system.record_outcome(self.current_command_id, success=True)
+                    self.learning_system.learn_user_preference('install_method', method)
             except Exception as e:
+                if self.learning_enabled and hasattr(self, 'current_command_id'):
+                    self.learning_system.record_outcome(self.current_command_id, success=False, error=str(e))
                 self.handle_install_error(e, package)
'''
    
    return patch

if __name__ == "__main__":
    print("🧠 Learning System Integration Guide")
    print("=" * 50)
    print("\nKey integration points:")
    print(INTEGRATION_POINTS)
    print("\n📝 To generate a patch file:")
    print("   python enhance-ask-nix-learning.py > learning.patch")
    print("   patch -p1 < learning.patch")
    print("\n✨ This will enable intelligent learning from every interaction!")