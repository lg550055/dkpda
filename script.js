document.addEventListener('DOMContentLoaded', function () {

    // --- Header height for sidebar sticky positioning ---
    const headerEl = document.querySelector('header');
    function syncHeaderHeight() {
        if (headerEl) {
            document.documentElement.style.setProperty(
                '--header-height',
                headerEl.offsetHeight + 'px'
            );
        }
    }
    syncHeaderHeight();
    window.addEventListener('resize', syncHeaderHeight);

    // --- Theme ---
    const toggleBtn = document.getElementById('theme-toggle');
    const body = document.body;

    function applyTheme(dark) {
        body.classList.toggle('dark', dark);
        toggleBtn.textContent = dark ? '☀️' : '🌙';
    }

    applyTheme(localStorage.getItem('theme') === 'dark');

    toggleBtn.addEventListener('click', function () {
        const isDark = body.classList.toggle('dark');
        toggleBtn.textContent = isDark ? '☀️' : '🌙';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    // --- Date ---
    const dateEl = document.getElementById('issue-date');
    if (dateEl) {
        dateEl.textContent = new Date().toLocaleDateString('en-US', {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
        });
    }

    // --- Category nav ---
    const navLinks = document.querySelectorAll('nav a[data-category]');
    let currentCategory = 'all';
    let allArticles = [];

    navLinks.forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            currentCategory = link.dataset.category;
            displayArticles(allArticles, currentCategory);
        });
    });

    // --- Article containers ---
    const articlesContainer = document.getElementById('articles-container');
    const trendingContainer = document.getElementById('trending-container');

    function formatDate(isoString) {
        try {
            return new Date(isoString).toLocaleDateString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric'
            });
        } catch (_) {
            return '';
        }
    }

    function categoryOf(article) {
        return (article.category || '').toLowerCase();
    }

    function metaHTML(article) {
        return `
            <div class="article-meta">
                <span class="article-date">${formatDate(article.created_at)}</span>
                <div class="article-votes">
                    <button class="vote-btn upvote" data-id="${article.id}" data-type="upvote" title="Upvote">
                        👍 <span class="vote-count">${article.upvotes ?? 0}</span>
                    </button>
                    <button class="vote-btn downvote" data-id="${article.id}" data-type="downvote" title="Downvote">
                        👎 <span class="vote-count">${article.downvotes ?? 0}</span>
                    </button>
                </div>
            </div>
        `;
    }

    function createFeaturedArticle(article) {
        const el = document.createElement('article');
        el.className = 'article-featured';
        el.dataset.category = categoryOf(article);

        const imgStyle = article.image_url
            ? `background-image: url('${article.image_url}')`
            : 'background: var(--border)';

        el.innerHTML = `
            <div class="article-featured-img" style="${imgStyle}">
                <div class="article-featured-overlay"></div>
            </div>
            <div class="article-body">
                <span class="article-category">${article.category || 'General'}</span>
                <h2 class="article-featured-title">${article.title}</h2>
                <p class="article-excerpt">${article.content}</p>
                ${metaHTML(article)}
            </div>
        `;
        return el;
    }

    function createArticleCard(article) {
        const el = document.createElement('article');
        el.className = 'article-card';
        el.dataset.category = categoryOf(article);

        el.innerHTML = `
            ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}" class="card-img" loading="lazy">` : ''}
            <div class="card-body">
                <span class="article-category">${article.category || 'General'}</span>
                <h3 class="card-title">${article.title}</h3>
                <p class="card-excerpt">${article.content}</p>
                ${metaHTML(article)}
            </div>
        `;
        return el;
    }

    function renderTrending(articles) {
        if (!trendingContainer) return;
        const sorted = [...articles]
            .sort((a, b) => (b.upvotes ?? 0) - (a.upvotes ?? 0))
            .slice(0, 5);

        trendingContainer.innerHTML = '';
        sorted.forEach((a, i) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="trending-num">${i + 1}</span>
                <div class="trending-item-inner">
                    <span class="trending-cat">${a.category || 'General'}</span>
                    <p class="trending-title">${a.title}</p>
                </div>
            `;
            trendingContainer.appendChild(li);
        });
    }

    function displayArticles(articles, category) {
        articlesContainer.innerHTML = '';

        const filtered = category === 'all'
            ? articles
            : articles.filter(a => categoryOf(a) === category);

        if (!filtered.length) {
            articlesContainer.innerHTML = '<p class="no-articles">No articles in this category yet.</p>';
            return;
        }

        const topLabel = document.createElement('span');
        topLabel.className = 'section-label';
        topLabel.textContent = 'Top Story';
        articlesContainer.appendChild(topLabel);

        articlesContainer.appendChild(createFeaturedArticle(filtered[0]));

        if (filtered.length > 1) {
            const label = document.createElement('span');
            label.className = 'section-label';
            label.textContent = 'Latest Stories';
            articlesContainer.appendChild(label);

            const grid = document.createElement('div');
            grid.className = 'articles-grid';
            filtered.slice(1).forEach(a => grid.appendChild(createArticleCard(a)));
            articlesContainer.appendChild(grid);
        }
    }

    // --- Voting ---
    articlesContainer.addEventListener('click', async function (e) {
        const btn = e.target.closest('.vote-btn');
        if (!btn) return;

        const articleId = btn.dataset.id;
        const voteType = btn.dataset.type;
        const token = localStorage.getItem('token');

        if (!token) {
            // Non-intrusive nudge — replace with a modal if auth UI is added later
            btn.title = 'Log in to vote';
            btn.style.animation = 'none';
            btn.offsetHeight; // reflow
            btn.style.opacity = '0.5';
            setTimeout(() => { btn.style.opacity = ''; }, 600);
            return;
        }

        try {
            const res = await fetch(`http://localhost:8000/articles/${articleId}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ vote_type: voteType })
            });

            if (res.ok) {
                // Optimistic local update
                const countEl = btn.querySelector('.vote-count');
                if (countEl) {
                    const prev = parseInt(countEl.textContent, 10) || 0;
                    countEl.textContent = prev + 1;
                }
                btn.classList.toggle('voted-up', voteType === 'upvote');
                btn.classList.toggle('voted-down', voteType === 'downvote');
            }
        } catch (err) {
            console.error('Vote failed', err);
        }
    });

    // --- Load articles ---
    async function loadArticles() {
        try {
            const resp = await fetch('http://localhost:8000/articles');
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            allArticles = await resp.json();

            if (!Array.isArray(allArticles) || !allArticles.length) {
                articlesContainer.innerHTML = '<p class="no-articles">No articles available.</p>';
                return;
            }

            displayArticles(allArticles, currentCategory);
            renderTrending(allArticles);
        } catch (err) {
            console.error('Failed to load articles', err);
            articlesContainer.innerHTML = '<p class="load-error">Could not reach the server. Make sure the backend is running on port 8000.</p>';
        }
    }

    loadArticles();
});
