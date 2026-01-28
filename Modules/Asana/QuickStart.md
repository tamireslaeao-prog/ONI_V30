# 🎯 ONI ASANA CONTROL SYSTEM
> **Version:** 1.0  
> **Status:** PRODUCTION READY

---

## 🌟 OVERVIEW
Complete automation framework for Asana project management with real-time monitoring, deep analytics, and template-based workflows.

---

## 📂 SYSTEM ARCHITECTURE

```
C:\ONI\Asana\
├── oni_lib_asana.js         # Core JavaScript Library (Node.js/Browser)
├── workspace_db.json         # Harvested workspace database
├── sentinel_log.txt          # Real-time change log
├── Scripts\
│   ├── ONI_Asana_Harvester.ps1   # Deep workspace scanner
│   ├── ONI_Asana_Sentinel.ps1    # Real-time monitor
│   └── ONI_Asana_Injector.ps1    # Bulk operations engine
└── Templates\
    ├── sprint_template.json
    ├── campaign_template.json
    └── onboarding_template.json
```

---

## 🔑 AUTHENTICATION SETUP

### Get Your Personal Access Token
1. Go to: **https://app.asana.com/0/my-apps**
2. Click **"Create New Personal Access Token"**
3. Name it: `ONI_Automation`
4. Copy the token

### Set Environment Variable (PowerShell)
```powershell
$env:ASANA_TOKEN = "your_token_here"

# To persist across sessions:
[System.Environment]::SetEnvironmentVariable('ASANA_TOKEN', 'your_token_here', 'User')
```

### Verify Connection
```powershell
$headers = @{ Authorization = "Bearer $env:ASANA_TOKEN" }
Invoke-RestMethod -Uri "https://app.asana.com/api/1.0/users/me" -Headers $headers
```

---

## 🚀 QUICK START

### 1. Harvest Your Workspace
```powershell
.\ONI_Asana_Harvester.ps1 -WorkspaceGid "123456789"
```

**What it does:**
- Scans ALL projects, tasks, users, tags, custom fields
- Creates comprehensive JSON database
- Generates statistics and analytics
- Maps entire workspace structure

**Output:** `workspace_db.json` with complete workspace snapshot

---

### 2. Start Real-Time Monitor
```powershell
.\ONI_Asana_Sentinel.ps1 -WorkspaceGid "123456789" -PollInterval 30
```

**What it monitors:**
- ✨ New projects created
- 📝 Project updates (name, archive status)
- ✅ Task completions
- 👤 New team members
- 🏷️ New tags created
- 🗑️ Deleted projects

**Auto-actions:**
- Updates `workspace_db.json` in real-time
- Logs all changes to `sentinel_log.txt`
- Triggers custom webhooks (configurable)

---

## 💻 JAVASCRIPT API USAGE

### Setup (Node.js)
```javascript
const ONI = require('./oni_lib_asana.js');

// Configure
ONI.Core.SetToken('your_asana_token');
ONI.Core.SetWorkspace('your_workspace_gid');

// Verify connection
const me = await ONI.Core.GetMe();
console.log(`Connected as: ${me.data.name}`);
```

### Create a Project
```javascript
const project = await ONI.Project.Create('Q1 Marketing Campaign', {
    color: 'light-pink',
    layout: 'board',  // 'list', 'board', 'timeline', 'calendar'
    notes: 'Campaign launching March 2026',
    public: true
});

console.log(`Project created: ${project.data.gid}`);
```

### Create Tasks in Bulk
```javascript
const tasks = [
    { name: 'Design landing page', assignee: 'user_gid_123', dueDate: '2026-02-15' },
    { name: 'Write ad copy', assignee: 'user_gid_456', dueDate: '2026-02-20' },
    { name: 'Set up analytics', assignee: 'user_gid_789', dueDate: '2026-02-25' }
];

const created = await ONI.Templates.BulkCreateTasks(project.data.gid, tasks);
console.log(`Created ${created.length} tasks`);
```

### Add Sections (Kanban Columns)
```javascript
const sections = ['To Do', 'In Progress', 'Review', 'Done'];

for (const sectionName of sections) {
    await ONI.Section.Create(project.data.gid, sectionName);
}
```

