#!/usr/bin/env python3
"""
AI Factory Dashboard with integrated API proxy
Serves dashboard and proxies API requests to avoid CORS issues
"""

import asyncio
import logging
from aiohttp import web, ClientSession
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API backend URL
API_BACKEND = "http://localhost:8080"

# HTML template with updated API path
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>AI Factory Control Center</title>
    <style>
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 0;
            background: #0a0a0a;
            color: #e0e0e0;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }
        h1 { margin: 0; font-size: 1.8em; }
        .real-api-badge {
            background: #22c55e;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-right: 50px;
        }
        button {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-toggle { 
            background: #22c55e; 
            color: white; 
            min-width: 120px;
        }
        .btn-toggle.stop { 
            background: #ef4444; 
        }
        .btn-add { background: #3b82f6; color: white; }
        .btn-logs { background: #6366f1; color: white; }
        button:hover { transform: translateY(-1px); box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        
        .factory-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-left: 20px;
            margin-right: 150px;
            padding: 5px 10px;
            background: rgba(0,0,0,0.7);
            border-radius: 4px;
            font-size: 0.8em;
        }
        
        .main-container {
            display: grid;
            grid-template-columns: 600px 1fr;
            height: calc(100vh - 60px);
        }
        
        .sidebar {
            background: #1a1a1a;
            border-right: 1px solid #333;
            overflow-y: auto;
            padding: 20px;
        }
        
        .personas-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .persona-card {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #333;
            cursor: pointer;
            transition: all 0.3s;
        }
        .persona-card:hover {
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(59, 130, 246, 0.2);
        }
        .persona-card.selected {
            border-color: #3b82f6;
            background: #1e3a5f;
        }
        .persona-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .persona-name {
            font-weight: bold;
            font-size: 1.1em;
        }
        .persona-role {
            color: #999;
            font-size: 0.9em;
            margin-top: 2px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            border: 2px solid transparent;
        }
        .status-idle { 
            background: #9ca3af; 
            border-color: #4b5563;
        }
        .status-working { 
            background: #3b82f6; 
            animation: pulse 2s infinite;
            border-color: #1d4ed8;
        }
        .status-error { 
            background: #ef4444;
            border-color: #dc2626;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .content {
            padding: 20px;
            overflow-y: auto;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #333;
        }
        .stat-label {
            color: #666;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #3b82f6;
            margin-top: 5px;
        }
        
        .log-viewer {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            overflow-y: auto;
            max-height: 600px;
        }
        .log-entry {
            padding: 3px 0;
            border-bottom: 1px solid #222;
        }
        .log-entry.error { color: #ef4444; }
        .log-entry.warning { color: #f59e0b; }
        .log-entry.info { color: #3b82f6; }
        .log-entry.success { color: #22c55e; }
        
        .work-item {
            background: #1a1a1a;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #333;
        }
        .work-item.pending { border-left: 3px solid #f59e0b; }
        .work-item.processing { border-left: 3px solid #3b82f6; }
        .work-item.completed { border-left: 3px solid #22c55e; }
        
        .add-work-form {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }
        input, select, textarea {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 4px;
            color: #e0e0e0;
        }
        .api-status {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 5px 10px;
            background: rgba(0,0,0,0.7);
            border-radius: 4px;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏭 AI Factory Control Center <span class="real-api-badge">REAL API</span></h1>
        <div class="controls">
            <button id="toggleBtn" class="btn-toggle" onclick="toggleFactory()">▶️ Start Factory</button>
            <button class="btn-add" onclick="showAddWorkItem()">➕ Add Work</button>
            <button class="btn-logs" onclick="showSystemLogs()">📋 System Logs</button>
            <div class="factory-status">
                Factory: <span id="statusText">❌ Stopped</span>
            </div>
        </div>
    </div>
    
    <div class="api-status" id="apiStatus">
        API: <span id="apiStatusText">Checking...</span>
    </div>
    
    <div class="main-container">
        <div class="sidebar">
            <h3>Personas</h3>
            <div id="personaList" class="personas-grid"></div>
        </div>
        
        <div class="content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Work Queue Size</div>
                    <div class="stat-value" id="workQueueSize">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active Personas</div>
                    <div class="stat-value" id="activePersonas">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Completed Items</div>
                    <div class="stat-value" id="completedItems">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">System Uptime</div>
                    <div class="stat-value" id="systemUptime">-</div>
                </div>
            </div>
            
            <div id="mainContent">
                <!-- Dynamic content -->
            </div>
        </div>
    </div>
    
    <script>
        let selectedPersona = null;
        let factoryRunning = false;
        
        async function fetchAPI(endpoint, options = {}) {
            try {
                // Use proxy endpoint
                const response = await fetch(`/proxy${endpoint}`, options);
                if (!response.ok) throw new Error(`API error: ${response.status}`);
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                document.getElementById('apiStatusText').innerHTML = '❌ Disconnected';
                throw error;
            }
        }
        
        async function updateDashboard() {
            try {
                // Get factory status
                const status = await fetchAPI('/api/status');
                factoryRunning = status.factory_running;
                
                // Update stats
                document.getElementById('workQueueSize').textContent = status.work_queue_size;
                document.getElementById('completedItems').textContent = status.completed_items;
                document.getElementById('systemUptime').textContent = status.uptime || '-';
                
                // Get personas
                const personas = await fetchAPI('/api/personas');
                updatePersonaList(personas);
                
                // Count active personas
                const activeCount = Object.values(personas).filter(p => p.state.status === 'working').length;
                document.getElementById('activePersonas').textContent = activeCount;
                
                // Update factory status
                updateFactoryStatus();
                
                // Update API status
                document.getElementById('apiStatusText').innerHTML = '🟢 Connected';
                
                // Update selected view
                if (selectedPersona && personas[selectedPersona]) {
                    showPersonaDetails(selectedPersona, personas[selectedPersona]);
                }
                
            } catch (error) {
                console.error('Dashboard update failed:', error);
            }
        }
        
        function updateFactoryStatus() {
            const btn = document.getElementById('toggleBtn');
            const statusText = document.getElementById('statusText');
            
            if (factoryRunning) {
                btn.textContent = '⏹️ Stop Factory';
                btn.className = 'btn-toggle stop';
                statusText.textContent = '🟢 Running';
            } else {
                btn.textContent = '▶️ Start Factory';
                btn.className = 'btn-toggle';
                statusText.textContent = '❌ Stopped';
            }
        }
        
        async function toggleFactory() {
            const endpoint = factoryRunning ? '/api/factory/stop' : '/api/factory/start';
            try {
                await fetchAPI(endpoint, { method: 'POST' });
                await updateDashboard();
            } catch (error) {
                alert('Failed to toggle factory: ' + error.message);
            }
        }
        
        function updatePersonaList(personas) {
            const container = document.getElementById('personaList');
            container.innerHTML = '';
            
            Object.entries(personas).forEach(([id, data]) => {
                const div = document.createElement('div');
                div.className = 'persona-card' + (id === selectedPersona ? ' selected' : '');
                div.onclick = () => selectPersona(id);
                
                div.innerHTML = `
                    <div class="persona-header">
                        <div>
                            <div class="persona-name">${data.info.name}</div>
                            <div class="persona-role">${data.info.role}</div>
                        </div>
                        <span class="status-indicator status-${data.state.status}"></span>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.85em; color: #666;">
                        ${data.state.status === 'working' ? 'Working on: ' + (data.state.current_work_item || 'Task') : 
                          'Completed: ' + data.state.work_items_completed + ' items'}
                    </div>
                `;
                
                container.appendChild(div);
            });
        }
        
        function selectPersona(personaId) {
            selectedPersona = personaId;
            updateDashboard();
        }
        
        async function showPersonaDetails(personaId, data) {
            const content = document.getElementById('mainContent');
            content.innerHTML = `
                <h2>${data.info.name} - ${data.info.role}</h2>
                <p><strong>Skills:</strong> ${data.info.skills}</p>
                <p><strong>Status:</strong> <span class="status-indicator status-${data.state.status}"></span> ${data.state.status}</p>
                <p><strong>Work Items Completed:</strong> ${data.state.work_items_completed}</p>
                ${data.state.current_work_item ? `<p><strong>Current Work:</strong> ${data.state.current_work_item}</p>` : ''}
                ${data.state.last_activity ? `<p><strong>Last Activity:</strong> ${new Date(data.state.last_activity).toLocaleString()}</p>` : ''}
            `;
        }
        
        async function showSystemLogs() {
            selectedPersona = null;
            document.querySelectorAll('.persona-card').forEach(el => el.classList.remove('selected'));
            
            try {
                const logs = await fetchAPI('/api/logs?limit=100');
                const content = document.getElementById('mainContent');
                
                content.innerHTML = `
                    <h2>System Logs</h2>
                    <div class="log-viewer">
                        ${logs.map(log => `
                            <div class="log-entry ${log.level}">
                                [${new Date(log.timestamp).toLocaleTimeString()}] ${log.message}
                            </div>
                        `).join('') || '<p>No logs available</p>'}
                    </div>
                `;
            } catch (error) {
                alert('Failed to load logs: ' + error.message);
            }
        }
        
        async function showAddWorkItem() {
            selectedPersona = null;
            document.querySelectorAll('.persona-card').forEach(el => el.classList.remove('selected'));
            
            const content = document.getElementById('mainContent');
            content.innerHTML = `
                <h2>Add Work Item</h2>
                <div class="add-work-form">
                    <input type="text" id="workTitle" placeholder="Work item title" />
                    <textarea id="workDescription" placeholder="Description" rows="3"></textarea>
                    <select id="workType">
                        <option value="feature">Feature</option>
                        <option value="bug">Bug Fix</option>
                        <option value="security">Security Review</option>
                        <option value="documentation">Documentation</option>
                        <option value="testing">Testing</option>
                    </select>
                    <button class="btn-add" onclick="submitWorkItem()">Add to Queue</button>
                </div>
                <h3>Current Work Queue</h3>
                <div id="workQueueList"></div>
            `;
            
            await loadWorkQueue();
        }
        
        async function loadWorkQueue() {
            try {
                const queue = await fetchAPI('/api/work-queue');
                const container = document.getElementById('workQueueList');
                
                container.innerHTML = queue.items.map(item => `
                    <div class="work-item ${item.status}">
                        <strong>${item.title || item.id}</strong>
                        <div style="font-size: 0.85em; color: #666;">
                            Status: ${item.status} | Created: ${new Date(item.created_at).toLocaleString()}
                            ${item.assigned_to ? ` | Assigned to: ${item.assigned_to}` : ''}
                        </div>
                    </div>
                `).join('') || '<p>No work items in queue</p>';
            } catch (error) {
                console.error('Failed to load work queue:', error);
            }
        }
        
        async function submitWorkItem() {
            const title = document.getElementById('workTitle').value;
            const description = document.getElementById('workDescription').value;
            const type = document.getElementById('workType').value;
            
            if (!title) {
                alert('Please enter a title');
                return;
            }
            
            try {
                await fetchAPI('/api/work-queue', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description, type })
                });
                
                // Clear form
                document.getElementById('workTitle').value = '';
                document.getElementById('workDescription').value = '';
                
                // Reload queue
                await loadWorkQueue();
                await updateDashboard();
                
            } catch (error) {
                alert('Failed to add work item: ' + error.message);
            }
        }
        
        // Start updates
        setInterval(updateDashboard, 2000);
        updateDashboard();
        
        // Show logs by default
        window.onload = () => showSystemLogs();
    </script>
</body>
</html>"""


async def index(request):
    """Serve the dashboard HTML"""
    return web.Response(text=HTML_TEMPLATE, content_type='text/html')


async def proxy_handler(request):
    """Proxy API requests to backend"""
    # Get the path after /proxy
    api_path = request.match_info.get('path', '')
    if request.rel_url.query_string:
        api_path += '?' + request.rel_url.query_string
    
    # Build backend URL
    backend_url = f"{API_BACKEND}/{api_path}"
    
    # Forward the request
    async with ClientSession() as session:
        # Prepare request data
        data = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            data = await request.read()
        
        # Forward headers (excluding host)
        headers = {}
        for key, value in request.headers.items():
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        
        # Make request to backend
        async with session.request(
            method=request.method,
            url=backend_url,
            headers=headers,
            data=data
        ) as response:
            # Get response body
            body = await response.read()
            
            # Return proxied response
            # Don't pass content_type if it's already in headers
            resp = web.Response(
                body=body,
                status=response.status
            )
            # Copy headers except Content-Length (aiohttp will set it)
            for key, value in response.headers.items():
                if key.lower() not in ['content-length', 'transfer-encoding']:
                    resp.headers[key] = value
            return resp


def create_app():
    """Create the web application"""
    app = web.Application()
    app.router.add_get('/', index)
    # Proxy all /proxy/* requests to the API backend
    app.router.add_route('*', '/proxy/{path:.*}', proxy_handler)
    return app


async def main():
    """Main entry point"""
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 3000)
    
    logger.info("Starting AI Factory Dashboard with API Proxy on http://localhost:3000")
    logger.info(f"Proxying API requests to {API_BACKEND}")
    await site.start()
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == '__main__':
    asyncio.run(main())