#!/usr/bin/env python3
"""
Dynamic Blog System
Automatically reads markdown files from ./blogs folder
"""

import os
import re
from datetime import datetime
from flask import Flask, render_template, abort
import markdown
import frontmatter

app = Flask(__name__)

# Configuration
BLOG_DIR = os.path.join(os.path.dirname(__file__), 'blogs')
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

# Ensure directories exist
os.makedirs(BLOG_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)


def get_blog_files():
    """Get all markdown files from the blogs directory"""
    blog_files = []
    for filename in os.listdir(BLOG_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(BLOG_DIR, filename)
            blog_files.append({
                'filename': filename,
                'filepath': filepath,
                'slug': os.path.splitext(filename)[0]
            })
    return blog_files


def parse_blog_post(filepath):
    """Parse a markdown file with frontmatter"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Extract metadata
        metadata = {
            'title': post.get('title', 'Untitled'),
            'date': post.get('date', datetime.now()),
            'author': post.get('author', 'Anonymous'),
            'tags': post.get('tags', []),
            'excerpt': post.get('excerpt', ''),
            'slug': os.path.splitext(os.path.basename(filepath))[0]
        }
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            post.content,
            extensions=['extra', 'codehilite', 'tables', 'toc']
        )
        
        return {
            'metadata': metadata,
            'content': html_content,
            'raw_content': post.content
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None


def get_all_posts():
    """Get all blog posts with metadata"""
    posts = []
    for blog_file in get_blog_files():
        post_data = parse_blog_post(blog_file['filepath'])
        if post_data:
            posts.append({
                **post_data['metadata'],
                'content': post_data['content'],
                'filename': blog_file['filename']
            })
    
    # Sort by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts


def get_post_by_slug(slug):
    """Get a specific blog post by slug"""
    filepath = os.path.join(BLOG_DIR, f"{slug}.md")
    if not os.path.exists(filepath):
        return None
    
    return parse_blog_post(filepath)


@app.route('/')
def index():
    """Home page - list all blog posts"""
    posts = get_all_posts()
    
    # Format dates for display
    for post in posts:
        if isinstance(post['date'], datetime):
            post['formatted_date'] = post['date'].strftime('%B %d, %Y')
        else:
            post['formatted_date'] = str(post['date'])
    
    return render_template('index.html', posts=posts)


@app.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post page"""
    post_data = get_post_by_slug(slug)
    if not post_data:
        abort(404)
    
    # Get all posts for navigation
    all_posts = get_all_posts()
    current_index = None
    for i, post in enumerate(all_posts):
        if post['slug'] == slug:
            current_index = i
            break
    
    # Get next and previous posts
    next_post = all_posts[current_index + 1] if current_index is not None and current_index + 1 < len(all_posts) else None
    prev_post = all_posts[current_index - 1] if current_index is not None and current_index - 1 >= 0 else None
    
    # Format date
    metadata = post_data['metadata']
    if isinstance(metadata['date'], datetime):
        formatted_date = metadata['date'].strftime('%B %d, %Y')
    else:
        formatted_date = str(metadata['date'])
    
    return render_template('blog_post.html', 
                          post=post_data,
                          formatted_date=formatted_date,
                          next_post=next_post,
                          prev_post=prev_post)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


if __name__ == '__main__':
    # Create sample blogs if none exist
    if not os.listdir(BLOG_DIR):
        create_sample_blogs()
    
    print("Starting blog system...")
    print(f"Blog directory: {BLOG_DIR}")
    print(f"Number of blog files: {len(get_blog_files())}")
    app.run(debug=True, host='0.0.0.0', port=5000)


def create_sample_blogs():
    """Create sample blog posts if none exist"""
    sample_blogs = [
        {
            'filename': 'welcome-to-my-blog.md',
            'content': '''---
title: "Welcome to My Blog"
date: 2023-10-01
author: "Blog Author"
tags: [welcome, introduction]
excerpt: "Welcome to my new blog system built with Python and Flask!"
---

# Welcome to My Blog!

This is my first blog post using the dynamic blog system. The system automatically reads markdown files from the `./blog/blogs` folder and displays them without requiring any code updates.

## Features

- **Dynamic content**: Just add a new `.md` file to the blogs folder
- **Markdown support**: Write posts using markdown syntax
- **Frontmatter metadata**: Add title, date, author, tags, and excerpt
- **Automatic sorting**: Posts are sorted by date (newest first)
- **Responsive design**: Works on mobile and desktop

## How to Add New Posts

1. Create a new markdown file in the `./blog/blogs/` folder
2. Add YAML frontmatter at the top:
   ```yaml
   ---
   title: "Your Post Title"
   date: YYYY-MM-DD
   author: "Your Name"
   tags: [tag1, tag2]
   excerpt: "Brief description"
   ---
   ```
3. Write your content using markdown
4. Save the file - it will automatically appear on the blog!

## Code Example

Here's a simple Python example:

```python
def hello_world():
    print("Hello, Blog World!")
    return "Success"
```

Enjoy blogging!'''
        },
        {
            'filename': 'markdown-tips.md',
            'content': '''---
title: "Markdown Tips and Tricks"
date: 2023-10-05
author: "Blog Author"
tags: [markdown, writing, tips]
excerpt: "Useful markdown formatting tips for better blog posts"
---

# Markdown Tips and Tricks

Markdown is a lightweight markup language that makes writing for the web easy. Here are some tips for creating great blog posts.

## Headings

Use headings to structure your content:

```markdown
# Main Title (H1)
## Section (H2)
### Subsection (H3)
```

## Formatting

- **Bold text** with `**bold**` or `__bold__`
- *Italic text* with `*italic*` or `_italic_`
- ***Bold and italic*** with `***bold italic***`
- ~~Strikethrough~~ with `~~strikethrough~~`

## Lists

### Unordered Lists

```markdown
- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2
- Item 3
```

### Ordered Lists

```markdown
1. First item
2. Second item
3. Third item
```

## Code Blocks

Inline code: `print("Hello")`

Code blocks with syntax highlighting:

```python
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
```

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```

## Links and Images

- [Link text](https://example.com)
- ![Alt text](image.jpg)

## Tables

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

## Blockquotes

> This is a blockquote.
> It can span multiple lines.
>
> — Author Name

## Horizontal Rules

---

Three or more hyphens, asterisks, or underscores.

## Task Lists

```markdown
- [x] Completed task
- [ ] Incomplete task
- [ ] Another task
```

Happy writing!'''
        }
    ]
    
    for blog in sample_blogs:
        filepath = os.path.join(BLOG_DIR, blog['filename'])
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(blog['content'])
    
    print(f"Created {len(sample_blogs)} sample blog posts")
