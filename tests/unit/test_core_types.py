"""
Unit tests for core type definitions
"""

import unittest
from datetime import datetime
from luminous_nix.core.intents import (
    Request,
    Response,
    Context,
    Intent,
    IntentType,
    ExecutionResult,
    Plan,
    Command,
    Package,
    FeedbackItem
)


class TestCoreTypes(unittest.TestCase):
    """Test core type definitions"""
    
    def test_context_creation(self):
        """Test Context creation and defaults"""
        # Default context
        ctx = Context()
        self.assertTrue(ctx.execute is False)
        self.assertTrue(ctx.dry_run is False)
        self.assertEqual(ctx.personality, "friendly")
        self.assertEqual(ctx.frontend, "cli")
        self.assertEqual(ctx.session_id, "")
        self.assertEqual(ctx.user_preferences, {})
        
        # Custom context
        ctx = Context(
            execute=True,
            personality="minimal",
            frontend="tui",
            session_id="test-123"
        )
        self.assertTrue(ctx.execute is True)
        self.assertEqual(ctx.personality, "minimal")
        self.assertEqual(ctx.frontend, "tui")
        self.assertEqual(ctx.session_id, "test-123")
    
    def test_context_to_dict(self):
        """Test Context serialization"""
        ctx = Context(
            execute=True,
            personality="minimal",
            user_preferences={"theme": "dark"}
        )
        data = ctx.to_dict()
        
        self.assertTrue(data["execute"] is True)
        self.assertEqual(data["personality"], "minimal")
        self.assertEqual(data["user_preferences"]["theme"], "dark")
    
    def test_request_creation(self):
        """Test Request creation"""
        # Simple request
        req = Request(query="install firefox")
        self.assertEqual(req.query, "install firefox")
        self.assertTrue(isinstance(req.context, Context))
        self.assertTrue(isinstance(req.timestamp, datetime))
        
        # Request with context
        ctx = Context(personality="minimal")
        req = Request(query="update system", context=ctx)
        self.assertEqual(req.context.personality, "minimal")
    
    def test_request_serialization(self):
        """Test Request to/from dict"""
        req = Request(
            query="install firefox",
            context=Context(execute=True, personality="minimal")
        )
        
        # To dict
        data = req.to_dict()
        self.assertEqual(data["query"], "install firefox")
        self.assertTrue(data["context"]["execute"] is True)
        self.assertEqual(data["context"]["personality"], "minimal")
        self.assertIn("timestamp", data)
        
        # From dict
        req2 = Request.from_dict(data)
        self.assertEqual(req2.query, req.query)
        self.assertEqual(req2.context.execute, req.context.execute)
        self.assertEqual(req2.context.personality, req.context.personality)
    
    def test_intent_creation(self):
        """Test Intent creation"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.95
        )
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(intent.entities["package"], "firefox")
        self.assertEqual(intent.confidence, 0.95)
    
    def test_execution_result(self):
        """Test ExecutionResult"""
        result = ExecutionResult(
            success=True,
            output="Package installed successfully",
            exit_code=0,
            duration=1.5
        )
        self.assertTrue(result.success is True)
        self.assertEqual(result.output, "Package installed successfully")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.duration, 1.5)
    
    def test_plan_creation(self):
        """Test Plan creation"""
        plan = Plan(
            steps=["Update channels", "Install package"],
            commands=[{"cmd": "nix-channel --update"}, {"cmd": "nix-env -iA firefox"}],
            requires_sudo=False,
            is_destructive=False,
            estimated_duration=30.0
        )
        self.assertEqual(len(plan.steps), 2)
        self.assertEqual(len(plan.commands), 2)
        self.assertTrue(plan.requires_sudo is False)
    
    def test_response_creation(self):
        """Test Response creation"""
        # Simple response
        resp = Response(
            success=True,
            text="Firefox has been installed successfully"
        )
        self.assertTrue(resp.success is True)
        self.assertEqual(resp.text, "Firefox has been installed successfully")
        self.assertEqual(resp.commands, [])
        self.assertEqual(resp.suggestions, [])
        
        # Complex response with all fields
        intent = Intent(type=IntentType.INSTALL_PACKAGE, entities={"package": "firefox"})
        plan = Plan(steps=["Install firefox"])
        result = ExecutionResult(success=True, output="Done")
        
        resp = Response(
            success=True,
            text="Installing Firefox",
            intent=intent,
            plan=plan,
            result=result,
            suggestions=["You can launch Firefox with 'firefox' command"],
            explanation="Firefox is a popular web browser"
        )
        self.assertEqual(resp.intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(resp.plan.steps[0], "Install firefox")
        self.assertTrue(resp.result.success is True)
        self.assertEqual(len(resp.suggestions), 1)
    
    def test_response_serialization(self):
        """Test Response to/from dict"""
        intent = Intent(type=IntentType.INSTALL_PACKAGE, entities={"package": "firefox"})
        plan = Plan(steps=["Install firefox"], requires_sudo=False)
        result = ExecutionResult(success=True, output="Done", exit_code=0)
        
        resp = Response(
            success=True,
            text="Firefox installed",
            intent=intent,
            plan=plan,
            result=result,
            suggestions=["Launch with 'firefox'"],
            explanation="Firefox is a web browser"
        )
        
        # To dict
        data = resp.to_dict()
        self.assertTrue(data["success"] is True)
        self.assertEqual(data["text"], "Firefox installed")
        self.assertEqual(data["intent"]["type"], "install_package")
        self.assertEqual(data["plan"]["steps"][0], "Install firefox")
        self.assertTrue(data["result"]["success"] is True)
        self.assertEqual(len(data["suggestions"]), 1)
        
        # From dict
        resp2 = Response.from_dict(data)
        self.assertEqual(resp2.success, resp.success)
        self.assertEqual(resp2.text, resp.text)
        self.assertEqual(resp2.intent.type, resp.intent.type)
        self.assertEqual(resp2.plan.steps, resp.plan.steps)
        self.assertEqual(resp2.result.success, resp.result.success)
    
    def test_command_type(self):
        """Test Command type"""
        cmd = Command(
            command="nix-env",
            args=["-iA", "nixpkgs.firefox"],
            requires_sudo=False,
            description="Install Firefox"
        )
        self.assertEqual(cmd.command, "nix-env")
        self.assertEqual(len(cmd.args), 2)
        self.assertEqual(cmd.description, "Install Firefox")
    
    def test_package_type(self):
        """Test Package type"""
        pkg = Package(
            name="firefox",
            attribute="nixpkgs.firefox",
            version="121.0",
            description="Mozilla Firefox web browser",
            installed=False
        )
        self.assertEqual(pkg.name, "firefox")
        self.assertEqual(pkg.attribute, "nixpkgs.firefox")
        self.assertEqual(pkg.version, "121.0")
        self.assertTrue(pkg.installed is False)
    
    def test_feedback_item(self):
        """Test FeedbackItem type"""
        feedback = FeedbackItem(
            response_id="resp-123",
            helpful=True,
            comment="Very clear explanation"
        )
        self.assertEqual(feedback.response_id, "resp-123")
        self.assertTrue(feedback.helpful is True)
        self.assertEqual(feedback.comment, "Very clear explanation")
        self.assertTrue(isinstance(feedback.timestamp, datetime))

if __name__ == "__main__":
    unittest.main()
