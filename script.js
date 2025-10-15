document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme in localStorage
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        toggleButton.textContent = '☀️';
    }
    
    toggleButton.addEventListener('click', function() {
        if (body.classList.contains('light-mode')) {
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
            toggleButton.textContent = '☀️';
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
            toggleButton.textContent = '🌙';
            localStorage.setItem('theme', 'light');
        }
    });

    // --- Articles fetching and rendering ---
    const articlesContainer = document.getElementById('articles-container');

    function formatDate(isoString) {
        try {
            const d = new Date(isoString);
            return d.toLocaleDateString();
        } catch (e) {
            return isoString;
        }
    }

    function renderArticle(article) {
        const el = document.createElement('article');

        const img = document.createElement('img');
        img.src = './media/cfclasspic.png';
        img.alt = 'Satirical Image';

        const topic = document.createElement('span');
        topic.className = 'topic';
        topic.textContent = 'satire';

        const date = document.createElement('span');
        date.className = 'date';
        date.textContent = formatDate(article.created_at);

        const h2 = document.createElement('h2');
        h2.textContent = article.title;

        const p = document.createElement('p');
        p.textContent = article.content;

        const meta = document.createElement('div');
        meta.className = 'meta';
        meta.textContent = `Upvotes: ${article.upvotes}  Downvotes: ${article.downvotes}`;

        el.appendChild(img);
        el.appendChild(topic);
        el.appendChild(date);
        el.appendChild(h2);
        el.appendChild(p);
        el.appendChild(meta);

        return el;
    }

    async function loadArticles() {
        try {
            const resp = await fetch('http://localhost:8000/articles');
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const articles = await resp.json();
            articlesContainer.innerHTML = '';
            if (!Array.isArray(articles) || articles.length === 0) {
                articlesContainer.textContent = 'No articles available.';
                return;
            }
            for (const a of articles) {
                articlesContainer.appendChild(renderArticle(a));
            }
        } catch (err) {
            console.error('Failed to load articles', err);
            articlesContainer.textContent = 'Failed to load articles.';
        }
    }

    // Load on startup
    loadArticles();
});