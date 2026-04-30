import re

with open('templates/index.html', 'r') as f:
    html = f.read()

# We want to replace everything from <article class="message assistant"> 
# to the end of the turn loop (up to {% endfor %}\n          {% endfor %})
# We'll use a precise regex or string replacement.

old_block = """            <article class="message assistant">
              <div class="message-header">
                <span class="message-role">VibeTune AI</span>
              </div>
              <p>{{ turn.assistant_message }}</p>
            </article>

            {% if turn.reference_song %}
              <article class="message assistant">
                <div class="message-header">
                  <span class="message-role">Matched Song</span>
                </div>
                <div class="recommendations">
                  <section class="recommendation-card">
                    <div class="recommendation-sidebar">
                      <button
                        class="track-link play-inline-btn primary-play-btn"
                        type="button"
                        data-preview-url="{{ turn.reference_song.preview_url }}"
                        data-title="{{ turn.reference_song.title }}"
                        data-artist="{{ turn.reference_song.artist }}"
                      >
                        ▶ Play
                      </button>
                      <a class="track-link" href="{{ turn.reference_song.spotify_url or turn.reference_song.website_url }}" target="_blank" rel="noreferrer">Open</a>
                    </div>
                    <div class="recommendation-info">
                      <h3>{{ turn.reference_song.title }}</h3>
                      <p>{{ turn.reference_song.artist }}</p>
                      <p class="recommendation-meta">{{ turn.reference_song.language }} | {{ turn.reference_song.genre }}</p>
                      {% if not turn.reference_song.preview_url %}
                        <span class="preview-badge">Preview unavailable</span>
                      {% endif %}
                    </div>
                  </section>
                </div>
              </article>
            {% endif %}

            {% for song in turn.recommendations %}
              <article class="message assistant">
                <div class="recommendations">
                  <section class="recommendation-card">
                    <div class="recommendation-sidebar">
                      <button
                        class="track-link play-inline-btn primary-play-btn"
                        type="button"
                        data-preview-url="{{ song.preview_url }}"
                        data-title="{{ song.title }}"
                        data-artist="{{ song.artist }}"
                      >
                        ▶ Play
                      </button>
                      <a class="track-link" href="{{ song.spotify_url or song.website_url }}" target="_blank" rel="noreferrer">Open</a>
                      <form method="post" action="{{ url_for('favorite') }}" data-async="true">
                        <input type="hidden" name="title" value="{{ song.title }}" />
                        <input type="hidden" name="artist" value="{{ song.artist }}" />
                        <input type="hidden" name="language" value="{{ song.language }}" />
                        <input type="hidden" name="genre" value="{{ song.genre }}" />
                        <input type="hidden" name="album" value="{{ song.album }}" />
                        <input type="hidden" name="website_url" value="{{ song.website_url }}" />
                        <input type="hidden" name="app_url" value="{{ song.app_url }}" />
                        <input type="hidden" name="preview_url" value="{{ song.preview_url }}" />
                        <input type="hidden" name="spotify_url" value="{{ song.spotify_url }}" />
                        <input type="hidden" name="apple_url" value="{{ song.apple_url }}" />
                        <button class="track-link save-btn" type="submit">Save</button>
                      </form>
                    </div>
                    <div class="recommendation-info">
                      <h3>{{ song.title }}</h3>
                      <p>{{ song.artist }}</p>
                      <p class="recommendation-meta">{{ song.language }} | {{ song.genre }}</p>
                      {% if not song.preview_url %}
                        <span class="preview-badge">Preview unavailable</span>
                      {% endif %}
                    </div>
                  </section>
                </div>
              </article>
            {% endfor %}"""

new_block = """            <article class="message assistant">
              <div class="message-header">
                <span class="message-role">VibeTune AI</span>
              </div>
              <p>{{ turn.assistant_message }}</p>

              {% if turn.reference_song or turn.recommendations %}
                <div class="embedded-recommendations" style="margin-top: 1rem; display: flex; flex-direction: column; gap: 0.8rem;">
                  
                  {% if turn.reference_song %}
                    <section class="recommendation-card embedded-card" style="margin: 0; background: rgba(255,255,255,0.02);">
                      <div class="recommendation-sidebar">
                        <button
                          class="track-link play-inline-btn primary-play-btn"
                          type="button"
                          data-preview-url="{{ turn.reference_song.preview_url }}"
                          data-title="{{ turn.reference_song.title }}"
                          data-artist="{{ turn.reference_song.artist }}"
                        >
                          ▶ Play
                        </button>
                        <a class="track-link" href="{{ turn.reference_song.spotify_url or turn.reference_song.website_url }}" target="_blank" rel="noreferrer">Open</a>
                      </div>
                      <div class="recommendation-info">
                        <h3>{{ turn.reference_song.title }} <span style="font-size:0.7rem; padding: 2px 6px; background: rgba(59, 130, 246, 0.2); border-radius: 8px; margin-left: 6px; color: var(--accent-1);">Matched</span></h3>
                        <p>{{ turn.reference_song.artist }}</p>
                        <p class="recommendation-meta">{{ turn.reference_song.language }} | {{ turn.reference_song.genre }}</p>
                        {% if not turn.reference_song.preview_url %}
                          <span class="preview-badge">Preview unavailable</span>
                        {% endif %}
                      </div>
                    </section>
                  {% endif %}

                  {% for song in turn.recommendations %}
                    <section class="recommendation-card embedded-card" style="margin: 0; background: rgba(255,255,255,0.02);">
                      <div class="recommendation-sidebar">
                        <button
                          class="track-link play-inline-btn primary-play-btn"
                          type="button"
                          data-preview-url="{{ song.preview_url }}"
                          data-title="{{ song.title }}"
                          data-artist="{{ song.artist }}"
                        >
                          ▶ Play
                        </button>
                        <a class="track-link" href="{{ song.spotify_url or song.website_url }}" target="_blank" rel="noreferrer">Open</a>
                        <form method="post" action="{{ url_for('favorite') }}" data-async="true">
                          <input type="hidden" name="title" value="{{ song.title }}" />
                          <input type="hidden" name="artist" value="{{ song.artist }}" />
                          <input type="hidden" name="language" value="{{ song.language }}" />
                          <input type="hidden" name="genre" value="{{ song.genre }}" />
                          <input type="hidden" name="album" value="{{ song.album }}" />
                          <input type="hidden" name="website_url" value="{{ song.website_url }}" />
                          <input type="hidden" name="app_url" value="{{ song.app_url }}" />
                          <input type="hidden" name="preview_url" value="{{ song.preview_url }}" />
                          <input type="hidden" name="spotify_url" value="{{ song.spotify_url }}" />
                          <input type="hidden" name="apple_url" value="{{ song.apple_url }}" />
                          <button class="track-link save-btn" type="submit">Save</button>
                        </form>
                      </div>
                      <div class="recommendation-info">
                        <h3>{{ song.title }}</h3>
                        <p>{{ song.artist }}</p>
                        <p class="recommendation-meta">{{ song.language }} | {{ song.genre }}</p>
                        {% if not song.preview_url %}
                          <span class="preview-badge">Preview unavailable</span>
                        {% endif %}
                      </div>
                    </section>
                  {% endfor %}
                </div>
              {% endif %}
            </article>"""

new_html = html.replace(old_block, new_block)
with open('templates/index.html', 'w') as f:
    f.write(new_html)
