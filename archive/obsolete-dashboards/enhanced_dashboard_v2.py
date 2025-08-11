#!/usr/bin/env python3
"""
Enhanced AI Factory Dashboard with improved UI
- Two-column layout for personas
- Single toggle button for Start/Stop Factory
"""

import asyncio
import json
import logging
from aiohttp import web
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Factory state
factory_running = False

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
        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
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
        .btn-logs { background: #3b82f6; color: white; }
        button:hover { transform: translateY(-1px); box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        
        .factory-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-left: 20px;
            padding: 6px 12px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            font-size: 0.9em;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-dot.running { background: #22c55e; }
        .status-dot.stopped { background: #ef4444; animation: none; }
        
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
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-idle { background: #666; }
        .status-working { background: #3b82f6; animation: pulse 2s infinite; }
        .status-completed { background: #22c55e; }
        .status-error { background: #ef4444; }
        .status-blocked { background: #f59e0b; }
        
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
        }
        .log-entry {
            padding: 3px 0;
            border-bottom: 1px solid #222;
        }
        .log-entry.error { color: #ef4444; }
        .log-entry.warning { color: #f59e0b; }
        .log-entry.info { color: #3b82f6; }
        .log-entry.debug { color: #666; }
        .log-entry.success { color: #22c55e; }
        
        .output-item {
            background: #1a1a1a;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #333;
        }
        .code-block {
            background: #0a0a0a;
            padding: 10px;
            border-radius: 3px;
            margin-top: 5px;
            font-family: monospace;
            overflow-x: auto;
        }
        
        .filter-bar {
            margin-bottom: 10px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        select {
            background: #2a2a2a;
            color: #e0e0e0;
            border: 1px solid #333;
            padding: 5px 10px;
            border-radius: 3px;
        }
    </style>
    <script>
        let selectedPersona = null;
        let dashboardData = null;
        let logFilter = 'all';
        let factoryRunning = false;
        
        async function updateDashboard() {
            try {
                const response = await fetch('/api/dashboard-data');
                const data = await response.json();
                dashboardData = data;
                factoryRunning = data.factory_status === 'running';
                
                // Update factory status indicator
                updateFactoryStatus();
                
                // Update stats
                document.getElementById('totalWorkItems').textContent = data.stats.total_work_items;
                document.getElementById('activePersonas').textContent = data.stats.active_personas;
                document.getElementById('completedTasks').textContent = data.stats.completed_tasks;
                document.getElementById('systemUptime').textContent = data.stats.system_uptime;
                
                // Update personas
                updatePersonaList(data.personas);
                
                // Update selected persona details
                if (selectedPersona && data.personas[selectedPersona]) {
                    updatePersonaDetails(selectedPersona, data.personas[selectedPersona]);
                }
                
                // Update system logs if viewing
                if (!selectedPersona && document.getElementById('systemLogs')) {
                    updateSystemLogs(data.system_logs);
                }
                
                // Update connection status
                document.getElementById('connectionStatus').innerHTML = 
                    '🟢 Connected';
            } catch (error) {
                document.getElementById('connectionStatus').innerHTML = 
                    '🔴 Disconnected';
            }
        }
        
        function updateFactoryStatus() {
            const btn = document.getElementById('toggleBtn');
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (factoryRunning) {
                btn.textContent = '⏹️ Stop Factory';
                btn.className = 'btn-toggle stop';
                statusDot.className = 'status-dot running';
                statusText.textContent = 'Running';
            } else {
                btn.textContent = '▶️ Start Factory';
                btn.className = 'btn-toggle';
                statusDot.className = 'status-dot stopped';
                statusText.textContent = 'Stopped';
            }
        }
        
        async function toggleFactory() {
            if (factoryRunning) {
                await stopFactory();
            } else {
                await startFactory();
            }
        }
        
        async function startFactory() {
            try {
                await fetch('/api/start-factory', { method: 'POST' });
                factoryRunning = true;
                updateFactoryStatus();
            } catch (error) {
                console.error('Failed to start factory:', error);
            }
        }
        
        async function stopFactory() {
            try {
                await fetch('/api/stop-factory', { method: 'POST' });
                factoryRunning = false;
                updateFactoryStatus();
            } catch (error) {
                console.error('Failed to stop factory:', error);
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
                        ${data.state.current_task || 'Idle'}
                    </div>
                `;
                
                container.appendChild(div);
            });
        }
        
        function selectPersona(personaId) {
            selectedPersona = personaId;
            updateDashboard();
        }
        
        function updatePersonaDetails(personaId, data) {
            const content = document.getElementById('mainContent');
            
            content.innerHTML = `
                <h2>${data.info.name} - ${data.info.role}</h2>
                <p><strong>Skills:</strong> ${data.info.skills}</p>
                <p><strong>Status:</strong> <span class="status-indicator status-${data.state.status}"></span> ${data.state.status}</p>
                <p><strong>Current Task:</strong> ${data.state.current_task || 'None'}</p>
                <p><strong>Work Items Completed:</strong> ${data.state.work_items_completed}</p>
                
                <h3>Recent Outputs</h3>
                <div class="outputs-section">
                    ${data.state.outputs_generated.map(output => `
                        <div class="output-item">
                            <strong>${output.type}:</strong> ${output.name}
                            ${output.preview ? `<div class="code-block">${output.preview}</div>` : ''}
                        </div>
                    `).join('') || '<p>No outputs generated yet</p>'}
                </div>
                
                <h3>Activity Log</h3>
                <div class="log-viewer" style="height: 300px;">
                    ${data.logs.map(log => `
                        <div class="log-entry ${log.level}">
                            [${new Date(log.timestamp).toLocaleTimeString()}] ${log.message}
                        </div>
                    `).join('') || '<p>No activity yet</p>'}
                </div>
            `;
        }
        
        function updateSystemLogs(logs) {
            const container = document.getElementById('systemLogs');
            if (!container) return;
            
            const filteredLogs = logFilter === 'all' 
                ? logs 
                : logs.filter(log => log.level === logFilter);
            
            container.innerHTML = filteredLogs.map(log => `
                <div class="log-entry ${log.level}">
                    [${new Date(log.timestamp).toLocaleTimeString()}] ${log.message}
                </div>
            `).join('') || '<p>No logs available</p>';
            
            // Auto-scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        function showSystemLogs() {
            selectedPersona = null;
            document.querySelectorAll('.persona-card').forEach(el => el.classList.remove('selected'));
            
            const content = document.getElementById('mainContent');
            content.innerHTML = `
                <h2>System Logs</h2>
                <div class="filter-bar">
                    <label>Filter:</label>
                    <select onchange="logFilter = this.value; updateDashboard()">
                        <option value="all">All</option>
                        <option value="error">Errors</option>
                        <option value="warning">Warnings</option>
                        <option value="info">Info</option>
                        <option value="debug">Debug</option>
                        <option value="success">Success</option>
                    </select>
                </div>
                <div class="log-viewer" id="systemLogs" style="height: 600px;"></div>
            `;
            
            updateDashboard();
        }
        
        // Start updates
        setInterval(updateDashboard, 2000);
        updateDashboard();
        
        // Show system logs by default
        window.onload = () => showSystemLogs();
    </script>
</head>
<body>
    <div class="header">
        <h1>🏭 AI Factory Control Center</h1>
        <div class="controls">
            <button id="toggleBtn" class="btn-toggle" onclick="toggleFactory()">▶️ Start Factory</button>
            <button class="btn-logs" onclick="showSystemLogs()">📋 System Logs</button>
            <div class="factory-status">
                <span class="status-dot stopped" id="statusDot"></span>
                <span id="statusText">Stopped</span>
            </div>
            <span id="connectionStatus" style="margin-left: 20px; font-size: 0.9em;"></span>
        </div>
    </div>
    
    <div class="main-container">
        <div class="sidebar">
            <h3>Personas</h3>
            <div id="personaList" class="personas-grid"></div>
        </div>
        
        <div class="content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Work Items</div>
                    <div class="stat-value" id="totalWorkItems">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active Personas</div>
                    <div class="stat-value" id="activePersonas">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Completed Tasks</div>
                    <div class="stat-value" id="completedTasks">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">System Uptime</div>
                    <div class="stat-value" id="systemUptime">0h</div>
                </div>
            </div>
            
            <div id="mainContent">
                <!-- Dynamic content goes here -->
            </div>
        </div>
    </div>
</body>
</html>"""

async def index(request):
    """Serve the dashboard HTML"""
    return web.Response(text=HTML_TEMPLATE, content_type='text/html')

async def dashboard_data(request):
    """Return dashboard data as JSON"""
    global factory_running
    
    data = {
        "factory_status": "running" if factory_running else "stopped",
        "stats": {
            "total_work_items": 42,
            "active_personas": 5,
            "completed_tasks": 128,
            "system_uptime": "12h 34m"
        },
        "personas": {
            "dave": {
                "info": {
                    "name": "DaveBot",
                    "role": "Technical Lead",
                    "skills": "Architecture, Code Reviews, Technical Design"
                },
                "state": {
                    "status": "working",
                    "current_task": "Reviewing PR #1234",
                    "work_items_completed": 15,
                    "outputs_generated": []
                },
                "logs": []
            },
            "steve": {
                "info": {
                    "name": "SteveBot",
                    "role": "Security Architect",
                    "skills": "Security Design, Threat Modeling, Compliance"
                },
                "state": {
                    "status": "idle",
                    "current_task": None,
                    "work_items_completed": 23,
                    "outputs_generated": []
                },
                "logs": []
            },
            "kav": {
                "info": {
                    "name": "KavBot",
                    "role": "Security Test Engineer",
                    "skills": "Security Testing, Penetration Testing, SAST/DAST"
                },
                "state": {
                    "status": "completed",
                    "current_task": "Security scan completed",
                    "work_items_completed": 45,
                    "outputs_generated": []
                },
                "logs": []
            },
            "lachlan": {
                "info": {
                    "name": "LachlanBot",
                    "role": "DevSecOps Engineer",
                    "skills": "CI/CD, Infrastructure Security, Automation"
                },
                "state": {
                    "status": "working",
                    "current_task": "Updating security pipelines",
                    "work_items_completed": 31,
                    "outputs_generated": []
                },
                "logs": []
            },
            "jordan": {
                "info": {
                    "name": "JordanBot",
                    "role": "API Developer",
                    "skills": "REST APIs, GraphQL, Integration"
                },
                "state": {
                    "status": "idle",
                    "current_task": None,
                    "work_items_completed": 18,
                    "outputs_generated": []
                },
                "logs": []
            },
            "puck": {
                "info": {
                    "name": "PuckBot",
                    "role": "API Security Specialist",
                    "skills": "API Security, OAuth, JWT"
                },
                "state": {
                    "status": "idle",
                    "current_task": None,
                    "work_items_completed": 12,
                    "outputs_generated": []
                },
                "logs": []
            },
            "shaun": {
                "info": {
                    "name": "ShaunBot",
                    "role": "UI/UX Designer",
                    "skills": "UI Design, UX Research, Prototyping"
                },
                "state": {
                    "status": "working",
                    "current_task": "Designing security dashboard",
                    "work_items_completed": 9,
                    "outputs_generated": []
                },
                "logs": []
            },
            "matt": {
                "info": {
                    "name": "MattBot",
                    "role": "Frontend Developer",
                    "skills": "React, TypeScript, UI Implementation"
                },
                "state": {
                    "status": "idle",
                    "current_task": None,
                    "work_items_completed": 27,
                    "outputs_generated": []
                },
                "logs": []
            },
            "moby": {
                "info": {
                    "name": "MobyBot",
                    "role": "Database Architect",
                    "skills": "Database Design, SQL, Performance Tuning"
                },
                "state": {
                    "status": "idle",
                    "current_task": None,
                    "work_items_completed": 14,
                    "outputs_generated": []
                },
                "logs": []
            },
            "ruley": {
                "info": {
                    "name": "RuleyBot",
                    "role": "Requirements Analyst",
                    "skills": "Requirements Analysis, Documentation, Compliance"
                },
                "state": {
                    "status": "blocked",
                    "current_task": "Waiting for stakeholder input",
                    "work_items_completed": 8,
                    "outputs_generated": []
                },
                "logs": []
            },
            "brumbie": {
                "info": {
                    "name": "BrumbieBot",
                    "role": "Development Manager",
                    "skills": "Project Management, Sprint Planning, Team Coordination"
                },
                "state": {
                    "status": "working",
                    "current_task": "Sprint planning for next iteration",
                    "work_items_completed": 6,
                    "outputs_generated": []
                },
                "logs": []
            },
            "claude": {
                "info": {
                    "name": "ClaudeBot",
                    "role": "AI Assistant",
                    "skills": "Code Generation, Problem Solving, Documentation"
                },
                "state": {
                    "status": "idle",
                    "current_task": None,
                    "work_items_completed": 52,
                    "outputs_generated": []
                },
                "logs": []
            },
            "laureen": {
                "info": {
                    "name": "LaureenBot",
                    "role": "QA Engineer",
                    "skills": "Test Planning, Test Automation, Quality Assurance"
                },
                "state": {
                    "status": "error",
                    "current_task": "Test suite failed",
                    "work_items_completed": 33,
                    "outputs_generated": []
                },
                "logs": []
            }
        },
        "system_logs": [
            {"timestamp": datetime.now().isoformat(), "level": "info", "message": "Dashboard requested"},
            {"timestamp": datetime.now().isoformat(), "level": "success", "message": "All systems operational"}
        ]
    }
    
    return web.json_response(data)

async def start_factory(request):
    """Start the AI factory"""
    global factory_running
    factory_running = True
    logger.info("Factory started")
    return web.json_response({"status": "success", "message": "Factory started"})

async def stop_factory(request):
    """Stop the AI factory"""
    global factory_running
    factory_running = False
    logger.info("Factory stopped")
    return web.json_response({"status": "success", "message": "Factory stopped"})

def create_app():
    """Create the web application"""
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/api/dashboard-data', dashboard_data)
    app.router.add_post('/api/start-factory', start_factory)
    app.router.add_post('/api/stop-factory', stop_factory)
    return app

async def main():
    """Main entry point"""
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 3000)
    
    logger.info("Starting Enhanced Dashboard v2 on http://localhost:3000")
    await site.start()
    
    # Keep the server running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == '__main__':
    asyncio.run(main())