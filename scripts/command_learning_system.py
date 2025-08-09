# Import from the hyphenated file
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "command_learning_system_module", 
    os.path.join(os.path.dirname(__file__), "command-learning-system.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Export the class
CommandLearningSystem = module.CommandLearningSystem