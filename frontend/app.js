const state = {
  tenancies: [],
  selectedTenancyId: "",
  sessionId: "",
  currentSkill: "",
};

const els = {
  apiStatus: document.getElementById("api-status"),
  skillVersion: document.getElementById("skill-version"),
  tenancyForm: document.getElementById("tenancy-form"),
  tenancyFeedback: document.getElementById("tenancy-feedback"),
  tenancySelect: document.getElementById("tenancy-select"),
  refreshTenancies: document.getElementById("refresh-tenancies"),
  createSession: document.getElementById("create-session"),
  sessionId: document.getElementById("session-id"),
  currentSkill: document.getElementById("current-skill"),
  chatPanel: document.getElementById("chat-panel"),
  chatBox: document.getElementById("chat-box"),
  messageForm: document.getElementById("message-form"),
  messageInput: document.getElementById("message-input"),
  messageFeedback: document.getElementById("message-feedback"),
  promptBank: document.querySelector(".prompt-bank"),
  inventoryPanel: document.getElementById("inventory-panel"),
  inventoryForm: document.getElementById("inventory-form"),
  inventoryCompartmentId: document.getElementById("inventory-compartment-id"),
  inventoryRegion: document.getElementById("inventory-region"),
  inventoryInstanceId: document.getElementById("inventory-instance-id"),
  inventoryFeedback: document.getElementById("inventory-feedback"),
  inventoryResults: document.getElementById("inventory-results"),
};

async function fetchJson(url, options) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const data = await response.json();
      detail = data?.detail || data?.error?.message || detail;
    } catch (_) {
      // Ignore parse errors and use the default detail.
    }
    throw new Error(detail);
  }

  return response.json();
}

function setFeedback(el, message, isError = false) {
  el.textContent = message || "";
  el.classList.toggle("error", isError);
}

function renderInventoryEmpty(message) {
  els.inventoryPanel.classList.add("is-visible");
  els.inventoryResults.className = "inventory-results empty";
  els.inventoryResults.textContent = message;
}

function hideInventoryPanel() {
  els.inventoryPanel.classList.remove("is-visible");
}

function showChatPanel() {
  els.chatPanel.classList.add("is-visible");
}

function hideChatPanel() {
  els.chatPanel.classList.remove("is-visible");
}

function showInventoryPanel() {
  els.inventoryPanel.classList.add("is-visible");
  hideChatPanel();
}

function renderChatMessage(role, content, meta = "") {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role === "user" ? "message-user" : "message-assistant"}`;

  const metaEl = document.createElement("div");
  metaEl.className = "message-meta";

  const bodyEl = document.createElement("div");
  bodyEl.className = "message-body";

  if (role === "assistant") {
    renderAssistantMeta(metaEl, meta);
    renderAssistantBody(bodyEl, content);
  } else {
    const label = document.createElement("span");
    label.textContent = meta || "User";
    metaEl.appendChild(label);
    bodyEl.textContent = content;
  }

  wrapper.append(metaEl, bodyEl);
  els.chatBox.appendChild(wrapper);
  els.chatBox.scrollTop = els.chatBox.scrollHeight;
}

function isBulletLine(line) {
  return line.trim().startsWith("- ");
}

function renderSectionContent(container, lines) {
  const bullets = lines.filter(isBulletLine);
  const prose = lines.filter((line) => line.trim() && !isBulletLine(line));

  if (prose.length) {
    const paragraph = document.createElement("p");
    paragraph.textContent = prose.join(" ");
    container.appendChild(paragraph);
  }

  if (bullets.length) {
    const list = document.createElement("ul");
    bullets.forEach((line) => {
      const item = document.createElement("li");
      item.textContent = line.replace(/^\s*-\s*/, "");
      list.appendChild(item);
    });
    container.appendChild(list);
  }
}

function renderAssistantBody(bodyEl, content) {
  const sections = content.split(/\n\s*\n/).map((block) => block.trim()).filter(Boolean);

  sections.forEach((section, index) => {
    const lines = section.split("\n").map((line) => line.trim()).filter(Boolean);
    if (!lines.length) {
      return;
    }

    const card = document.createElement("div");
    card.className = "assistant-section";

    const headingLine = lines[0];
    const hasHeading = headingLine.endsWith(":") && !headingLine.includes("Session `");

    if (hasHeading) {
      const heading = document.createElement("h3");
      heading.textContent = headingLine.slice(0, -1);
      card.appendChild(heading);
      renderSectionContent(card, lines.slice(1));
    } else {
      if (index === 0) {
        card.classList.add("assistant-summary");
      }
      renderSectionContent(card, lines);
    }

    bodyEl.appendChild(card);
  });
}

