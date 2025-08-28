# AI Coding Instructions

## Code Formatting Guidelines

### NO Emojis in Code and Scripts
**DO NOT** use emojis in any code files, scripts, or technical documentation unless explicitly requested by the user.

**Rationale:**
- Emojis can cause encoding issues in terminal output (especially Windows)
- May not render properly in all environments
- Can interfere with parsing and automation tools
- Create compatibility issues across different systems and consoles

**Examples of what NOT to include:**
- ✅ ❌ 🤔 📋 💡 ⚡ 🔧 🚀 📝 🎯 💯 🔍 ⭐ 🎉 🛠️ 📊 ⚠️ ✨
- Any other Unicode emoji characters in print statements, log messages, or comments

**Use plain text alternatives instead:**
- Instead of ✅: "SUCCESS" or "COMPLETED"
- Instead of ❌: "ERROR" or "FAILED" 
- Instead of ⚠️: "Warning:" or "NOTICE"
- Instead of 📊: "Data:" or "Report"

## Error Handling Philosophy

### DO NOT Create Silent Failure Backups
When writing code that depends on external resources (files, scripts, services), **DO NOT** automatically implement fallback mechanisms that silently continue with reduced functionality.

**Examples of what NOT to do:**
- If a cleanup script is missing, don't fall back to basic cleanup commands
- If a configuration file is missing, don't fall back to hardcoded defaults  
- If a required dependency is unavailable, don't fall back to limited functionality
- If an API is unreachable, don't fall back to cached/stale data

### DO Follow Fail-Fast Principle
Instead of silent fallbacks, prefer **explicit error handling** that:
- **Fails immediately** when dependencies are missing
- **Provides clear error messages** explaining what went wrong
- **Gives specific instructions** on how to fix the issue
- **Exits with appropriate error codes** for automated systems

### When Fallbacks Might Be Justified
If you believe a fallback mechanism is truly necessary, **ASK EXPLICITLY**:

> "I'm implementing [feature X] which depends on [resource Y]. If [resource Y] is unavailable, I can either:
> 1. **Fail immediately** with a clear error message
> 2. **Implement a fallback** that does [specific behavior]
> 
> Which approach would you prefer?"

### Error Handling Best Practices
1. **Validate dependencies early** in the execution flow
2. **Use descriptive error messages** that include:
   - What went wrong
   - What was expected
   - How to fix it
3. **Log errors appropriately** for debugging
4. **Return meaningful exit codes** for automation
5. **Document error conditions** in comments

### Example Implementation
```bash
# Good: Fail fast with clear error
if [ ! -f "./required_script.sh" ]; then
    log_error "required_script.sh not found! Cannot proceed."
    log_error "Please ensure required_script.sh exists in: $(pwd)"
    exit 1
fi

# Bad: Silent fallback
if [ -f "./required_script.sh" ]; then
    ./required_script.sh
else
    echo "Using fallback cleanup..."
    # basic cleanup commands
fi
```

## Code Quality Guidelines

### Dependencies
- Always validate required files/scripts exist before using them
- Prefer explicit dependency checking over try-catch fallbacks
- Document all external dependencies clearly

### Logging
- Use structured logging with timestamps and severity levels
- Log both successful operations and failures
- Make logs useful for debugging and monitoring

### Configuration
- Validate configuration early in the application lifecycle
- Provide clear error messages for invalid configurations
- Don't guess or assume configuration values

## When in Doubt
If you're unsure whether to implement error handling or fallback behavior, **ask the user explicitly** rather than making assumptions about their preferred approach.
