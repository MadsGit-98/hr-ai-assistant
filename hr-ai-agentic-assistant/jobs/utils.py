import bleach
import markdown


def markdown_to_html_with_sanitization(text):
    """
    Convert markdown text to HTML and sanitize it to prevent XSS (T020a)
    """
    if text:
        # Convert markdown to HTML
        html = markdown.markdown(text, extensions=['extra', 'codehilite'])
        # Sanitize HTML to prevent XSS while allowing safe elements
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'code', 'pre', 'hr', 'a', 'img'
        ]
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title'],
            'p': ['class'],
            'code': ['class'],
            'pre': ['class']
        }
        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
    return ''