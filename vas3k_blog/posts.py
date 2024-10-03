from dataclasses import dataclass

DEFAULT_LIST_ITEMS_PER_PAGE = 30


@dataclass
class PostTypeConfig:
    name: str = "Posts"
    list_items_per_page: int = DEFAULT_LIST_ITEMS_PER_PAGE
    card_template: str = "posts/cards/horizontal.html",
    list_template: str = "posts/lists/layout.html",
    show_template: str = "posts/full/layout.html"


POST_TYPES: dict[str, PostTypeConfig] = {
    "blog": PostTypeConfig(
        name="Blog",
        list_items_per_page=30,
        card_template="posts/cards/horizontal.html",
        list_template="posts/lists/blog.html",
        show_template="posts/full/blog.html",
    ),
    "thoughts": PostTypeConfig(
        name="Thoughts",
        list_items_per_page=30,
        card_template="posts/cards/horizontal.html",
        list_template="posts/lists/notes.html",
        show_template="posts/full/notes.html",
    ),
    "books": PostTypeConfig(
        name="Books",
        list_items_per_page=30,
        card_template="posts/cards/vertical.html",
        list_template="posts/lists/books.html",
        show_template="posts/full/blog.html",
    ),
    "gallery": PostTypeConfig(
        name="Gallery",
        list_items_per_page=30,
        card_template="posts/cards/vertical.html",
        list_template="posts/lists/blog.html",
        show_template="posts/full/legacy/gallery.html",
    ),
    "inside": PostTypeConfig(
        name="Inside",
        list_items_per_page=30,
        card_template="posts/cards/vertical.html",
        list_template="posts/lists/notes.html",
        show_template="posts/full/notes.html",
    ),
    "notes": PostTypeConfig(
        name="Notes",
        list_items_per_page=50,
        card_template="posts/cards/vertical.html",
        list_template="posts/lists/notes.html",
        show_template="posts/full/notes.html",
    ),
}


def post_config_by_type(post_type):
    if post_type in POST_TYPES:
        return POST_TYPES[post_type]
    else:
        return PostTypeConfig()


INDEX_PAGE_BEST_POSTS = [
    "organizational-design-key-to-company-success",
]