### Search Tasks
```javascript
const results = await ONI.Task.Search('urgent bug fix');
console.log(`Found ${results.data.length} tasks`);
```

### Get Project Analytics
```javascript
const stats = await ONI.Analytics.GetProjectStats(project.data.gid);
console.log(`Completion Rate: ${stats.completionRate}%`);
console.log(`Overdue Tasks: ${stats.overdue}`);
```

---

## 🎨 PRE-BUILT TEMPLATES

### Sprint Project
```javascript
const sprint = await ONI.Templates.CreateSprint(
    'Sprint 23 - Feb 2026',
    '2026-02-01',
    '2026-02-14',
    'team_gid_123'
);

// Auto-creates sections: Backlog, To Do, In Progress, Review, Done
```

### Marketing Campaign
```javascript
const campaign = await ONI.Templates.CreateCampaign(
    'Product Launch 2.0',
    '2026-03-15'
);

// Auto-creates phases: Planning, Content Creation, Design, Review, Launch
```

### Custom Template
```javascript
const tasks = [
    { name: 'Environment Setup', assignee: 'dev_1', dueDate: '2026-02-10' },
    { name: 'Database Migration', assignee: 'dev_2', dueDate: '2026-02-12' },
    { name: 'API Integration', assignee: 'dev_3', dueDate: '2026-02-15' }
];

await ONI.Templates.BulkCreateTasks('project_gid', tasks);
```

---

## 🔧 ADVANCED OPERATIONS

### Custom Fields
```javascript
// Create dropdown field
const priorityField = await ONI.CustomField.Create(
    'Priority',
    'enum',
    workspace_gid,
    {
        enumOptions: [
            { name: 'Low', color: 'green' },
            { name: 'Medium', color: 'yellow' },
            { name: 'High', color: 'red' }
        ]
    }
);

// Add to project
await ONI.CustomField.AddToProject(project_gid, priorityField.data.gid);
```

### Subtasks
```javascript
const parentTask = await ONI.Task.Create('Implement Payment System');

// Add subtasks
await ONI.Task.AddSubtask(parentTask.data.gid, 'Setup Stripe SDK');
await ONI.Task.AddSubtask(parentTask.data.gid, 'Create checkout flow');
await ONI.Task.AddSubtask(parentTask.data.gid, 'Add webhooks');

const subtasks = await ONI.Task.GetSubtasks(parentTask.data.gid);
console.log(`Total subtasks: ${subtasks.data.length}`);
```

### Tags
```javascript
// Create tag
const bugTag = await ONI.Tag.Create('Bug', 'red', workspace_gid);

// Apply to task
await ONI.Tag.AddToTask(task_gid, bugTag.data.gid);
```

### Comments
```javascript
await ONI.Task.AddComment(
    task_gid,
    'Updated design files uploaded to Figma. @john please review.'
);
```

---

## 📊 ANALYTICS & REPORTING

### Project Health Dashboard
```javascript
const stats = await ONI.Analytics.GetProjectStats(project_gid);

console.log('PROJECT HEALTH REPORT');
console.log('═══════════════════════');
console.log(`Total Tasks:      ${stats.total}`);
console.log(`Completed:        ${stats.completed}`);
console.log(`In Progress:      ${stats.incomplete}`);
console.log(`Completion Rate:  ${stats.completionRate}%`);
console.log(`With Assignee:    ${stats.withAssignee}`);
```

### User Workload
```javascript
const workload = await ONI.Analytics.GetUserWorkload(user_gid);

console.log(`${user.name} has ${workload.totalTasks} active tasks`);
```

### Team Performance (Custom)
```javascript
// Get all users
const users = await ONI.Workspace.GetUsers(workspace_gid);

// Calculate workload for each
for (const user of users.data) {
    const load = await ONI.Analytics.GetUserWorkload(user.gid);
    console.log(`${user.name}: ${load.totalTasks} tasks`);
}
```

---

## 🎭 USE CASES

