const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("url-input");
const sendBtn = document.getElementById("sendBtn");
const voiceBtn = document.getElementById("voiceBtn");
const voiceOverlay = document.getElementById("voiceOverlay");
const stopVoice = document.getElementById("stopVoice");
const url = document.getElementById("url-input").value;

let messages = [
  {
    id: 1,
    type: "bot",
    content:
      "Welcome to PhishGuard AI! How can I assist you with phishing threat detection today?",
    suggestions: [
      "🛡️ Analyze suspicious domain",
      "📊 View threat intelligence",
      "⚡ Real-time monitoring status",
    ],
  },
];

// Render messages
function renderMessages() {
  chatMessages.innerHTML = "";
  messages.forEach((msg) => {
    const div = document.createElement("div");
    div.className = `message ${msg.type}`;
    div.innerHTML = `<p>${msg.content}</p>`;

    if (msg.suggestions) {
      msg.suggestions.forEach((s) => {
        const btn = document.createElement("button");
        btn.textContent = s;
        btn.className = "suggestion-btn";
        btn.onclick = () => {
          chatInput.value = s.replace(/[🛡️📊⚡🎯📈🔄📋⚙️🔔]/g, "").trim();
        };
        div.appendChild(btn);
      });
    }

    chatMessages.appendChild(div);
  });

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Bot response logic
// function getBotResponse(input) {
//   input = input.toLowerCase();
//   if (input.includes("domain") || input.includes("url"))
//     return "🔍 Analyzing domain for phishing indicators... Risk Level: HIGH";
//   if (input.includes("status") || input.includes("monitoring"))
//     return "📊 Current system status: Domain Hunter Active";
//   if (input.includes("threat") || input.includes("intelligence"))
//     return "🎯 Latest Threat Intelligence detected";
//   return "I can help you with phishing detection, domain analysis, and threat monitoring.";
// }

async function getBotResponseFromBackend(url) {
  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await response.json();

    if (data.error) return "Error: " + data.error;

    // Create response text
    let msg = `🔍 URL: ${data.url}\nVerdict: ${data.verdict}\nProbability: ${data.probability}\n`;
    if (data.reasons && data.reasons.length > 0) {
      msg += "Reasons:\n" + data.reasons.map((r) => " - " + r).join("\n");
    }
    return msg;
  } catch (err) {
    return "Error: Could not reach server.";
  }
}

// Update send button click
// sendBtn.onclick = async () => {
//   const text = chatInput.value.trim();
//   if (!text) return;

//   messages.push({ id: messages.length + 1, type: "user", content: text });
//   chatInput.value = "";
//   renderMessages();

//   // Add typing indicator
//   messages.push({
//     id: messages.length + 1,
//     type: "bot",
//     content: "PhishGuard AI is analyzing...",
//   });
//   renderMessages();

//   const botMsgContent = await getBotResponseFromBackend(text);

//   // Replace typing message with actual response
//   messages = messages.filter(
//     (m) => m.content !== "PhishGuard AI is analyzing..."
//   );
//   messages.push({
//     id: messages.length + 1,
//     type: "bot",
//     content: botMsgContent,
//   });
//   renderMessages();
// };

function getBotSuggestions(input) {
  input = input.toLowerCase();
  if (input.includes("domain"))
    return [
      "📈 View domain reputation",
      "🔄 Run deeper analysis",
      "📋 Export threat report",
    ];
  if (input.includes("status"))
    return [
      "⚙️ Configure agent settings",
      "📊 View detailed metrics",
      "🔔 Set up alerts",
    ];
  return [
    "🛡️ Analyze new domain",
    "📊 System health check",
    "🎯 Threat landscape",
  ];
}

// Send message
sendBtn.onclick = () => {
  const text = chatInput.value.trim();
  if (!text) return;

  messages.push({ id: messages.length + 1, type: "user", content: text });
  chatInput.value = "";
  renderMessages();

  setTimeout(() => {
    const botMsg = {
      id: messages.length + 1,
      type: "bot",
      content: getBotResponse(text),
      suggestions: getBotSuggestions(text),
    };
    messages.push(botMsg);
    renderMessages();
  }, 1500);
};

// Voice input simulation
voiceBtn.onclick = () => {
  voiceOverlay.style.display = "flex";
  setTimeout(() => {
    chatInput.value = "Check suspicious domain amazon-security-update.com";
    voiceOverlay.style.display = "none";
  }, 3000);
};

stopVoice.onclick = () => {
  voiceOverlay.style.display = "none";
};

// Initial render
renderMessages();

// Enter key sends message
chatInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendBtn.click();
});

async function sendUrl() {
  const url = document.getElementById("urlInput").value;

  fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: url }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      //   alert(
      //     `Verdict: ${data.verdict}\nProbability: ${
      //       data.probability
      //     }\nReasons: ${data.reasons.join("\n")}`
      //   );
      const chatContainer = document.getElementById("chat-messages"); // your chat area div

      function addMessage(content, sender = "bot") {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender); // CSS can style .message.bot and .message.user
        msgDiv.innerText = content;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }

      document
        .getElementById("send-btn")
        .addEventListener("click", async () => {
          const urlInput = document.getElementById("url-input").value.trim();
          if (!urlInput) return;

          // Display user's message
          addMessage(urlInput, "user");

          // Call Flask backend
          try {
            const response = await fetch("/predict", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ url: urlInput }),
            });
            const data = await response.json();

            // Format bot response
            let botMessage = `Verdict: ${data.verdict}\nProbability: ${data.probability}\n`;
            if (data.reasons && data.reasons.length > 0) {
              botMessage +=
                "Reasons:\n" + data.reasons.map((r) => "• " + r).join("\n");
            }

            // Display bot message
            addMessage(botMessage, "bot");
          } catch (err) {
            addMessage("Error connecting to server.", "bot");
          }

          // Clear input
          document.getElementById("url-input").value = "";
        });
    });
}
