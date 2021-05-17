# Book Review Crawler

This book reviews crawler scrapes all the books' info, users' reviews, comments for the reviews on all pages from this [site](https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh?page=1&per_page=30). The result is stored in `bookreviews.json`

Scrapy and Selenium are required to run the crawler. It is recommended that they are installed in a virtual environment.

Usage
-----
`scrapy crawl goodreads -o <output file>`
