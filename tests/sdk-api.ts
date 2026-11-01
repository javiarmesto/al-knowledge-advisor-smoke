// Compile-time compatibility check against the pinned SDK; no model calls.
import { CopilotClient, type SessionConfig, type Tool, type ToolInvocation } from "@github/copilot-sdk";
const tool: Tool = {
  name: "smoke_read", description: "bounded read", defer: "never", skipPermission: true,
  parameters: { type: "object", properties: { path: { type: "string" } }, required: ["path"] },
  handler: (_args: unknown, invocation: ToolInvocation) => {
    const agent: string | undefined = invocation.agentId;
    return { resultType: "success", textResultForLlm: agent || "" };
  }
};
const config: SessionConfig = {
  sessionId: "test", model: "explicit-at-runtime", workingDirectory: ".",
  enableConfigDiscovery: false, enableFileHooks: false, streaming: true,
  infiniteSessions: { enabled: false }, largeOutput: { enabled: false },
  pluginDirectories: ["./.deps/bcquality"], skillDirectories: ["./.deps/bcquality/skills"],
  availableTools: ["task", tool.name], tools: [tool], defaultAgent: { excludedTools: [tool.name] },
  customAgents: [{ name: "al-knowledge-advisor", prompt: "fixture", tools: [tool.name], skills: ["al-knowledge"] }],
  sessionLimits: { maxAiCredits: 5 },
  onPermissionRequest: () => ({ kind: "reject", feedback: "read-only" }),
  onEvent: event => { void event.agentId; }
};
const client = new CopilotClient({
  mode: "empty", workingDirectory: ".", baseDirectory: "./output/runtime",
  builtinPluginDirectories: ["./.deps/bcquality"], useLoggedInUser: true, logLevel: "error"
});
async function apiCheck() {
  await client.start();
  const auth = await client.getAuthStatus(); void auth.isAuthenticated;
  const status = await client.getStatus(); void status;
  const models = await client.listModels(); void models[0]?.id;
  const session = await client.createSession(config);
  await session.sendAndWait({ prompt: "test" }, 1000);
  await session.abort();
  await session.disconnect();
  await client.stop();
}
void apiCheck; // Deliberately never invoked in offline CI.
