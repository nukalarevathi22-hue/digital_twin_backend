# Render MCP Server for Copilot Chat

This MCP (Model Context Protocol) server allows you to manage your Render deployments directly from GitHub Copilot Chat in VS Code.

## Features

✅ **List all services** - See all your Render services  
✅ **Check service status** - Monitor deployment health  
✅ **View logs** - Read error messages and deployment logs  
✅ **Restart services** - Restart deployments on demand  
✅ **Update environment variables** - Change config without leaving Chat  
✅ **View deployment history** - Check past deploys  

---

## Setup

### 1. Get Your Render API Token

1. Go to: https://dashboard.render.com/account/api-tokens
2. Click **"Create API Token"**
3. Name it: `copilot-mcp`
4. Copy the token (you'll need it)

### 2. Configure VS Code

#### Option A: Using Cursor (Recommended for Cursor IDE)

If using Cursor AI IDE, add to `~/.cursor/rules/render-mcp.json`:

```json
{
  "mcpServers": {
    "render": {
      "command": "python",
      "args": ["/path/to/mcp_render_server.py"],
      "env": {
        "RENDER_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### Option B: Using VS Code with Claude Extension

1. Open VS Code settings: `Ctrl+,` (or Cmd+, on Mac)
2. Search: `MCP servers`
3. Add the configuration:

```json
{
  "render": {
    "command": "python",
    "args": ["mcp_render_server.py"],
    "env": {
      "RENDER_API_TOKEN": "your_token_here"
    }
  }
}
```

#### Option C: Global MCP Configuration

Copy `mcp-settings.json` to your global MCP config location:

- **Windows:** `%LOCALAPPDATA%\Cursor\mcp-settings.json`
- **Mac:** `~/.config/cursor/mcp-settings.json`
- **Linux:** `~/.config/cursor/mcp-settings.json`

Then edit and replace `YOUR_RENDER_API_TOKEN_HERE` with your actual token.

### 3. Install Dependencies

```powershell
pip install mcp requests
```

---

## Usage in Copilot Chat

### In Cursor or VS Code with Copilot:

**Example prompts:**

```
@render Check the status of my digital-twin-backend service
```

```
@render Show me the last 50 lines of logs for service [service-id]
```

```
@render Restart my digital-twin-backend service
```

```
@render Update FITBIT_CLIENT_ID to 23TV8Q in my service
```

```
@render List all my Render services
```

---

## Finding Your Service ID

1. Go to: https://dashboard.render.com
2. Click your service (e.g., `digital-twin-backend`)
3. The URL will be: `https://dashboard.render.com/services/srv-xxxxxxxxxxxxx`
4. The `srv-xxxxxxxxxxxxx` part is your **Service ID**

Or run in Copilot Chat:
```
@render List all my Render services
```

This will show all service IDs.

---

## Debugging Your Deployment

If your Render deployment failed:

1. **In Copilot Chat:**
   ```
   @render Get logs for my digital-twin-backend service and explain the error
   ```

2. **Copilot will:**
   - Fetch your logs
   - Identify the error
   - Suggest fixes
   - Help you update configurations

---

## Common Issues

### "RENDER_API_TOKEN not set"
- Check that your API token is set in the environment or MCP configuration
- Ensure it's not expired (regenerate if needed)

### "Service not found"
- Verify the service ID is correct
- Check it matches your Render dashboard

### "Permission denied"
- Your API token may not have the required permissions
- Regenerate the token and ensure it has full access

---

## Example: Debug a Failed Render Deployment

**In Copilot Chat:**

```
@render I deployed digital-twin-backend but it's not working. 
What are the latest errors in the logs?
```

**Copilot will:**
1. Fetch your service logs
2. Show you the error messages
3. Identify common issues (config, missing env vars, etc.)
4. Suggest fixes

---

## Security Best Practices

⚠️ **NEVER commit your API token** to GitHub!

- Add `RENDER_API_TOKEN` to `.gitignore`
- Use environment variables instead of hardcoding
- Use VS Code's built-in secret storage when available
- Rotate your token periodically

---

## More Info

- Render API Docs: https://render.com/docs/api
- MCP Protocol: https://modelcontextprotocol.io
