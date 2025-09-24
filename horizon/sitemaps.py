from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse


class StaticViewSitemap(Sitemap):

    def items(self):
        all_paths = [
            'signup',
            'not_available_in_your_country',
            'affiliates',
        ]
        return all_paths


    def location(self, item):
        return reverse(item)
