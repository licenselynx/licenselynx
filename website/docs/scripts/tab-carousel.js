class CodeCarousel {
    constructor(container) {
        this.container = container;
        this.slides = container.querySelectorAll('.code-slide');
        this.currentIndex = 0;
        this.isTyping = false;
        this.autoPlayInterval = null;

        // Code snippets
        this.codeSnippets = {
            java: `import org.licenselynx.*;

LicenseLynx.map("Eclipse Distribution License 1.0");
// Result: BSD-3-Clause
`,
            python: `from licenselynx.licenselynx import LicenseLynx
LicenseLynx.map("Eclipse Distribution License 1.0")
# Result: BSD-3-Clause
`,
            typescript: `import {map} from "@licenselynx/licenselynx";

map('Eclipse Distribution License 1.0');
// Result: BSD-3-Clause
`
        };

        // Syntax highlighting rules
        // Comments are listed FIRST to give them highest priority
        this.syntaxRules = {
            java: [
                { pattern: /\/\/.*/g, className: 'comment' },
                { pattern: /\b(import|class|public|private|static|void|new)\b/g, className: 'keyword' },
                { pattern: /\b([A-Z][a-zA-Z0-9]*)\b/g, className: 'class-name' },
                { pattern: /\b([a-z_][a-zA-Z0-9_]*)\s*\(/g, className: 'function', group: 1 },
                { pattern: /"[^"]*"/g, className: 'string' },
            ],
            python: [
                { pattern: /#.*/g, className: 'comment' },
                { pattern: /\b(from|import|def|class|return|if|else|elif|for|while|in|as)\b/g, className: 'keyword' },
                { pattern: /\b([A-Z][a-zA-Z0-9]*)\b/g, className: 'class-name' },
                { pattern: /\b([a-z_][a-z0-9_]*)\s*\(/g, className: 'function', group: 1 },
                { pattern: /"[^"]*"|'[^']*'/g, className: 'string' },
                { pattern: /\b([a-z_][a-z0-9_]*)\s*=/g, className: 'property', group: 1 },
            ],
            typescript: [
                { pattern: /\/\/.*/g, className: 'comment' },
                { pattern: /\b(import|export|from|const|let|var|function|class|interface|type|return|if|else|new)\b/g, className: 'keyword' },
                { pattern: /\b([A-Z][a-zA-Z0-9]*)\b/g, className: 'class-name' },
                { pattern: /\b([a-z_][a-zA-Z0-9_]*)\s*\(/g, className: 'function', group: 1 },
                { pattern: /"[^"]*"|'[^']*'|`[^`]*`/g, className: 'string' },
                { pattern: /\b(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g, className: 'property', group: 2 },
            ]
        };

        this.init();
    }

    init() {
        // Start with first slide
        this.typeCode(0);

        // Auto-play
        this.startAutoPlay();
    }

    highlightSyntax(code, language) {
        const rules = this.syntaxRules[language] || [];

        // Track positions to avoid overlapping replacements
        const replacements = [];

        rules.forEach(rule => {
            const matches = [...code.matchAll(rule.pattern)];
            matches.forEach(match => {
                const text = rule.group ? match[rule.group] : match[0];
                const index = rule.group ? match.index + match[0].indexOf(text) : match.index;
                replacements.push({
                    start: index,
                    end: index + text.length,
                    original: text,
                    className: rule.className
                });
            });
        });

        // Sort by start position (forward order)
        replacements.sort((a, b) => a.start - b.start);

        // Remove overlapping replacements (keep first match which has priority)
        const filtered = [];
        for (let i = 0; i < replacements.length; i++) {
            const current = replacements[i];
            const overlaps = filtered.some(r =>
                (current.start < r.end && current.end > r.start)
            );
            if (!overlaps) {
                filtered.push(current);
            }
        }

        // Build highlighted HTML in a single pass
        let result = '';
        let lastIndex = 0;

        filtered.forEach(r => {
            // Add text before this replacement
            result += this.escapeHtml(code.substring(lastIndex, r.start));
            // Add the highlighted token
            result += `<span class="token ${r.className}">${this.escapeHtml(r.original)}</span>`;
            lastIndex = r.end;
        });

        // Add remaining text
        result += this.escapeHtml(code.substring(lastIndex));

        return result;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getHtmlPosition(html, textPosition) {
        let pos = 0;
        let htmlPos = 0;
        let inTag = false;

        while (pos < textPosition && htmlPos < html.length) {
            if (html[htmlPos] === '<') {
                inTag = true;
            } else if (html[htmlPos] === '>') {
                inTag = false;
                htmlPos++;
                continue;
            }

            if (!inTag) {
                pos++;
            }
            htmlPos++;
        }

        return htmlPos;
    }

    async typeCode(index, charDelay = 30) {
        if (this.isTyping) return;

        this.isTyping = true;
        const slide = this.slides[index];
        const codeElement = slide.querySelector('code');
        const language = slide.dataset.language;
        const code = this.codeSnippets[language];

        codeElement.innerHTML = '';
        codeElement.classList.remove('typing-complete');

        let currentText = '';

        // Type character by character
        for (let i = 0; i < code.length; i++) {
            currentText += code[i];
            codeElement.innerHTML = this.highlightSyntax(currentText, language);
            await this.sleep(charDelay);
        }

        codeElement.classList.add('typing-complete');
        this.isTyping = false;
    }

    async goToSlide(index) {
        if (index === this.currentIndex || this.isTyping) return;

        // Fade out current
        this.slides[this.currentIndex].classList.remove('active');

        // Update index
        this.currentIndex = index;

        // Fade in new
        this.slides[this.currentIndex].classList.add('active');

        // Wait for fade transition
        await this.sleep(400);

        // Type new code
        await this.typeCode(this.currentIndex);
    }

    startAutoPlay(interval = 6000) {
        this.stopAutoPlay();
        this.autoPlayInterval = setInterval(() => {
            const nextIndex = (this.currentIndex + 1) % this.slides.length;
            this.goToSlide(nextIndex);
        }, interval);
    }

    stopAutoPlay() {
        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
            this.autoPlayInterval = null;
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.querySelector('.code-carousel');
    if (carousel) {
        new CodeCarousel(carousel);
    }
});