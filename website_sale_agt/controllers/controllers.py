# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL
import logging

_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 2  # Products Per Row


class TableCompute(object):

    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= PPR:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, categories, ppg=PPG):
        # Compute categories positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        x = 0
        for c in categories:
            x = min(max(c.website_size_x, 1), PPR)
            y = min(max(c.website_size_y, 1), PPR)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % PPR, pos // PPR, x, y):
                pos += 1
            # if 21st categories (index 20) and the last line is full (PPR categories in it), break
            # (pos + 1.0) / PPR is the line where the category would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) // PPR) > maxy:
                break

            if x == 1 and y == 1:  # simple heuristic for CPU optimization
                minpos = pos // PPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos // PPR) + y2][(pos % PPR) + x2] = False
            self.table[pos // PPR][pos % PPR] = {
                'category': c, 'x': x, 'y': y,
                'class': " ".join(x.html_class for x in c.website_style_ids if x.html_class)
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos // PPR))
            index += 1

        # Format table according to HTML needs
        rows = sorted(self.table.items())
        rows = [r[1] for r in rows]
        for col in range(len(rows)):
            cols = sorted(rows[col].items())
            x += len(cols)
            rows[col] = [r[1] for r in cols if r[1]]

        return rows


class WebsiteSaleBrands(WebsiteSale):
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
    ], type='http', auth="public", website=True)
    def brand(self, page=0, search='', ppg=False, **post):
        url = "/shop"
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        Category = request.env['product.public.category']
        domain = [('parent_id', '=', False)]
        keep = QueryURL('/shop', search=search)
        if search:
            post["search"] = search
            for srch in search.split(" "):
                domain += [('name', 'ilike', srch)]
        category_count = Category.search_count(domain)
        pager = request.website.pager(url=url, total=category_count, page=page, step=ppg, scope=7, url_args=post)
        categs = Category.search(domain, limit=ppg, offset=pager['offset'])

        values = {
            'search': search,
            'pager': pager,
            'categories': categs,
            'bins': TableCompute().process(categs, ppg),
            'rows': PPR,
            'keep': keep,
        }
        return request.render("website_sale_agt.categories", values)
