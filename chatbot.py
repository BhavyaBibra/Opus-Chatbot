import streamlit as st
import streamlit.components.v1 as components

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Claude 4.5 Opus — Chat",
    layout="centered"
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💬 Claude 4.5 Opus — Chat")
st.caption("Free via Puter · ChatGPT-style UI")

# ---------------- HTML / JS App ----------------
components.html(
"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://js.puter.com/v2/"></script>

  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

  <link rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github.min.css">
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/build/highlight.min.js"></script>

  <style>
    * { box-sizing: border-box; }

    :root {
      --bg: #ffffff;
      --bg-soft: #fafafa;
      --text: #111;
      --border: #e5e5e5;
      --assistant-bg: #ffffff;
      --user-bg: #dcf8c6;
      --code-bg: #f6f8fa;
      --accent: #10a37f;
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #0f1115;
        --bg-soft: #161a22;
        --text: #eaeaea;
        --border: #2a2f3a;
        --assistant-bg: #161a22;
        --user-bg: #1f6f5c;
        --code-bg: #1c1f26;
        --accent: #10a37f;
      }
    }

    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont;
      background: var(--bg-soft);
      color: var(--text);
    }

    .chat-wrapper {
      display: flex;
      flex-direction: column;
      height: calc(100vh - 120px);
      max-height: 860px;
      border-radius: 14px;
      overflow: hidden;
      border: 1px solid var(--border);
      background: var(--bg);
    }

    .chat {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      scroll-behavior: smooth;
    }

    .msg {
      max-width: 75%;
      padding: 12px 14px;
      margin-bottom: 14px;
      border-radius: 14px;
      line-height: 1.45;
      word-wrap: break-word;
      transition: background 0.15s ease, border 0.15s ease;
    }

    .user {
      background: var(--user-bg);
      margin-left: auto;
      border-bottom-right-radius: 4px;
      white-space: pre-wrap;
    }

    .assistant {
      background: var(--assistant-bg);
      border: 1px solid var(--border);
      margin-right: auto;
      border-bottom-left-radius: 4px;
    }

    .assistant .markdown pre {
      background: var(--code-bg);
      padding: 12px;
      border-radius: 8px;
      overflow-x: auto;
    }

    .assistant .markdown table {
      border-collapse: collapse;
      width: 100%;
      margin-top: 8px;
    }

    .assistant .markdown th,
    .assistant .markdown td {
      border: 1px solid var(--border);
      padding: 6px 8px;
    }

    .assistant .markdown th {
      background: var(--bg-soft);
    }

    .input-bar {
      display: flex;
      gap: 10px;
      padding: 14px;
      border-top: 1px solid var(--border);
      background: var(--bg-soft);
    }

    textarea {
      flex: 1;
      resize: none;
      border-radius: 10px;
      border: 1px solid var(--border);
      padding: 10px 12px;
      font-size: 14px;
      height: 44px;
      outline: none;
      background: var(--bg);
      color: var(--text);
    }

    textarea:focus {
      border-color: var(--accent);
    }

    button {
      border: none;
      background: var(--accent);
      color: white;
      padding: 0 16px;
      border-radius: 10px;
      font-size: 14px;
      cursor: pointer;
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    #resetBtn {
      background: transparent;
      color: var(--text);
      border: 1px solid var(--border);
    }

    #resetBtn:hover {
      background: var(--bg-soft);
    }

    .status {
      font-size: 12px;
      color: #888;
      padding: 6px 14px;
    }

    .error {
      color: red;
      font-size: 12px;
      padding: 6px 14px;
      white-space: pre-wrap;
    }
  </style>
</head>

<body>
  <div class="chat-wrapper">
    <div id="chat" class="chat"></div>

    <div class="status" id="status">Initializing…</div>
    <div class="error" id="error"></div>

    <div class="input-bar">
      <textarea id="prompt"
        placeholder="Send a message…"
        onkeydown="handleKey(event)"></textarea>
      <button id="resetBtn" onclick="resetChat()">Reset</button>
      <button id="sendBtn" onclick="send()">Send</button>
    </div>
  </div>

<script>
const chatEl = document.getElementById("chat");
const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");
const sendBtn = document.getElementById("sendBtn");

const conversation = [];

function addUserMessage(text) {
  const div = document.createElement("div");
  div.className = "msg user";
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function addAssistantMessage() {
  const div = document.createElement("div");
  div.className = "msg assistant";
  div.innerHTML = "<div class='markdown'></div>";
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div.querySelector(".markdown");
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
}

function resetChat() {
  chatEl.innerHTML = "";
  conversation.length = 0;
  statusEl.textContent = "Ready";
  errorEl.textContent = "";
}

function waitForPuter() {
  return new Promise((resolve, reject) => {
    let tries = 0;
    const timer = setInterval(() => {
      tries++;
      if (window.puter?.ai && window.puter?.auth) {
        clearInterval(timer);
        resolve();
      }
      if (tries > 50) {
        clearInterval(timer);
        reject("Puter SDK failed to load");
      }
    }, 100);
  });
}

async function ensureAuth() {
  await waitForPuter();
  if (!puter.auth.isSignedIn()) {
    statusEl.textContent = "Signing in…";
    await puter.auth.signIn();
  }
  statusEl.textContent = "Ready";
}

async function send() {
  errorEl.textContent = "";
  const promptEl = document.getElementById("prompt");
  const prompt = promptEl.value.trim();
  if (!prompt) return;

  promptEl.value = "";
  sendBtn.disabled = true;

  addUserMessage(prompt);
  conversation.push({ role: "user", content: prompt });

  if (conversation.length > 20) {
    conversation.splice(0, 2);
  }

  const markdownEl = addAssistantMessage();
  let renderBuffer = "";
  let assistantBuffer = "";

  try {
    await ensureAuth();
    statusEl.textContent = "Claude is typing…";

    const stream = await puter.ai.chat(conversation, {
      model: "claude-opus-4-5-20251101",
      stream: true
    });

    for await (const chunk of stream) {
      let text = "";

      if (chunk?.message?.content) {
        for (const part of chunk.message.content) {
          if (part?.type === "output_text") {
            text += part.text;
          }
        }
      }

      if (chunk?.text) text += chunk.text;
      if (!text) continue;

      renderBuffer += text;
      assistantBuffer += text;

      markdownEl.innerHTML = marked.parse(renderBuffer);

      if (window.hljs) {
        markdownEl.querySelectorAll("pre code").forEach(block => {
          if (!block.classList.contains("hljs")) {
            window.hljs.highlightElement(block);
          }
        });
      }

      chatEl.scrollTop = chatEl.scrollHeight;
    }

    conversation.push({
      role: "assistant",
      content: assistantBuffer
    });

    statusEl.textContent = "Done";
  } catch (err) {
    statusEl.textContent = "Error";
    errorEl.textContent = String(err);
  } finally {
    sendBtn.disabled = false;
  }
}

ensureAuth();
</script>
</body>
</html>
""",
height=900,
)
