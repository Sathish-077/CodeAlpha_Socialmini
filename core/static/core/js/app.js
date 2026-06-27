// ── Like Toggle ──────────────────────────────────────────────────────────────
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.like-btn');
  if (!btn) return;

  const postId = btn.dataset.postId;
  const csrf = btn.dataset.csrf;

  btn.disabled = true;
  try {
    const res = await fetch(`/post/${postId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    const icon = btn.querySelector('.like-icon');
    const count = btn.querySelector('.like-count');
    icon.textContent = data.liked ? '♥' : '♡';
    count.textContent = data.count;
    btn.classList.toggle('liked', data.liked);
  } catch (err) {
    console.error('Like failed:', err);
  } finally {
    btn.disabled = false;
  }
});

// ── Follow Toggle ─────────────────────────────────────────────────────────────
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.follow-btn');
  if (!btn) return;

  const username = btn.dataset.username;
  const isFollowing = btn.dataset.following === 'true';

  // Get CSRF from any form on page
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    || getCookie('csrftoken');

  btn.disabled = true;
  try {
    const res = await fetch(`/follow/${username}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    const nowFollowing = data.following;
    btn.dataset.following = nowFollowing;
    btn.textContent = nowFollowing ? 'Following' : 'Follow';
    btn.className = btn.className.replace(/btn-primary|btn-outline|btn-following/g, '').trim();
    btn.classList.add(nowFollowing ? 'btn-following' : 'btn-primary');

    // Update followers count on profile page if present
    const fc = document.querySelector('#followers-count strong');
    if (fc && data.followers_count !== undefined) {
      fc.textContent = data.followers_count;
    }
  } catch (err) {
    console.error('Follow failed:', err);
  } finally {
    btn.disabled = false;
  }
});

// ── Comment Submit ────────────────────────────────────────────────────────────
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.comment-submit');
  if (!btn) return;

  const postId = btn.dataset.postId;
  const input = document.querySelector(`.comment-input[data-post-id="${postId}"]`);
  const csrf = input.dataset.csrf;
  const content = input.value.trim();

  if (!content) return;

  btn.disabled = true;
  try {
    const res = await fetch(`/post/${postId}/comment/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    const data = await res.json();
    if (data.success) {
      input.value = '';
      appendComment(postId, data);
      // Update comment count
      const countEl = document.querySelector(`.comment-count-${postId}`);
      if (countEl) countEl.textContent = data.count;
    }
  } catch (err) {
    console.error('Comment failed:', err);
  } finally {
    btn.disabled = false;
  }
});

// Submit comment on Enter
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target.matches('.comment-input')) {
    const postId = e.target.dataset.postId;
    document.querySelector(`.comment-submit[data-post-id="${postId}"]`)?.click();
  }
});

function appendComment(postId, data) {
  const list = document.getElementById(`comment-list-${postId}`);
  if (!list) return;
  const div = document.createElement('div');
  div.className = 'comment-item';
  div.id = `comment-${data.id}`;
  div.innerHTML = `
    <div class="avatar-xs" style="background:${data.avatar_color}">${data.author[0].toUpperCase()}</div>
    <div class="comment-body">
      <a href="/profile/${data.author}/"><strong>${data.author}</strong></a>
      <span>${escHtml(data.content)}</span>
    </div>
    <button class="btn-ghost delete-comment-btn"
            data-comment-id="${data.id}"
            data-csrf="${document.querySelector('.comment-input[data-post-id="'+postId+'"]').dataset.csrf}">✕</button>
  `;
  list.appendChild(div);
}

// ── Delete Comment ────────────────────────────────────────────────────────────
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.delete-comment-btn');
  if (!btn) return;

  const commentId = btn.dataset.commentId;
  const csrf = btn.dataset.csrf;

  if (!confirm('Delete this comment?')) return;

  try {
    const res = await fetch(`/comment/${commentId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf },
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById(`comment-${commentId}`)?.remove();
    }
  } catch (err) {
    console.error('Delete comment failed:', err);
  }
});

// ── Delete Post confirmation ──────────────────────────────────────────────────
document.addEventListener('submit', (e) => {
  if (e.target.matches('.delete-form')) {
    if (!confirm('Delete this post?')) e.preventDefault();
  }
});

// ── Helpers ──────────────────────────────────────────────────────────────────
function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}

function escHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Auto-dismiss toasts
document.querySelectorAll('.toast').forEach(t => {
  setTimeout(() => t.remove(), 3500);
});
