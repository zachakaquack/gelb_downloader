# gelb_downloader

A simple app to download and sort through images downloaded by Gelbooru.

This all started because I wanted to find a bunch of random images off of Gelbooru, for backgrounds, and it ended up here.

Fully supports the tag searching within Gelbooru, as well as many file types (`.png`, `.jpg`, `.jpeg`, `.mp4`, `.gif`, etc). For example:

`{one_piece ~ soul_eater} rating:general` would search for posts rated general for either one_piece OR soul eater.

for more information on searching, check out [howto:cheatsheet](https://gelbooru.com/index.php?page=wiki&s=&s=view&id=26263).

# Some Screenshots
![The main look of the program.](/assets/images/main_program.png)

![How searching works.](/assets/images/searching.png)

# Installation
- download and run `main.py` once
- open up  `~/.config/gelbooru-downloader/config.json` (windows: `C:/Users/{USER}/.config/gelbooru-downloader/config.json`)
- input your API key and user ID in `["user_info"]["api_key"]` and `["user_info"]["user_id"]` respectively - [How to find your API key & user ID](https://github.com/zachakaquack/gelb_downloader?tab=readme-ov-file#how-to-find-your-api-key-and-user-id)
- run `main.py` again, and now you can search!

# How to find your API key and user ID
- create a gelbooru account - linked here.
- go to your [account page](https://gelbooru.com/index.php?page=account&s=options), scroll to the very bottom, and copy the text in API Access Credentials.
- if the text says `&api_key=testapikey&user_id=7279641`, then your API key is `testapikey` and your user ID is `7279641`.

# TODO
- [x] General Code Cleanup
- [x] Removing searches from history
- [ ] Custom directories for downloads, saved images, and deleted images
- [ ] Adding your API key & user ID without going into the .json
- [x] Help menu for searching
