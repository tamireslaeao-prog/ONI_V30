/*
 * ONI CORE LIBRARY - ASANA AUTOMATION
 * Version: 1.0 (Total Project Control)
 * 
 * Standardized High-Level Functions for Task & Project Management.
 * Usage: Import this module into your Node.js automation context.
 */

const ONI = ONI || {};

// ============================================================================
// MODULE: CORE UTILITIES
// ============================================================================
ONI.Core = {
    // Base API Configuration
    config: {
        baseURL: 'https://app.asana.com/api/1.0',
        token: null,
        defaultWorkspace: null
    },

    // Set Authentication Token
    SetToken: function(token) {
        this.config.token = token;
    },

    // Set Default Workspace
    SetWorkspace: function(workspaceGid) {
        this.config.defaultWorkspace = workspaceGid;
    },

    // Generic API Request Handler
    Request: async function(method, endpoint, data = null) {
        const url = `${this.config.baseURL}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Authorization': `Bearer ${this.config.token}`,
                'Content-Type': 'application/json'
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify({ data: data });
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`ONI.Core.Request Failed: ${error.message}`);
            return null;
        }
    },

    // Get Current User Info
    GetMe: async function() {
        return await this.Request('GET', '/users/me');
    }
};

// ============================================================================
// MODULE: WORKSPACE MANAGEMENT
// ============================================================================
ONI.Workspace = {
    // List All Workspaces
    List: async function() {
        return await ONI.Core.Request('GET', '/workspaces');
    },

    // Get Workspace Details
    Get: async function(workspaceGid) {
        return await ONI.Core.Request('GET', `/workspaces/${workspaceGid}`);
    },

    // Get All Users in Workspace
    GetUsers: async function(workspaceGid) {
        const ws = workspaceGid || ONI.Core.config.defaultWorkspace;
        return await ONI.Core.Request('GET', `/workspaces/${ws}/users`);
    },

    // Get All Teams
    GetTeams: async function(workspaceGid) {
        const ws = workspaceGid || ONI.Core.config.defaultWorkspace;
        return await ONI.Core.Request('GET', `/organizations/${ws}/teams`);
    }
};

// ============================================================================
// MODULE: PROJECT ENGINE
// ============================================================================
ONI.Project = {
    // Create New Project
    Create: async function(name, options = {}) {
        const ws = options.workspace || ONI.Core.config.defaultWorkspace;
        const projectData = {
            name: name,
            workspace: ws,
            color: options.color || 'light-green',
            notes: options.notes || '',
            public: options.public !== undefined ? options.public : true,
            layout: options.layout || 'list', // 'list', 'board', 'timeline', 'calendar'
            default_view: options.defaultView || 'list'
        };

        if (options.team) projectData.team = options.team;
        if (options.owner) projectData.owner = options.owner;

        return await ONI.Core.Request('POST', '/projects', projectData);
    },

    // Get Project Details
    Get: async function(projectGid) {
        return await ONI.Core.Request('GET', `/projects/${projectGid}`);
    },

    // Update Project
    Update: async function(projectGid, updates) {
        return await ONI.Core.Request('PUT', `/projects/${projectGid}`, updates);
    },

    // Delete Project
    Delete: async function(projectGid) {
        return await ONI.Core.Request('DELETE', `/projects/${projectGid}`);
    },

    // List All Projects in Workspace
    List: async function(workspaceGid) {
        const ws = workspaceGid || ONI.Core.config.defaultWorkspace;
        return await ONI.Core.Request('GET', `/workspaces/${ws}/projects`);
    },

    // Duplicate Project
    Duplicate: async function(projectGid, newName) {
        const endpoint = `/projects/${projectGid}/duplicate`;
        return await ONI.Core.Request('POST', endpoint, {
            name: newName,
            include: 'notes,members,forms'
        });
    },

    // Add Members to Project
    AddMembers: async function(projectGid, userGids) {
        const endpoint = `/projects/${projectGid}/addMembers`;
        return await ONI.Core.Request('POST', endpoint, {
            members: userGids
        });
    }
};

// ============================================================================
// MODULE: TASK ENGINE
// ============================================================================
ONI.Task = {
    // Create New Task
    Create: async function(name, options = {}) {
        const ws = options.workspace || ONI.Core.config.defaultWorkspace;
        const taskData = {
            name: name,
            workspace: ws,
            notes: options.notes || '',
            html_notes: options.htmlNotes || null,
            assignee: options.assignee || null,
            due_on: options.dueDate || null,
            due_at: options.dueTime || null,
            start_on: options.startDate || null
        };

        if (options.projects) taskData.projects = options.projects;
        if (options.tags) taskData.tags = options.tags;
        if (options.followers) taskData.followers = options.followers;
        if (options.parent) taskData.parent = options.parent; // For subtasks

        return await ONI.Core.Request('POST', '/tasks', taskData);
    },

    // Get Task Details
    Get: async function(taskGid) {
        return await ONI.Core.Request('GET', `/tasks/${taskGid}`);
    },

    // Update Task
    Update: async function(taskGid, updates) {
        return await ONI.Core.Request('PUT', `/tasks/${taskGid}`, updates);
    },

    // Delete Task
    Delete: async function(taskGid) {
        return await ONI.Core.Request('DELETE', `/tasks/${taskGid}`);
    },

    // Complete Task
    Complete: async function(taskGid) {
        return await this.Update(taskGid, { completed: true });
    },

    // Add Comment to Task
    AddComment: async function(taskGid, text) {
        const endpoint = `/tasks/${taskGid}/stories`;
        return await ONI.Core.Request('POST', endpoint, {
            text: text
        });
    },

    // Add Subtask
    AddSubtask: async function(parentTaskGid, name, options = {}) {
        options.parent = parentTaskGid;
        return await this.Create(name, options);
    },

    // Get All Subtasks
    GetSubtasks: async function(taskGid) {
        return await ONI.Core.Request('GET', `/tasks/${taskGid}/subtasks`);
    },

    // Add Attachment
    AddAttachment: async function(taskGid, fileUrl, fileName) {
        // Note: File upload requires multipart/form-data, not JSON
        // This is a simplified version
        const endpoint = `/tasks/${taskGid}/attachments`;
        return await ONI.Core.Request('POST', endpoint, {
            resource_subtype: 'external',
            name: fileName,
            url: fileUrl
        });
    },

    // Search Tasks
    Search: async function(query, workspaceGid) {
        const ws = workspaceGid || ONI.Core.config.defaultWorkspace;
        const endpoint = `/workspaces/${ws}/tasks/search`;
        return await ONI.Core.Request('GET', `${endpoint}?text=${encodeURIComponent(query)}`);
    }
};

// ============================================================================
// MODULE: SECTION MANAGEMENT (for Board/List views)
// ============================================================================
ONI.Section = {
    // Create Section in Project
    Create: async function(projectGid, name) {
        const endpoint = `/projects/${projectGid}/sections`;
        return await ONI.Core.Request('POST', endpoint, {
            name: name
        });
    },

    // Get All Sections in Project
    List: async function(projectGid) {
        return await ONI.Core.Request('GET', `/projects/${projectGid}/sections`);
    },

    // Add Task to Section
    AddTask: async function(sectionGid, taskGid) {
        const endpoint = `/sections/${sectionGid}/addTask`;
        return await ONI.Core.Request('POST', endpoint, {
            task: taskGid
        });
    },

    // Move Section
    Move: async function(sectionGid, projectGid, insertBefore = null, insertAfter = null) {
        const endpoint = `/sections/${sectionGid}/move`;
        const data = { project: projectGid };
        if (insertBefore) data.insert_before = insertBefore;
        if (insertAfter) data.insert_after = insertAfter;
        return await ONI.Core.Request('POST', endpoint, data);
    }
};

// ============================================================================
// MODULE: TAG SYSTEM
// ============================================================================
ONI.Tag = {
    // Create Tag
    Create: async function(name, color, workspaceGid) {
        const ws = workspaceGid || ONI.Core.config.defaultWorkspace;
        return await ONI.Core.Request('POST', '/tags', {
            name: name,
            color: color || 'light-green',
            workspace: ws
        });
    },

    // List All Tags
    List: async function(workspaceGid) {
        const ws = workspaceGid || ONI.Core.config.defaultWorkspace;
        return await ONI.Core.Request('GET', `/workspaces/${ws}/tags`);
    },

    // Add Tag to Task
    AddToTask: async function(taskGid, tagGid) {
        const endpoint = `/tasks/${taskGid}/addTag`;
        return await ONI.Core.Request('POST', endpoint, {
            tag: tagGid
        });
    }
};

// ============================================================================
// MODULE: CUSTOM FIELDS
// ============================================================================
ONI.CustomField = {
    // Create Custom Field
    Create: async function(name, type, workspaceGid, options = {}) {
        const ws = workspaceGid || ONI.Core.config.defaultWorkspace;
        const fieldData = {
            name: name,
            resource_subtype: type, // 'text', 'number', 'enum', 'date'
            workspace: ws
        };

        if (type === 'enum' && options.enumOptions) {
            fieldData.enum_options = options.enumOptions;
        }
        if (options.precision) fieldData.precision = options.precision;

        return await ONI.Core.Request('POST', '/custom_fields', fieldData);
    },

    // Add Custom Field to Project
    AddToProject: async function(projectGid, customFieldGid) {
        const endpoint = `/projects/${projectGid}/addCustomFieldSetting`;
        return await ONI.Core.Request('POST', endpoint, {
            custom_field: customFieldGid
        });
    }
};

// ============================================================================
// MODULE: AUTOMATION TEMPLATES
// ============================================================================
ONI.Templates = {
    // Create Sprint Project
    CreateSprint: async function(sprintName, startDate, endDate, teamGid) {
        const project = await ONI.Project.Create(sprintName, {
            team: teamGid,
            layout: 'board',
            color: 'light-blue',
            notes: `Sprint: ${startDate} to ${endDate}`
        });

        if (!project || !project.data) return null;

        const projectGid = project.data.gid;

        // Create standard sections
        const sections = ['Backlog', 'To Do', 'In Progress', 'Review', 'Done'];
        for (const sectionName of sections) {
            await ONI.Section.Create(projectGid, sectionName);
        }

        return project;
    },

    // Create Marketing Campaign
    CreateCampaign: async function(campaignName, launchDate) {
        const project = await ONI.Project.Create(campaignName, {
            layout: 'timeline',
            color: 'light-pink',
            notes: `Launch Date: ${launchDate}`
        });

        if (!project || !project.data) return null;

        const projectGid = project.data.gid;

        // Create campaign phases as sections
        const phases = ['Planning', 'Content Creation', 'Design', 'Review', 'Launch'];
        for (const phase of phases) {
            await ONI.Section.Create(projectGid, phase);
        }

        return project;
    },

    // Bulk Create Tasks from Template
    BulkCreateTasks: async function(projectGid, taskTemplates) {
        const createdTasks = [];
        for (const template of taskTemplates) {
            const task = await ONI.Task.Create(template.name, {
                projects: [projectGid],
                assignee: template.assignee || null,
                dueDate: template.dueDate || null,
                notes: template.notes || ''
            });
            if (task && task.data) {
                createdTasks.push(task.data);
            }
        }
        return createdTasks;
    }
};

// ============================================================================
// MODULE: ANALYTICS & REPORTING
// ============================================================================
ONI.Analytics = {
    // Get Project Statistics
    GetProjectStats: async function(projectGid) {
        const tasks = await ONI.Core.Request('GET', `/projects/${projectGid}/tasks`);
        if (!tasks || !tasks.data) return null;

        const stats = {
            total: tasks.data.length,
            completed: tasks.data.filter(t => t.completed).length,
            incomplete: tasks.data.filter(t => !t.completed).length,
            overdue: 0,
            withAssignee: tasks.data.filter(t => t.assignee).length
        };

        stats.completionRate = stats.total > 0 
            ? ((stats.completed / stats.total) * 100).toFixed(2) 
            : 0;

        return stats;
    },

    // Get User Workload
    GetUserWorkload: async function(userGid, workspaceGid) {
        const ws = workspaceGid || ONI.Core.config.defaultWorkspace;
        const endpoint = `/tasks?assignee=${userGid}&workspace=${ws}&completed_since=now`;
        const tasks = await ONI.Core.Request('GET', endpoint);
        
        if (!tasks || !tasks.data) return null;

        return {
            totalTasks: tasks.data.length,
            tasksList: tasks.data
        };
    }
};

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ONI;
}