function renderAssistantMeta(metaEl, meta) {
  const defaultLabel = document.createElement("span");
  defaultLabel.textContent = "Assistant";
  metaEl.appendChild(defaultLabel);

  if (!meta) {
    return;
  }

  const [skill, reason] = meta.split("·").map((part) => part.trim());

  if (skill) {
    const skillBadge = document.createElement("span");
    skillBadge.className = "meta-badge meta-badge-skill";
    skillBadge.textContent = skill;
    metaEl.appendChild(skillBadge);
  }

  if (reason) {
    const reasonBadge = document.createElement("span");
    reasonBadge.className = "meta-badge meta-badge-reason";
    reasonBadge.textContent = reason;
    metaEl.appendChild(reasonBadge);
  }
}

function setSession(sessionId, currentSkill) {
  state.sessionId = sessionId;
  state.currentSkill = currentSkill;
  els.sessionId.textContent = sessionId || "None";
  els.currentSkill.textContent = currentSkill || "Not started";
}

function getSelectedTenancy() {
  return state.tenancies.find((tenancy) => tenancy.id === state.selectedTenancyId) || null;
}

function syncInventoryDefaults() {
  const tenancy = getSelectedTenancy();
  if (!tenancy) {
    els.inventoryRegion.value = "";
    hideInventoryPanel();
    return;
  }

  if (!els.inventoryRegion.value) {
    els.inventoryRegion.value = tenancy.home_region || "";
  }

  if (!els.inventoryCompartmentId.value) {
    const ocidCompartment = tenancy.compartments_in_scope.find((item) =>
      item.startsWith("ocid1.compartment.")
    );
    if (ocidCompartment) {
      els.inventoryCompartmentId.value = ocidCompartment;
    }
  }
}

function updateTenancyOptions() {
  const priorValue = state.selectedTenancyId;
  els.tenancySelect.innerHTML = "";

  if (!state.tenancies.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No tenancies registered yet";
    els.tenancySelect.appendChild(option);
    state.selectedTenancyId = "";
    hideInventoryPanel();
    return;
  }

  state.tenancies.forEach((tenancy) => {
    const option = document.createElement("option");
    option.value = tenancy.id;
    option.textContent = `${tenancy.tenancy_name} (${tenancy.onboarding_status})`;
    els.tenancySelect.appendChild(option);
  });

  state.selectedTenancyId =
    state.tenancies.find((tenancy) => tenancy.id === priorValue)?.id || state.tenancies[0].id;
  els.tenancySelect.value = state.selectedTenancyId;
  syncInventoryDefaults();
}

function createInventoryList(title, items, formatter) {
  if (!items?.length) {
    return null;
  }

  const section = document.createElement("section");
  section.className = "inventory-subsection";

  const heading = document.createElement("h5");
  heading.textContent = title;
  section.appendChild(heading);

  const list = document.createElement("ul");
  items.forEach((item) => {
    const line = document.createElement("li");
    line.textContent = formatter(item);
    list.appendChild(line);
  });
  section.appendChild(list);
  return section;
}

