document.addEventListener("DOMContentLoaded", () => {
  const SNAPSHOT_PREFIX = "vibetune:snapshot:";
  let currentPlayButton = null;

  function scrollToLatest() {
    const stack = document.querySelector(".message-stack");
    if (stack) {
      stack.scrollTop = stack.scrollHeight;
    }
  }

  function snapshotKey() {
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function saveSnapshot() {
    const shell = document.querySelector(".page-shell");
    if (!shell) return null;

    const key = snapshotKey();
    sessionStorage.setItem(`${SNAPSHOT_PREFIX}${key}`, shell.outerHTML);
    return key;
  }

  function restoreSnapshot(key) {
    if (!key) return false;
    const html = sessionStorage.getItem(`${SNAPSHOT_PREFIX}${key}`);
    if (!html) return false;

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const nextShell = doc.querySelector(".page-shell");
    const currentShell = document.querySelector(".page-shell");
    if (!nextShell || !currentShell) return false;

    const panelsToUpdate = [".chat-log", ".more-actions", ".favorites-list"];
    panelsToUpdate.forEach(selector => {
      const currentPart = currentShell.querySelector(selector);
      const nextPart = doc.querySelector(selector);
      if (currentPart && nextPart) currentPart.replaceWith(nextPart);
    });

    wireUi();
    scrollToLatest();
    return true;
  }

  function syncHistoryState(usePush) {
    const key = saveSnapshot();
    if (!key) return;

    const state = { vibetuneSnapshotKey: key };
    if (usePush) {
      history.pushState(state, "", window.location.href);
    } else {
      history.replaceState(state, "", window.location.href);
    }
  }

  function showChatLoadingMessage(form) {
    if (!form.classList.contains("chat-form")) return;

    const stack = document.querySelector(".message-stack");
    if (!stack) return;

    const existing = stack.querySelector(".loading-message");
    if (existing) return;

    const loading = document.createElement("article");
    loading.className = "message assistant loading-message";
    loading.innerHTML = `
      <div class="message-header">
        <span class="message-role">VibeTune AI</span>
      </div>
      <div class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `;

    stack.appendChild(loading);
    scrollToLatest();
  }

  function hideChatLoadingMessage() {
    const loading = document.querySelector(".loading-message");
    if (loading) loading.remove();
  }

  async function submitFormAsync(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = true;
    showChatLoadingMessage(form);

    try {
      const response = await fetch(form.action, {
        method: (form.method || "POST").toUpperCase(),
        body: new FormData(form),
        headers: {
          "X-Requested-With": "fetch",
        },
      });

      const html = await response.text();
      const parser = new DOMParser();
      const nextDoc = parser.parseFromString(html, "text/html");
      const currentShell = document.querySelector(".page-shell");
      const nextShell = nextDoc.querySelector(".page-shell");

      // If request redirects to login/auth page, do a full navigation.
      if (!currentShell || !nextShell) {
        window.location.assign(response.url || form.action);
        return;
      }

      const panelsToUpdate = [".chat-log", ".more-actions", ".favorites-list"];
      panelsToUpdate.forEach(selector => {
        const currentPart = currentShell.querySelector(selector);
        const nextPart = nextDoc.querySelector(selector);
        if (currentPart && nextPart) currentPart.replaceWith(nextPart);
      });

      syncHistoryState(true);
      wireUi();
      scrollToLatest();
      
      if (form.classList.contains('chat-form')) {
        form.reset();
      }
    } catch (error) {
      hideChatLoadingMessage();
      // Fallback to regular submit if fetch fails.
      form.submit();
    } finally {
      hideChatLoadingMessage();
      if (submitButton) submitButton.disabled = false;
    }
  }

  function wireQuickMoodButtons() {
    const chatForm = document.querySelector(".chat-form");
    const queryInput = document.querySelector("#query");

    document.querySelectorAll(".quick-mood-btn").forEach((button) => {
      if (button.dataset.bound === "1") return;

      button.addEventListener("click", () => {
        if (!chatForm || !queryInput) return;
        queryInput.value = button.dataset.query || button.textContent.trim();
        chatForm.requestSubmit();
      });
      button.dataset.bound = "1";
    });
  }

  function wireInlinePlayer() {
    const audio = document.querySelector("#inline-audio");
    const trackLabel = document.querySelector("#inline-player-track");
    const timeLabel = document.querySelector("#inline-player-time");
    const progress = document.querySelector("#inline-player-progress");
    const progressFill = document.querySelector("#inline-player-progress-fill");
    const player = document.querySelector("#inline-player");
    if (!audio || !trackLabel) return;

    function formatTime(seconds) {
      if (!Number.isFinite(seconds) || seconds < 0) return "00:00";
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }

    function updateTimeLabel() {
      if (!timeLabel) return;
      const current = formatTime(audio.currentTime || 0);
      const total = formatTime(audio.duration || 0);
      timeLabel.textContent = `${current} / ${total}`;
    }

    function updateProgress() {
      if (!progress || !progressFill) return;
      const duration = audio.duration || 0;
      const current = audio.currentTime || 0;
      const percent = duration > 0 ? Math.min(100, Math.max(0, (current / duration) * 100)) : 0;
      progressFill.style.width = `${percent}%`;
      progress.setAttribute("aria-valuenow", String(Math.round(percent)));
    }

    function seekFromClientX(clientX) {
      if (!progress) return;
      const duration = audio.duration || 0;
      if (duration <= 0) return;

      const rect = progress.getBoundingClientRect();
      const ratio = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
      audio.currentTime = ratio * duration;
      updateTimeLabel();
      updateProgress();
    }

    function resetPlayButtons() {
      document.querySelectorAll(".play-inline-btn").forEach((button) => {
        if (button.disabled) return;
        button.textContent = "Play";
        button.classList.remove("is-playing");
      });
      if (player) player.classList.remove("is-playing");
      currentPlayButton = null;
      if (timeLabel) timeLabel.textContent = "00:00 / 00:00";
      if (progressFill) progressFill.style.width = "0%";
      if (progress) progress.setAttribute("aria-valuenow", "0");
    }

    if (audio.dataset.bound !== "1") {
      audio.addEventListener("pause", () => {
        if (audio.ended) return;
        if (currentPlayButton) {
          currentPlayButton.textContent = "Play";
          currentPlayButton.classList.remove("is-playing");
        }
        if (player) player.classList.remove("is-playing");
      });

      audio.addEventListener("play", () => {
        if (currentPlayButton && !currentPlayButton.disabled) {
          currentPlayButton.textContent = "Pause";
          currentPlayButton.classList.add("is-playing");
        }
        if (player) player.classList.add("is-playing");
      });

      audio.addEventListener("ended", () => {
        resetPlayButtons();
      });
      audio.addEventListener("timeupdate", updateTimeLabel);
      audio.addEventListener("timeupdate", updateProgress);
      audio.addEventListener("loadedmetadata", updateTimeLabel);
      audio.addEventListener("loadedmetadata", updateProgress);
      audio.addEventListener("emptied", updateTimeLabel);
      audio.addEventListener("emptied", updateProgress);

      audio.dataset.bound = "1";
    }

    if (progress && progress.dataset.bound !== "1") {
      progress.addEventListener("click", (event) => {
        seekFromClientX(event.clientX);
      });

      progress.addEventListener("keydown", (event) => {
        const duration = audio.duration || 0;
        if (duration <= 0) return;
        const step = Math.max(1, duration * 0.05);

        if (event.key === "ArrowRight") {
          event.preventDefault();
          audio.currentTime = Math.min(duration, (audio.currentTime || 0) + step);
          updateTimeLabel();
          updateProgress();
        } else if (event.key === "ArrowLeft") {
          event.preventDefault();
          audio.currentTime = Math.max(0, (audio.currentTime || 0) - step);
          updateTimeLabel();
          updateProgress();
        }
      });

      progress.dataset.bound = "1";
    }

    document.querySelectorAll(".play-inline-btn").forEach((button) => {
      if (button.dataset.bound === "1") return;

      button.addEventListener("click", () => {
        const previewUrl = button.dataset.previewUrl || "";
        if (!previewUrl) return;

        if (currentPlayButton === button && !audio.paused) {
          audio.pause();
          return;
        }

        const title = button.dataset.title || "Unknown title";
        const artist = button.dataset.artist || "Unknown artist";
        trackLabel.textContent = `${title} - ${artist}`;

        // Track recently played song
        addToRecentlyPlayed(title, artist, previewUrl);

        if (currentPlayButton && currentPlayButton !== button) {
          currentPlayButton.textContent = "Play";
          currentPlayButton.classList.remove("is-playing");
        }
        currentPlayButton = button;

        if (audio.src !== previewUrl) {
          audio.src = previewUrl;
        }
        updateTimeLabel();
        updateProgress();
        audio.play().catch(() => {});
      });

      button.dataset.bound = "1";
    });
  }

  function wireAsyncForms() {
    document.querySelectorAll("form[data-async='true']").forEach((form) => {
      if (form.dataset.bound === "1") return;

      form.addEventListener("submit", (event) => {
        event.preventDefault();
        submitFormAsync(form);
      });
      form.dataset.bound = "1";
    });
  }

  function addToRecentlyPlayed(title, artist, previewUrl) {
    fetch('/recently-played', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'fetch'
      },
      body: JSON.stringify({
        title: title,
        artist: artist,
        preview_url: previewUrl
      })
    }).then(() => {
      // Refresh the recently played section
      refreshRecentlyPlayed();
    }).catch(() => {
      // Silently fail if tracking doesn't work
    });
  }

  function refreshRecentlyPlayed() {
    fetch('/recently-played-section', {
      headers: {
        'X-Requested-With': 'fetch'
      }
    }).then(response => response.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newSection = doc.querySelector('.recently-played-list');
        const currentSection = document.querySelector('.recently-played-list');
        
        if (newSection && currentSection) {
          currentSection.innerHTML = newSection.innerHTML;
          // Re-wire the new play buttons
          wireInlinePlayer();
        }
      })
      .catch(() => {
        // Silently fail if refresh doesn't work
      });
  }

  function wireUi() {
    wireQuickMoodButtons();
    wireAsyncForms();
    wireInlinePlayer();
  }

  window.addEventListener("popstate", async (event) => {
    const key = event.state && event.state.vibetuneSnapshotKey;
    if (restoreSnapshot(key)) {
      return;
    }

    // If no snapshot exists (e.g. new tab/session), refresh this URL.
    window.location.reload();
  });

  wireUi();
  if (!history.state || !history.state.vibetuneSnapshotKey) {
    syncHistoryState(false);
  }
  scrollToLatest();
});
