import { Tool, ToolSchema, ToolContext } from "@moltbot/types";
import axios from "axios";

// Configuration
const DEFAULT_GATEWAY = "http://localhost:8000/api/v1/gateway";

/**
 * Execute a desktop automation workflow via ONI
 */
const executeWorkflow: Tool = {
    name: "oni_execute_workflow",
    description: "Executes a complex desktop automation workflow (e.g. Photoshop render, Form filling) on the host machine.",
    schema: {
        type: "object",
        properties: {
            workflow: {
                type: "string",
                description: "Name of the workflow execution mode.",
                enum: [
                    "photoshop_open",
                    "photoshop_render",
                    "task_execute",       // General Autonomy (DeepReasoning)
                    "blender_execute",    // 3D Operations
                    "system_command",     // OS Control (Open App, Focus)
                    "ping"
                ]
            },
            params: {
                type: "object",
                description: "Parameters dependent on workflow. Examples:\n" +
                    "- photoshop_open: { path: 'C:/file.psd' }\n" +
                    "- task_execute: { description: 'Draw a red circle' }\n" +
                    "- blender_execute: { script_code: 'bpy.ops.mesh.primitive_cube_add()' } OR { file_path: 'C:/model.obj' }\n" +
                    "- system_command: { command: 'open_app', value: 'Notepad' }"
            }
        }, // End params
        required: ["workflow"]
    } // End properties
} // End schema
  }, // End Tool object
execute: async (args: any, context: ToolContext) => {
    const gatewayUrl = context.config?.gatewayUrl || "http://localhost:8000";
    const endpoint = `${gatewayUrl}/api/v1/gateway/execute`;

    try {
        console.log(`[ONI] Executing ${args.workflow} at ${endpoint}`);
        const response = await axios.post(endpoint, {
            workflow: args.workflow,
            params: args.params || {},
            description: `Moltbot executed ${args.workflow}`
        });

        return {
            content: [
                {
                    type: "text",
                    text: `Workflow Queued. Job ID: ${response.data.job_id}. Status: ${response.data.status}`
                }
            ]
        };
    } catch (error: any) {
        return {
            content: [
                {
                    type: "text",
                    text: `Error executing ONI workflow: ${error.message}`
                }
            ],
            isError: true
        };
    }
}
};

/**
 * Check Job Status
 */
const checkStatus: Tool = {
    name: "oni_check_status",
    description: "Checks the status of a running ONI automation job.",
    schema: {
        type: "object",
        properties: {
            job_id: { type: "string" }
        },
        required: ["job_id"]
    },
    execute: async (args: any, context: ToolContext) => {
        const gatewayUrl = context.config?.gatewayUrl || "http://localhost:8000";
        const endpoint = `${gatewayUrl}/api/v1/gateway/status/${args.job_id}`;

        try {
            const response = await axios.get(endpoint);
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(response.data, null, 2)
                    }
                ]
            };
        } catch (error: any) {
            return { isError: true, content: [{ type: "text text", text: error.message }] };
        }
    }
};

// Export Tools
export const tools = [executeWorkflow, checkStatus];
