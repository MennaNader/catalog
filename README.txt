# Catalog

This is my submission for the Build an item Catalog for the udacity's fullstack development nanodegree.

#### This porject runs on port 8000

To run the program:

- make sure you using the course's vm after downloading both vagrant and virtual box
`https://github.com/udacity/fullstack-nanodegree-vm`
- you then will need to setup the news database found in the initialdata.py. run `python initialdata.py` to generate the data.
- run `python application.py`.

## What You're Getting

```bash
├── README.md - This file.
├── application.py - # the application endpoints and logic.
├── templates - # the html files for each view.
└── initialdata.py # intial data for the catalog.
```


## Project summary

- user can sign in with Google account. `http://localhost:8000/login`
- user can sign up with email and password. `http://localhost:8000/signup`
- user can log out. `http://localhost:8000/logout`
- user can check catalog categories. `http://localhost:8000/`
- user can check catalog category items (only if he is signed in). `http://localhost:8000/catalog/<category_id>/`
- user can edit category (only if he is signed in). `http://localhost:8000/catalog/<category_id>/edit/`
- user can delete category (only if he is signed in). `http://localhost:8000/catalog/<category_id>/delete/`
- user can add category (only if he is signed in). `http://localhost:8000/catalog/new/`
- user can edit category item (only if he is signed in). `http://localhost:8000/catalog/<category_id>/item/<item_id>/edit/`
- user can delete gcategory item (only if he is signed in). `http://localhost:8000/catalog/<category_id>/item/<item_id>/delete/`
- user can add category item (only if he is signed in). `http://localhost:8000/catalog/<category_id>/item/new/`


### Project contains JSON APIs 
- user can check catalog categories. `http://localhost:8000/JSON/`
- user can check catalog category items (only if he is signed in). `http://localhost:8000/catalog/<category_id>/JSON/`
- user can edit category (only if he is signed in). `http://localhost:8000/catalog/<category_id>/edit/JSON/`
- user can delete category (only if he is signed in). `http://localhost:8000/catalog/<category_id>/delete/JSON/`
- user can add category (only if he is signed in). `http://localhost:8000/catalog/new/JSON/`
- user can edit category item (only if he is signed in). `http://localhost:8000/catalog/<category_id>/item/<item_id>/edit/JSON/`
- user can delete gcategory item (only if he is signed in). `http://localhost:8000/catalog/<category_id>/item/<item_id>/delete/JSON/`
- user can add category item (only if he is signed in). `http://localhost:8000/catalog/<category_id>/item/new/JSON/`