### 1. Automated Sprint Planning
```javascript
// Create sprint
const sprint = await ONI.Templates.CreateSprint('Sprint 24', '2026-02-15', '2026-02-28', team_gid);

// Import backlog items
const backlogTasks = await ONI.Task.Search('backlog priority:high');

// Move to sprint
for (const task of backlogTasks.data.slice(0, 10)) {
    await ONI.Task.Update(task.gid, { 
        projects: [sprint.data.gid],
        due_on: '2026-02-28'
    });
}
```

### 2. Automated Daily Standup Report
```javascript
const today = new Date().toISOString().split('T')[0];

// Get completed tasks today
const completed = await ONI.Core.Request('GET', 
    `/tasks?completed_since=${today}&workspace=${workspace_gid}`
);

// Generate report
console.log('DAILY STANDUP REPORT');
console.log(`Completed: ${completed.data.length} tasks`);
for (const task of completed.data) {
    console.log(`- ${task.name} by ${task.assignee?.name}`);
}
```

### 3. Automated Onboarding
```javascript
async function onboardNewEmployee(employeeName, assigneeGid) {
    const project = await ONI.Project.Create(`Onboarding - ${employeeName}`);
    
    const tasks = [
        { name: 'Setup workspace access', dueDate: '+1d' },
        { name: 'Complete HR paperwork', dueDate: '+2d' },
        { name: 'Attend orientation', dueDate: '+3d' },
        { name: 'Meet with manager', dueDate: '+5d' }
    ];
    
    for (const t of tasks) {
        await ONI.Task.Create(t.name, {
            projects: [project.data.gid],
            assignee: assigneeGid,
            dueDate: calculateDate(t.dueDate)
        });
    }
}
```

---

## 🔔 WEBHOOK INTEGRATION (Future)

```javascript
// Setup webhook listener
ONI.Webhooks.Register({
    resource: project_gid,
    target: 'https://your-domain.com/asana-webhook',
    events: ['task.completed', 'task.created']
});

// Handle webhook
app.post('/asana-webhook', (req, res) => {
    const event = req.body.events[0];
    
    if (event.action === 'changed' && event.resource.completed) {
        console.log(`Task completed: ${event.resource.name}`);
        // Trigger celebration animation, send notification, etc.
    }
});
```

---

## 🎯 BEST PRACTICES

### 1. Rate Limiting
Asana API limits: **1500 requests/minute**
```javascript
// Use batch operations
await ONI.Templates.BulkCreateTasks(project_gid, tasks);
// Instead of individual creates
```

### 2. Error Handling
```javascript
try {
    const project = await ONI.Project.Create('My Project');
} catch (error) {
    console.error('Failed:', error.message);
    // Implement retry logic
}
```

### 3. Caching
```javascript
// Cache workspace users (they don't change often)
let cachedUsers = null;

async function getUsers() {
    if (!cachedUsers) {
        cachedUsers = await ONI.Workspace.GetUsers();
    }
    return cachedUsers;
}
```

---

## 🔐 SECURITY NOTES

- **Never commit** your Personal Access Token to git
- Use environment variables: `process.env.ASANA_TOKEN`
- Rotate tokens every 90 days
- Use separate tokens for dev/staging/production
- Limit token scope to only required permissions

---

## 🚨 TROUBLESHOOTING

### "Unauthorized" Error
```
Solution: Verify token is correct and not expired
Test: curl -H "Authorization: Bearer YOUR_TOKEN" https://app.asana.com/api/1.0/users/me
```

### "Forbidden" Error
```
Solution: Check if you have permission to access that workspace/project
```

### Sentinel Not Detecting Changes
```
Solution: Increase poll interval (API caching)
Check: Verify workspace_gid is correct
```

---

## 📚 ADDITIONAL RESOURCES

- **Asana API Docs:** https://developers.asana.com/docs
- **ONI Support:** (Your internal channel)
- **Rate Limits:** https://developers.asana.com/docs/rate-limits

---

## 🎉 READY TO USE!

```powershell
# 1. Set your token
$env:ASANA_TOKEN = "your_token"

# 2. Harvest workspace
.\ONI_Asana_Harvester.ps1

# 3. Start monitoring
.\ONI_Asana_Sentinel.ps1 -PollInterval 30

# 4. Build something amazing with oni_lib_asana.js
```

**System Status:** ✅ OPERATIONAL