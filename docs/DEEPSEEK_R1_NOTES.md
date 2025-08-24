# 🧠 DeepSeek-R1 Integration Notes

## ⚠️ Known Issues

### CPU Usage Problem
DeepSeek-R1:8b has a tendency to get stuck at 100% CPU usage even after completing a request. This can block other models from running.

**Symptoms:**
- `ollama ps` shows deepseek-r1:8b at 100% CPU indefinitely
- Other models timeout when trying to run
- System becomes sluggish

**Workarounds:**
1. **Manual cleanup after use:**
   ```bash
   ollama stop deepseek-r1:8b
   ```

2. **Use timeout wrapper:**
   ```python
   # Always use a timeout when invoking DeepSeek-R1
   result = subprocess.run(
       ['ollama', 'run', 'deepseek-r1:8b'],
       input=prompt,
       timeout=60,  # Force kill after 1 minute
       ...
   )
   ```

3. **Alternative for Sacred Council:**
   - Consider using `qwen3:8b` as the Mind instead
   - It's more stable and doesn't have the CPU issue

## ✨ Strengths

Despite the CPU issue, DeepSeek-R1 offers unique capabilities:

1. **Transparent Reasoning**: Shows its thinking process
2. **Self-Correction**: Can identify and fix its own mistakes
3. **Chain-of-Thought**: Excellent for complex reasoning tasks

## 📝 Recommendations

### For Production Use:
- **Prefer qwen3:8b** for the Mind role in Sacred Council
- Use DeepSeek-R1 only for specific reasoning tasks that need transparency
- Always implement timeouts and cleanup

### For Testing:
- Great for demonstrating transparent AI reasoning
- Use with caution and always monitor CPU usage
- Have cleanup scripts ready

## 🔧 Configuration Updates

To use qwen3:8b as default Mind instead:

```python
# In model_dispatcher.py _configure_sacred_council()
if 'qwen3:8b' in installed_models:
    council['mind'] = 'qwen3-8b'  # More stable
elif 'deepseek-r1:8b' in installed_models:
    council['mind'] = 'deepseek-r1-8b'  # Use as fallback
```

---

*Note: This is a temporary issue that may be resolved in future Ollama or DeepSeek-R1 updates.*