function renderInventoryResults(data) {
  showInventoryPanel();
  els.inventoryResults.className = "inventory-results";
  els.inventoryResults.innerHTML = "";

  const summary = document.createElement("div");
  summary.className = "inventory-summary";
  summary.innerHTML = `
    <strong>${data.instance_count} instance(s)</strong>
    <span>Region: ${data.region}</span>
    <span>Compartment: ${data.compartment_id}</span>
  `;
  els.inventoryResults.appendChild(summary);

  if (!data.instances.length) {
    const empty = document.createElement("div");
    empty.className = "inventory-empty-state";
    empty.textContent = "No compute instances were returned for this scope.";
    els.inventoryResults.appendChild(empty);
    return;
  }

  data.instances.forEach((instance) => {
    const card = document.createElement("article");
    card.className = "inventory-card";

    const header = document.createElement("div");
    header.className = "inventory-card-header";
    header.innerHTML = `
      <div>
        <h4>${instance.display_name}</h4>
        <p>${instance.instance_id}</p>
      </div>
      <div class="inventory-pill">${instance.lifecycle_state}</div>
    `;
    card.appendChild(header);

    const meta = document.createElement("div");
    meta.className = "inventory-meta-grid";
    [
      ["Shape", instance.shape],
      ["AD", instance.availability_domain],
      ["Fault Domain", instance.fault_domain || "n/a"],
      ["Region", instance.region],
    ].forEach(([label, value]) => {
      const block = document.createElement("div");
      block.className = "inventory-meta-item";
      block.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
      meta.appendChild(block);
    });
    card.appendChild(meta);

    if (instance.boot_volume) {
      const boot = document.createElement("section");
      boot.className = "inventory-subsection";
      boot.innerHTML = `
        <h5>Boot Volume</h5>
        <p>${instance.boot_volume.display_name} (${instance.boot_volume.volume_id})</p>
        <p>Size: ${instance.boot_volume.size_in_gbs || "n/a"} GB | State: ${instance.boot_volume.lifecycle_state || "n/a"}</p>
      `;
      card.appendChild(boot);
    }

    const blockVolumesSection = createInventoryList(
      "Block Volumes",
      instance.block_volumes,
      (volume) =>
        `${volume.display_name} (${volume.volume_id}) | ${volume.size_in_gbs || "n/a"} GB | ${volume.lifecycle_state || "n/a"}`
    );
    if (blockVolumesSection) {
      card.appendChild(blockVolumesSection);
    }

    const vnicsSection = createInventoryList(
      "VNICs",
      instance.vnics,
      (vnic) =>
        `${vnic.display_name} (${vnic.vnic_id}) | Private IP: ${vnic.private_ip || "n/a"} | Public IP: ${vnic.public_ip || "n/a"}`
    );
    if (vnicsSection) {
      card.appendChild(vnicsSection);
    }

    els.inventoryResults.appendChild(card);
  });
}

async function loadStatus() {
  try {
    const [health, version] = await Promise.all([
      fetchJson("/health"),
      fetchJson("/api/skills/version"),
    ]);
    els.apiStatus.textContent = health.status;
    els.skillVersion.textContent = `${version.repo_ref} / ${version.router_file}`;
  } catch (error) {
    els.apiStatus.textContent = "unreachable";
    els.skillVersion.textContent = "unknown";
  }
}

async function loadTenancies() {
  try {
    state.tenancies = await fetchJson("/api/tenancies");
    updateTenancyOptions();
    setFeedback(els.tenancyFeedback, `Loaded ${state.tenancies.length} tenancy profile(s).`);
  } catch (error) {
    setFeedback(els.tenancyFeedback, error.message, true);
  }
}

async function loadInventory() {
  showInventoryPanel();

  if (!state.selectedTenancyId) {
    setFeedback(els.inventoryFeedback, "Select a tenancy first.", true);
    return;
  }

  const compartmentId = els.inventoryCompartmentId.value.trim();
  const region = els.inventoryRegion.value.trim();
  const instanceId = els.inventoryInstanceId.value.trim();
  const query = new URLSearchParams();

  if (compartmentId) {
    query.set("compartment_id", compartmentId);
  }
  if (region) {
    query.set("region", region);
  }
  if (instanceId) {
    query.set("instance_id", instanceId);
  }

  try {
    setFeedback(els.inventoryFeedback, "Running read-only inventory lookup...");
    const suffix = query.toString() ? `?${query.toString()}` : "";
    const data = await fetchJson(
      `/api/tenancies/${state.selectedTenancyId}/inventory/compute${suffix}`
    );
    renderInventoryResults(data);
    setFeedback(
      els.inventoryFeedback,
      `Loaded ${data.instance_count} instance(s) from ${data.region}.`
    );
  } catch (error) {
    renderInventoryEmpty("Inventory results will appear here once the request succeeds.");
    setFeedback(els.inventoryFeedback, error.message, true);
  }
}

