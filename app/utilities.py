from flask import url_for


class Pager:
    def __init__(self, term_list, page, per_page, total_pages):
        self.term_list = term_list
        self.page = page
        self.per_page = per_page
        self.total_pages = total_pages
        self.next_page = term_list.next_num if term_list.has_next else None
        self.prev_page = term_list.prev_num if term_list.has_prev else None

    @property
    def pages(self):
        return int(self.total_pages / self.per_page) + (
            self.total_pages % self.per_page > 0
        )

    @property
    def next_url(self):
        return (
            url_for("term.list_alphabetical", page=self.next_page)
            if self.next_page
            else None
        )

    @property
    def prev_url(self):
        return (
            url_for("term.list_alphabetical", page=self.prev_page)
            if self.prev_page
            else None
        )

    @property
    def page_count(self):
        return self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (
                    num > self.page - left_current - 1
                    and num < self.page + right_current
                )
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num

    def __iter__(self):
        return iter(self.iter_pages())

    def __repr__(self):
        return "<Pager %s>" % self.page