async function registerTenancy(event) {
  event.preventDefault();
  const form = new FormData(els.tenancyForm);

  const payload = {
    tenancy_name: form.get("tenancy_name"),
    tenancy_ocid: form.get("tenancy_ocid"),
    home_region: form.get("home_region"),
    target_regions: String(form.get("target_regions"))
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    compartments_in_scope: String(form.get("compartments_in_scope"))
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    persona: form.get("persona"),
    intended_use: form.get("intended_use"),
    application_name: form.get("application_name") || null,
    environment_name: form.get("environment_name") || null,
  };

  try {
    const result = await fetchJson("/api/tenancies", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setFeedback(
      els.tenancyFeedback,
      `Created tenancy profile ${result.id} with onboarding status ${result.onboarding_status}.`
    );
    els.tenancyForm.reset();
    await loadTenancies();
  } catch (error) {
    setFeedback(els.tenancyFeedback, error.message, true);
  }
}

async function createSession() {
  try {
    const payload = state.selectedTenancyId
      ? { tenancy_profile_id: state.selectedTenancyId }
      : {};
    const session = await fetchJson("/api/sessions", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    els.chatBox.innerHTML = "";
    showChatPanel();
    hideInventoryPanel();
    setSession(session.id, session.current_skill);
    const scopeLabel = state.selectedTenancyId ? "with tenancy context" : "without tenancy context";
    setFeedback(els.messageFeedback, `Session ${session.id} created ${scopeLabel}.`);
  } catch (error) {
    setFeedback(els.messageFeedback, error.message, true);
  }
}

async function sendMessage(message) {
  if (!state.sessionId) {
    setFeedback(els.messageFeedback, "Create a session before sending messages.", true);
    return;
  }

  try {
    showChatPanel();
    hideInventoryPanel();
    renderChatMessage("user", message, "User");
    const response = await fetchJson(`/api/sessions/${state.sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    setSession(state.sessionId, response.selected_skill);
    renderChatMessage(
      "assistant",
      response.assistant_message,
      `${response.selected_skill} · ${response.routing_reason}`
    );
    setFeedback(els.messageFeedback, `Routed to ${response.selected_skill}.`);
  } catch (error) {
    setFeedback(els.messageFeedback, error.message, true);
  }
}

function handlePromptBank(event) {
  const button = event.target.closest(".prompt-chip");
  if (!button) {
    return;
  }

  if (button.dataset.action === "inventory") {
    syncInventoryDefaults();
    loadInventory();
    return;
  }

  const prompt = button.dataset.prompt;
  els.messageInput.value = prompt;
  sendMessage(prompt);
}

async function init() {
  hideInventoryPanel();
  showChatPanel();
  await loadStatus();
  await loadTenancies();

  els.tenancyForm.addEventListener("submit", registerTenancy);
  els.refreshTenancies.addEventListener("click", loadTenancies);
  els.createSession.addEventListener("click", createSession);
  els.tenancySelect.addEventListener("change", (event) => {
    state.selectedTenancyId = event.target.value;
    syncInventoryDefaults();
  });
  els.messageForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = els.messageInput.value.trim();
    if (!message) {
      setFeedback(els.messageFeedback, "Enter a message first.", true);
      return;
    }
    els.messageInput.value = "";
    await sendMessage(message);
  });
  els.promptBank.addEventListener("click", handlePromptBank);
  syncInventoryDefaults();
}

init();
