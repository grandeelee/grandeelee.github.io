{% raw %}
# Seminar 4 – Build a Shopping Site from Scratch (Seminar 1 to 3 in One Go)

In this walkthrough you will build, **from an empty folder**, a small but real Flask web application: an online shop called **ESSENTIALS**.

By the end you will have a site where visitors can:

- browse products that are stored in a **MongoDB database**,
- **register** an account and **log in / log out**,
- **add products to a cart** (only when logged in),

…and the code will be organised in the same *model / controller / templates* structure that the `staycation` project uses.

The visual design is the "Minimalist Shop" page from **Seminar 2**. The form handling, database and login parts come from **Seminar 1** and **Seminar 3**.

---

## Table of contents

| Step | What you build | Comes from |
|---|---|---|
| [0](#step-0--the-big-picture) | The big picture (how a web app works) | – |
| [1](#step-1--virtual-environment-packages-and-pip-freeze) | Virtual environment, installing packages, `pip freeze` | Seminar 1 |
| [2](#step-2--the-flask-skeleton-one-endpoint) | Flask skeleton: `__init__.py` + **one** endpoint | Seminar 1 |
| [3](#step-3--templates-jinja-and-static-files) | Templates, Jinja, static files → the shop front page | Seminar 2 |
| [4](#step-4--login-and-register-forms) | Login and register forms | Seminar 1 + Seminar 3 |
| [5](#step-5--redirect-render_template-and-flash) | `redirect`, `render_template`, `url_for`, `flash`, URL variables | Seminar 2 |
| [6](#step-6--the-database-mongodb--mongoengine) | The database (MongoDB + MongoEngine) | Seminar 3 |
| [7](#step-7--flask-login) | Flask-Login: real logins, protected pages, a cart | Seminar 3 |
| [8](#step-8--blueprints-and-a-proper-folder-structure) | Blueprints and reorganising into `models/` + `controllers/` | Seminar 3 / staycation |
| [End](#the-finished-project) | Final layout, URLs to try, troubleshooting, glossary | – |

### How to use this document

- Work **top to bottom**. Each step builds on the previous one.
- Every code block has a **file name** above it. Create or replace that file with exactly that content.
- Every step ends with a **✅ Checkpoint**. Do not move on until the checkpoint works – bugs are far easier to find when you have only changed a little.
- Commands are for **Linux / macOS** (bash). Windows equivalents are given where they differ.
- Lines starting with `$` are things you type in a terminal (don't type the `$`).

---

## Step 0 – The big picture

Before writing code, here is the mental model. A web app is a **conversation** between a browser and a server:

```
   Browser                                        Your Flask app
   -------                                        --------------
   "GET /login please"        ───request──►       finds the function registered for /login
                                                  (a "view function" / "route")
                                                  runs it, builds an HTML page
   shows the page             ◄──response──       "200 OK  +  <html>…</html>"
```

- A **request** has a *URL* (`/login`), a *method* (usually `GET` = "give me a page" or `POST` = "here is some form data") and possibly data.
- A **response** has a *status code* (`200` OK, `302` redirect, `404` not found, `400` bad request) and usually some HTML.
- **Flask** is the Python library that lets you say: *"when a request for `/login` arrives, run this Python function and send back whatever it returns."*

The pieces you will meet, and where they live in the final project:

| Piece | Job | Final location |
|---|---|---|
| **Route / view function** | Receives a request, decides what to do, returns a response | `controllers/` |
| **Template** (Jinja + HTML) | The HTML skeleton with `{{ holes }}` that Python fills in | `templates/` |
| **Model** | Python class that describes a thing stored in the database (User, Product) | `models/` |
| **Form** | Python class that describes an HTML form and validates what the user typed | `models/forms.py` |
| **Static files** | CSS, images, JavaScript – sent to the browser as-is | `assets/` |

---

## Step 1 – Virtual environment, packages and `pip freeze`

### 1.1 Why a virtual environment?

Python packages (like Flask) are installed *somewhere*. If you install everything globally, two projects that need different versions of Flask will fight each other. A **virtual environment** ("venv") is a private folder that holds *this project's* Python packages only. 

### 1.2 Check Python

```bash
$ python3 --version
```

You should see `Python 3.10` or newer (this walkthrough was tested on 3.12). On Windows use `python` instead of `python3`.

### 1.3 Create the project folder and the venv

```bash
$ mkdir shop-site
$ cd shop-site
$ python3 -m venv venv
```

- `mkdir shop-site` / `cd shop-site` – make the project folder and go inside it. **Everything in this walkthrough happens inside `shop-site/`.**
- `python3 -m venv venv` – "run Python's built-in `venv` module and create an environment in a folder called `venv`". You now have a `venv/` folder. You never edit anything in it.

### 1.4 Activate it

```bash
# Linux / macOS
$ source venv/bin/activate

# Windows (Command Prompt)
> venv\Scripts\activate.bat

# Windows (PowerShell)
> venv\Scripts\Activate.ps1
```

Your prompt now starts with `(venv)`. That means: *"`python` and `pip` now refer to this project's private copies."*

> ⚠️ **You must activate the venv in every new terminal window.** If you get `ModuleNotFoundError: No module named 'flask'` later, 90 % of the time you forgot this.
> To leave the venv: type `deactivate`.

### 1.5 Get the pinned `requirements.txt`

Your seminar provides a `requirements.txt`. Copy it into `shop-site/`:

Its contents:

```text
blinker==1.7.0
click==8.1.7
dnspython==2.6.1
email-validator==2.1.0.post1
Flask==2.2.5
Flask-Login==0.6.3
flask-mongoengine==1.0.0
Flask-WTF==1.2.1
idna==3.6
itsdangerous==2.1.2
Jinja2==3.1.3
MarkupSafe==2.1.5
mongoengine==0.27.0
pymongo==4.6.1
Werkzeug==3.0.1
WTForms==3.1.2
```

Each line is `package==exact.version`. Pinning exact versions matters because libraries change: a newer Flask or `flask-mongoengine` may behave differently or refuse to import at all. With these pins **everyone gets the same working combination**.

Only five of these are packages we ask for directly; the rest are *their* dependencies:

| Package | What it is for | Used from |
|---|---|---|
| **Flask** (+ Werkzeug, Jinja2, click, itsdangerous, blinker, MarkupSafe) | The web framework itself | Step 2 |
| **Flask-WTF** (+ WTForms) | Forms and CSRF protection | Step 4 |
| **email-validator** (+ dnspython, idna) | Lets the form check that an email looks valid | Step 4 |
| **flask-mongoengine** (+ mongoengine, pymongo) | Talk to MongoDB using Python classes | Step 6 |
| **Flask-Login** | Remember who is logged in | Step 7 |

### 1.6 Install everything and check with `pip freeze`

```bash
(venv) $ pip install -r requirements.txt
```

`-r` means "read the list of packages from this file". `pip` is Python's package installer; it downloads each package at exactly the pinned version.

Now compare what is installed with the file:

```bash
(venv) $ pip freeze
```

`pip freeze` prints every installed package with its **exact version**, in the same format as `requirements.txt`. The output should be the same 16 lines shown above.

You would use `pip freeze` to *create* a requirements file for your own project:

```bash
(venv) $ pip freeze > requirements.txt
```

`>` means "send the output into this file instead of the screen". Anyone (including *you* in six months, or your tutor) can then rebuild the identical environment with:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

This is why the seminars ship a `requirements.txt`. **If you ever `pip install` an extra package, re-run `pip freeze > requirements.txt`** so the file stays accurate.

> Tip: if you use git, add a `.gitignore` containing the line `venv/` – never commit the venv itself, only `requirements.txt`.

### ✅ Checkpoint 1

<video src="checkpoint-1.webm" controls muted width="100%"></video>

```bash
(venv) $ python -c "import flask; print(flask.__version__)"
```

prints `2.2.5`, and `pip freeze | diff - requirements.txt` prints nothing (no differences; on Windows just compare the two lists by eye).

```text
shop-site/
├── venv/               ← private packages (don't touch)
└── requirements.txt
```

---

## Step 2 – The Flask skeleton (one endpoint)

Now the smallest possible Flask app. We use the same **two-file layout** as Seminars 1–3:

- `app/__init__.py` – *creates* the Flask application object.
- `app/app.py` – *defines the routes* (the endpoints).
- `app/start.sh` – one command to run the server.

### 2.1 Create the `app` package

```bash
(venv) $ mkdir app
```

### 2.2 `app/__init__.py` – create the application

**`app/__init__.py`**

```py
from flask import Flask


def create_app():
    app = Flask(__name__)
    return app


app = create_app()
```

What this does:

- A folder containing a file called `__init__.py` is a Python **package**. That means other files can write `from app import ...` to import things defined in this file.
- `Flask(__name__)` creates the application. `__name__` tells Flask where this package lives so it can later find your `templates/` folder.
- We wrap creation in a function `create_app()` (the *application factory* pattern used in every lab) and then call it once: `app = create_app()`. Every other file can now do `from app import app` to get *the* application.

### 2.3 `app/app.py` – the one endpoint

**`app/app.py`**

```py
from app import app


@app.route("/")
def home():
    return "Hello from the shop!"
```

- `from app import app` – get the application object created in `__init__.py`.
- `@app.route("/")` is a **decorator**. It tells Flask: *"when someone requests the URL `/`, call the function directly below."*
- The function's `return` value becomes the **response body**. Right now it's plain text.

That is a complete web app: **one URL, one function**.

### 2.4 `app/start.sh` – how to run it

**`app/start.sh`**

```bash
export FLASK_APP=app.py; export PYTHONPATH=.; export FLASK_DEBUG=1;
flask run --host=0.0.0.0
```

Each part means:

| Part | Meaning |
|---|---|
| `export FLASK_APP=app.py` | Tell the `flask` command which file contains the routes. |
| `export PYTHONPATH=.` | Add the current folder (`.`) to Python's import search path, so later we can write `from forms import ...` and `from models.users import ...`. |
| `export FLASK_DEBUG=1` | Debug mode: the server **auto-restarts when you save a file** and shows a helpful error page instead of a blank "Internal Server Error". *Never use this on a real public website.* |
| `flask run --host=0.0.0.0` | Start the development server. `0.0.0.0` lets other devices on your network reach it; use `--host=127.0.0.1` (or drop the option) to keep it private to your computer. |

> **Windows:** replace the first line with these (PowerShell) and then run `flask run`:
> ```powershell
> $env:FLASK_APP="app.py"; $env:PYTHONPATH="."; $env:FLASK_DEBUG="1"
> ```

### 2.5 Run it

**Always run from inside the `app/` folder:**

```bash
(venv) $ cd app
(venv) $ bash start.sh
```

Output ends with something like:

```text
 * Running on http://127.0.0.1:5000
```

Open <http://127.0.0.1:5000/> in your browser. You should see **Hello from the shop!**

Stop the server with `Ctrl + C`.

### 2.6 A note on the odd-looking `from app import app`

You have a *folder* called `app` (the package) that contains a *file* called `app.py`. When Flask loads `app.py` it does so as the module `app.app` (file `app.py` inside package `app`). Inside it, `from app import app` means "from the **package** `app` (i.e. `__init__.py`) import the **variable** `app`". Confusing names, but it works – and it is exactly how Seminars 1–3 and `staycation` are set up, so we keep it.

One consequence: **start the server with `flask run` (via `start.sh`), not with `python app.py`**, otherwise Python will find `app.py` when it looks for the package `app` and the import breaks.

### ✅ Checkpoint 2

<video src="checkpoint-2.webm" controls muted width="100%"></video>

The browser shows "Hello from the shop!" and the terminal shows a log line like `"GET / HTTP/1.1" 200 -`. That log line *is* the request/response conversation from Step 0.

Try <http://127.0.0.1:5000/nothing> – you get **404 Not Found**, because no function is registered for that URL.

```text
shop-site/
├── venv/
├── requirements.txt
└── app/
    ├── __init__.py
    ├── app.py
    └── start.sh
```

---

## Step 3 – Templates, Jinja and static files

Returning strings from Python doesn't scale to a whole web page. Instead we keep the HTML in **template** files and let Flask fill in the blanks. The template language is **Jinja**.

We will use the page design from **Seminar 2** (`lab2/app/templates/base.html` and `shopping.html`).

### 3.1 Two new folders

```bash
(venv) $ mkdir templates
(venv) $ mkdir -p assets/css
```

(You are still inside `app/`.)

- `templates/` – Flask looks here for HTML templates automatically.
- `assets/` – our **static files** (CSS, images, JS). Flask's default name for this folder is `static`; Seminars 1–3 rename it to `assets`, so we do too.

Tell Flask about the rename in `__init__.py`:

**`app/__init__.py`**

```py
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.static_folder = "assets"  # serve CSS/JS/images from ./assets instead of ./static
    return app


app = create_app()
```

### 3.2 The CSS – `app/assets/css/custom.css`

In Seminar 2 the CSS lived in a `<style>` tag inside `base.html`. It is tidier to keep it in its own file:

**`app/assets/css/custom.css`**

```css
/* Custom CSS adjustments for a vanilla, elegant aesthetic */
body {
  background-color: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.navbar {
  border-bottom: 1px solid #eaeaea;
}

.product-card {
  border: 1px solid #eaeaea;
  background-color: #ffffff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
}

.product-img-placeholder {
  background-color: #f1f1f1;
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

footer {
  border-top: 1px solid #eaeaea;
  background-color: #ffffff;
}
```

### 3.3 The base template – `app/templates/base.html`

Every page on the shop shares the same header (navbar) and footer. Instead of copy-pasting them into every file, we write them **once** in a *base template* and mark the changing part with a **block**:

**`app/templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Essentials{% endblock %}</title>
  <!-- Bootstrap 5 CSS + Bootstrap Icons via CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <!-- our own CSS, served from the "assets" folder -->
  <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
</head>
<body>

  <!-- Header / navbar -->
  <nav class="navbar navbar-expand-lg navbar-light bg-white sticky-top py-3">
    <div class="container">
      <a class="navbar-brand fw-bold text-dark" href="/">ESSENTIALS</a>

      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
        <ul class="navbar-nav align-items-center">
          <li class="nav-item px-2"><a class="text-dark text-decoration-none" href="/">Shop All</a></li>
          <li class="nav-item ps-3">
            <a class="btn btn-outline-dark btn-sm rounded-pill px-3 position-relative" href="#">
              <i class="bi bi-bag me-1"></i> Cart
              <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-dark">0</span>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Each child page fills in this block -->
  {% block content %}{% endblock %}

  <!-- Footer -->
  <footer class="text-center text-muted py-4 mt-5">
    <div class="container">
      <p class="small mb-1">&copy; 2026 Essentials Studio. All rights reserved.</p>
    </div>
  </footer>

  <!-- Bootstrap JS (needed for the collapsing navbar on phones) -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

The Jinja parts (everything else is ordinary HTML):

| Syntax | Meaning |
|---|---|
| `{% block title %}Essentials{% endblock %}` | A named hole. Child pages can replace it; if they don't, the default text "Essentials" is used. |
| `{% block content %}{% endblock %}` | The main hole where each page puts its own content. |
| `{{ url_for('static', filename='css/custom.css') }}` | Builds the URL of a static file: `/static/css/custom.css`. Better than typing the path by hand because Flask works it out for you. |

Two small improvements over Seminar 2: we added the **Bootstrap Icons** stylesheet (Seminar 2 used `<i class="bi bi-bag">` icons but never loaded the icon CSS, so they were invisible) and the Bootstrap **JavaScript** so the mobile navbar button works.

### 3.4 The shop page – `app/templates/shopping.html`

**`app/templates/shopping.html`**

```html
{% extends "base.html" %}

{% block title %}Shop All{% endblock %}

{% block content %}
<main class="container my-5 py-4">
  <div class="row g-4 row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4">

    {% for product in products %}
    <div class="col">
      <div class="card h-100 product-card rounded-0">
        <div class="product-img-placeholder">
          <i class="bi bi-image fs-3"></i>
        </div>
        <div class="card-body d-flex flex-column p-4">
          <h5 class="card-title fs-6 fw-bold mb-1">{{ product.name }}</h5>
          <p class="text-muted small mb-3">{{ product.desc }}</p>
          <div class="d-flex justify-content-between align-items-center mt-auto">
            <span class="fw-semibold">${{ "%.2f"|format(product.price) }}</span>
            <button class="btn btn-dark btn-sm rounded-0 px-3">Add</button>
          </div>
        </div>
      </div>
    </div>
    {% else %}
    <p class="text-muted">No products yet.</p>
    {% endfor %}

  </div>
</main>
{% endblock %}
```

New Jinja ideas here:

| Syntax | Meaning |
|---|---|
| `{% extends "base.html" %}` | "Start from `base.html`, then fill in its blocks." Must be the first line. |
| `{% for product in products %}…{% else %}…{% endfor %}` | Loop over a list. The `else` part runs only if the list is empty. |
| `{{ product.name }}` | Print a value. Works for dict keys (`product["name"]`) and object attributes alike. |
| `{{ "%.2f"\|format(product.price) }}` | Apply a **filter** (`format`) to a value. Here: show 79.0 as `79.00`. |

Jinja automatically **escapes** anything inside `{{ }}` (turns `<` into `&lt;`), so a product called `<script>` cannot inject code into your page. This is a built-in security feature.

### 3.5 Send data to the template – `app/app.py`

`render_template("file.html", name=value, ...)` loads the template and fills it in. Every keyword argument becomes a variable inside the template.

**`app/app.py`**

```py
from app import app
from flask import render_template


@app.route("/")
def home():
    my_products = [
        {"name": "Linen Shirt", "desc": "Breathable, relaxed fit.", "price": 79.0},
        {"name": "Canvas Tote", "desc": "Sturdy everyday bag.", "price": 35.5},
        {"name": "Ceramic Mug", "desc": "Hand-glazed, 350 ml.", "price": 18.0},
        {"name": "Wool Beanie", "desc": "Soft merino blend.", "price": 24.9},
    ]
    return render_template("shopping.html", products=my_products)
```

The list of dictionaries is fake data – in Step 6 it will come from a real database. The template won't need to change much, which is the whole point of separating the two.

### ✅ Checkpoint 3

<video src="checkpoint-3.webm" controls muted width="100%"></video>

```bash
(venv) $ bash start.sh
```

Open <http://127.0.0.1:5000/>. You should see the ESSENTIALS navbar and four product cards with prices such as `$79.00`. Also try <http://127.0.0.1:5000/static/css/custom.css> – you should see the raw CSS (this proves the `assets` folder is being served).

If the page is unstyled, check the browser's developer tools (F12 → Network) to see whether `custom.css` returned 200 or 404.

```text
app/
├── __init__.py
├── app.py
├── start.sh
├── assets/
│   └── css/custom.css
└── templates/
    ├── base.html
    └── shopping.html
```

---

## Step 4 – Login and register forms

### 4.1 The plain-HTML way (Seminar 1)

In Seminar 1 the login page was an HTML `<form>` and the route read the values with `request.form`:

```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")          # show the empty form
    elif request.method == "POST":
        email = request.form.get("email")             # read what the user typed
        password = request.form.get("password")
        ...
```

Key facts:

- A route accepts only `GET` unless you say otherwise. A form that **submits** data uses `POST`, so the route must declare `methods=["GET", "POST"]`.
- `GET` = show the form. `POST` = the user pressed the button; the data is in `request.form`.

This works but you'd have to write all the checks yourself ("is the email really an email?", "is the password empty?", "do the two passwords match?") *and* the HTML for every error message. That's what **Flask-WTF / WTForms** (Seminar 3) is for.

### 4.2 The packages for this step

Nothing to install – **Flask-WTF** and **email-validator** came with `requirements.txt` in Step 1. (If you get an `ImportError` mentioning either of them, your venv is not activated or you skipped `pip install -r requirements.txt`.)

- **Flask-WTF** (which brings **WTForms**) – define forms as Python classes.
- **email-validator** – needed by WTForms' `Email()` check. Without it you get an `ImportError` the first time the form is used.

### 4.3 A secret key

Flask-WTF protects every form against **CSRF** (a malicious website secretly making your browser submit a form to *our* site). It does this with a hidden random token that is signed with the app's **secret key**. So we must set one in `__init__.py`:

**`app/__init__.py`**

```py
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.static_folder = "assets"  # serve CSS/JS/images from ./assets instead of ./static
    app.secret_key = "change-me-later"  # needed by Flask-WTF (CSRF) and, later, flash() and sessions
    return app


app = create_app()
```

> In a real deployment the secret key must be long, random and **not** stored in your code. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` and load it from an environment variable. For this seminar, a placeholder is fine.

### 4.4 Describe the forms – `app/forms.py`

**`app/forms.py`**

```py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    submit = SubmitField("Register")
```

Read a form class like a shopping list of fields:

- `StringField`, `PasswordField`, `BooleanField` (a checkbox), `SubmitField` (the button) – one per HTML input type. The first argument is the **label** text.
- `validators=[...]` – the rules. `DataRequired()` = must not be empty. `Email()` = must look like an email. `Length(min=6)` = at least 6 characters. `EqualTo("password")` = must be identical to the `password` field.
- Field names (`email`, `password`, …) become the HTML `name` attributes and the attributes you read later: `form.email.data`.

### 4.5 A reusable template snippet – `app/templates/_render_field.html`

Each input needs a label, the input, and its error messages. Instead of typing that for every field (Seminar 3's `login.html` repeats it), we write a Jinja **macro** – a function for templates:

**`app/templates/_render_field.html`**

```html
{# A Jinja "macro" is a reusable template function. #}
{% macro render_field(field) %}
  <div class="mb-3">
    {{ field.label(class="form-label") }}
    {{ field(class="form-control" ~ (" is-invalid" if field.errors else "")) }}
    {% for msg in field.errors %}
      <div class="invalid-feedback">{{ msg }}</div>
    {% endfor %}
  </div>
{% endmacro %}
```

`field.errors` is a list of error messages; it is empty until validation fails. The name starts with `_` only as a convention meaning "helper, not a full page".

### 4.6 The login and register pages

**`app/templates/login.html`**

```html
{% extends "base.html" %}
{% from "_render_field.html" import render_field %}

{% block title %}Login{% endblock %}

{% block content %}
<main class="container my-5" style="max-width: 480px;">
  <h1 class="h3 mb-4">Login</h1>

  <form method="POST" novalidate>
    {{ form.hidden_tag() }}  {# the hidden CSRF token #}

    {{ render_field(form.email) }}
    {{ render_field(form.password) }}

    <div class="form-check mb-3">
      {{ form.remember_me(class="form-check-input") }}
      {{ form.remember_me.label(class="form-check-label") }}
    </div>

    {{ form.submit(class="btn btn-dark w-100") }}
  </form>

  <p class="small text-muted mt-3">No account? <a href="/register">Register</a></p>
</main>
{% endblock %}
```

**`app/templates/register.html`**

```html
{% extends "base.html" %}
{% from "_render_field.html" import render_field %}

{% block title %}Register{% endblock %}

{% block content %}
<main class="container my-5" style="max-width: 480px;">
  <h1 class="h3 mb-4">Create an account</h1>

  <form method="POST" novalidate>
    {{ form.hidden_tag() }}

    {{ render_field(form.name) }}
    {{ render_field(form.email) }}
    {{ render_field(form.password) }}
    {{ render_field(form.confirm) }}

    {{ form.submit(class="btn btn-dark w-100") }}
  </form>

  <p class="small text-muted mt-3">Already registered? <a href="/login">Login</a></p>
</main>
{% endblock %}
```

Things to notice:

- `{% from "_render_field.html" import render_field %}` – import the macro.
- `{{ form.hidden_tag() }}` – outputs the hidden CSRF token input. **Forgetting it makes every submission fail validation.**
- `novalidate` on `<form>` – turns off the browser's own pop-up validation so that *our* (WTForms) error messages appear instead.
- The `<form>` has **no `action` attribute**, so the browser posts back to the same URL it is on. (This matters in Step 7.)

### 4.7 The routes – `app/app.py`

**`app/app.py`**

```py
from app import app
from flask import render_template
from forms import LoginForm, RegisterForm


@app.route("/")
def home():
    my_products = [
        {"name": "Linen Shirt", "desc": "Breathable, relaxed fit.", "price": 79.0},
        {"name": "Canvas Tote", "desc": "Sturdy everyday bag.", "price": 35.5},
        {"name": "Ceramic Mug", "desc": "Hand-glazed, 350 ml.", "price": 18.0},
        {"name": "Wool Beanie", "desc": "Soft merino blend.", "price": 24.9},
    ]
    return render_template("shopping.html", products=my_products)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # True only for a POST whose fields all pass validation
        return f"Login form OK for {form.email.data}"
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return f"Register form OK for {form.name.data} <{form.email.data}>"
    return render_template("register.html", form=form)
```

The pattern is the same for both forms and is worth memorising:

```python
form = LoginForm()                       # 1. create the form object
if form.validate_on_submit():            # 2. True only if it's a POST *and* all validators pass
    ...use form.email.data ...           # 3. success path
return render_template("login.html", form=form)   # otherwise (GET, or validation failed): show the form
```

On a `GET` the form is empty. On a failed `POST` the very same `form` object still holds what the user typed and the error messages, so re-rendering the template shows them.

For now a successful submit just returns a string. We'll do something sensible with it in the next step.

Finally, add Login/Register links to the navbar in `templates/base.html`. Find the line with `Shop All` and add two lines after it:

```html
          <li class="nav-item px-2"><a class="text-dark text-decoration-none" href="/">Shop All</a></li>
          <li class="nav-item px-2"><a class="text-secondary text-decoration-none" href="/login">Login</a></li>
          <li class="nav-item px-2"><a class="text-secondary text-decoration-none" href="/register">Register</a></li>
```

(The next step replaces these hard-coded paths with `url_for`.)

### ✅ Checkpoint 4

<video src="checkpoint-4.webm" controls muted width="100%"></video>

Restart the server if it isn't running (`bash start.sh`) and visit <http://127.0.0.1:5000/register>.

1. Press **Register** with everything empty → red "This field is required." under each field.
2. Type `abc` as the email → "Invalid email address."
3. Type different passwords in *Password* and *Confirm* → "Passwords must match".
4. Fill it in correctly → the page shows `Register form OK for …`.

```text
app/
├── __init__.py
├── app.py
├── forms.py                       ← new
├── start.sh
├── assets/css/custom.css
└── templates/
    ├── _render_field.html         ← new
    ├── base.html
    ├── login.html                 ← new
    ├── register.html              ← new
    └── shopping.html
```

---

## Step 5 – `redirect`, `render_template` and `flash`

Seminar 2 is about how a route *responds*. There are two main ways:

| | What it does | Browser sees |
|---|---|---|
| `return render_template("x.html", ...)` | Build a page and send it now | `200 OK` + HTML |
| `return redirect(url_for("other_route"))` | Tell the browser "go to *that* URL instead" | `302 Found` + a `Location` header; the browser then makes a **new** GET request |

### 5.1 Why redirect after a successful form?

At the end of Step 4 a successful `POST` returned a page directly. If the user then presses **F5 / Refresh**, the browser asks *"resubmit the form data?"* and – if they agree – repeats the POST (creating a second account, or ordering twice!). The standard cure is the **Post → Redirect → Get** pattern: after handling a POST, `redirect()` to a normal `GET` page. Refreshing then just reloads that page.

### 5.2 `url_for` – don't hard-code URLs

`url_for("login")` returns the URL of the route whose **function is called `login`**: `"/login"`. If you later change the route to `@app.route("/signin")`, every `url_for("login")` follows automatically, while a hard-coded `"/login"` would silently break. It also works inside templates: `{{ url_for('login') }}`.

### 5.3 URL variables and query strings (Seminar 2)

Seminar 2 experimented with three ways of getting input from the URL. We'll keep them as small "playground" routes so you can try them:

| URL | Route rule | How the value arrives |
|---|---|---|
| `/greet/Ann` | `"/greet/<name>"` | as the function argument `name` (a string) |
| `/add/2/3` | `"/add/<int:a>/<int:b>"` | `int:` converts to numbers; `/add/2/x` gives 404 |
| `/greetWithArgs?friend=bob` | `"/greetWithArgs"` | **query string**: `request.args.get("friend")` |

> Seminar 2's `greetWithArgs` did `request.args.get('friend').title()`. If you visit the page *without* `?friend=…`, `get` returns `None` and `None.title()` **crashes**. We pass a default instead: `request.args.get("friend", "stranger")`.

### 5.4 `flash` – a one-time message

`flash("text")` stores a message in the user's **session** (a small cookie signed with the secret key – another reason the key is needed). On the *next* page, `get_flashed_messages()` returns it and removes it, so it is shown exactly once. Perfect with redirects: *do something → flash("Done!") → redirect → the next page shows "Done!"*.

### 5.5 Update `app/app.py`

We also add a pretend user so you can practise both the "wrong password" and "success" paths *before* we have a database:

**`app/app.py`**

```py
from app import app
from flask import render_template, request, redirect, url_for, flash
from forms import LoginForm, RegisterForm

# A pretend "database" with one user. Step 6 replaces this with real MongoDB.
FAKE_USER = {"email": "demo@shop.com", "password": "password"}


@app.route("/")
def home():
    my_products = [
        {"name": "Linen Shirt", "desc": "Breathable, relaxed fit.", "price": 79.0},
        {"name": "Canvas Tote", "desc": "Sturdy everyday bag.", "price": 35.5},
        {"name": "Ceramic Mug", "desc": "Hand-glazed, 350 ml.", "price": 18.0},
        {"name": "Wool Beanie", "desc": "Soft merino blend.", "price": 24.9},
    ]
    return render_template("shopping.html", products=my_products)


# ---- Playground routes (from lab 2) -------------------------------------------------
@app.route("/greet/<name>")
def greet(name):
    return f"Hello, {name}!"


@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    return str(a + b)


@app.route("/greetWithArgs")
def greetWithArgs():
    name = request.args.get("friend", "stranger").title()
    return redirect(url_for("greet", name=name))


# ---- Login / Register ---------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data != FAKE_USER["email"]:
            form.email.errors.append("Email not found")
        elif form.password.data != FAKE_USER["password"]:
            form.password.errors.append("Password incorrect")
        else:
            flash("You were successfully logged in")
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("Thanks for registering! (Nothing is saved yet.)")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)
```

Notice how validation errors specific to *our* logic are added by hand: `form.email.errors.append("Email not found")`. `_render_field.html` will display them like any other error.

### 5.6 Show flashed messages in `base.html`

Insert this block **just above** the line `<!-- Each child page fills in this block -->`:

```html
  <!-- Flash messages: one-time notes stored in the session -->
  <div class="container mt-3">
    {% with messages = get_flashed_messages() %}
      {% for message in messages %}
        <div class="alert alert-dark alert-dismissible fade show" role="alert">
          {{ message }}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      {% endfor %}
    {% endwith %}
  </div>
```

(`{% with %}` just creates a temporary variable. This is the same idea as the flash block in Seminar 2's `base.html`, dressed up with Bootstrap's alert style.)

### 5.7 Replace hard-coded paths with `url_for`

In **`templates/base.html`** change the four links:

| Old | New |
|---|---|
| `href="/"` (brand, twice: `ESSENTIALS` and `Shop All`) | `href="{{ url_for('home') }}"` |
| `href="/login"` | `href="{{ url_for('login') }}"` |
| `href="/register"` | `href="{{ url_for('register') }}"` |

In **`templates/login.html`** change `href="/register"` → `href="{{ url_for('register') }}"`, and in **`templates/register.html`** change `href="/login"` → `href="{{ url_for('login') }}"`.

### ✅ Checkpoint 5

- <http://127.0.0.1:5000/greet/Ann> → `Hello, Ann!`
- <http://127.0.0.1:5000/add/2/3> → `5`
- <http://127.0.0.1:5000/greetWithArgs?friend=bob> → the address bar changes to `/greet/Bob` (that's the redirect) and you see `Hello, Bob!`
- Register with valid details → you land on the **Login** page with a dark banner "Thanks for registering!". Refresh – the banner is gone (shown once).
- Log in as `demo@shop.com` / `password` → back on the shop page with "You were successfully logged in". A wrong password shows "Password incorrect".
- In the terminal you can see the `302` lines: `"POST /login" 302` followed by `"GET /" 200`.

*Flash messages (shown once):*

<video src="checkpoint-5-flash.webm" controls muted width="100%"></video>

*Register and log in:*

<video src="checkpoint-5-login-register.webm" controls muted width="100%"></video>

---

## Step 6 – The database (MongoDB + MongoEngine)

Right now everything is forgotten when the server restarts and registering doesn't really register anyone. We need **persistent storage**.

### 6.1 What is MongoDB?

MongoDB is a **document database**. Compare with a spreadsheet:

| Spreadsheet idea | MongoDB name | Example |
|---|---|---|
| The whole workbook | **database** | `shop` |
| A sheet | **collection** | `products`, `users` |
| A row | **document** (JSON-like) | `{"name": "Linen Shirt", "price": 79.0}` |
| A column | **field** | `price` |

Every document automatically gets a unique `_id` (an `ObjectId` like `64f1…`). We'll use it later to identify products and users.

**MongoEngine** is a Python library that lets you describe documents as Python classes (like `class Product(db.Document)`) so you can write `Product.objects(name="Desk Lamp")` instead of raw database commands. We use it through a small wrapper called **flask-mongoengine**, which connects MongoEngine to Flask and gives us a `db` object.

### 6.2 Get a MongoDB server running

The Python code only *talks* to MongoDB; a MongoDB **server** must be running on your machine (default port **27017**). Choose one:

**Option A – Docker (quickest if you have Docker):**

```bash
$ docker run -d --name shop-mongo -p 27017:27017 -v shop-mongo-data:/data/db mongo:7
```

`-d` runs it in the background, `-p 27017:27017` exposes the port, `-v …` keeps your data in a Docker volume. Next time: `docker start shop-mongo`. (On Linux you may need `sudo`, or to add yourself to the `docker` group.)

**Option B – Install natively** – follow the official guide for your OS at <https://www.mongodb.com/docs/manual/administration/install-community/> (macOS: `brew tap mongodb/brew && brew install mongodb-community` then `brew services start mongodb-community`; Windows: the MSI installer; Ubuntu: add MongoDB's apt repository, it isn't in the default one).

**Option C – MongoDB Atlas** (free cloud database): create a free cluster at <https://www.mongodb.com/atlas>, then in `__init__.py` (Step 6.4) replace the settings dictionary with `{"host": "mongodb+srv://USER:PASSWORD@YOURCLUSTER.mongodb.net/shop"}`.

**Option D – Use Vocareum** no further action is needed. MongoDB is already set up on Vocareum Lab.

**Check that it is running** (optional but recommended). With Docker:

```bash
$ docker exec -it shop-mongo mongosh
test> show dbs
```

If you get a prompt and a list, MongoDB is alive. Type `exit` to leave.

### 6.3 The packages for this step

Nothing to install – **flask-mongoengine**, **mongoengine** and **pymongo** came with `requirements.txt` in Step 1. **pymongo** is the official low-level MongoDB driver, **mongoengine** builds the "Python classes ↔ documents" layer on top of it, and **flask-mongoengine** plugs that into Flask.

### 6.4 Connect – `app/__init__.py`

**`app/__init__.py`**

```py
from flask import Flask
from flask_mongoengine import MongoEngine


def create_app():
    app = Flask(__name__)
    app.static_folder = "assets"
    app.secret_key = "change-me-later"
    # Settings for MongoDB. The database ("shop") is created on first write.
    app.config["MONGODB_SETTINGS"] = [
        {
            "db": "shop",         # database name
            "host": "localhost",  # where mongod is running
            "port": 27017,        # MongoDB's default port
        }
    ]
    db = MongoEngine(app)  # opens the connection and gives us db.Document, db.StringField, ...
    return app, db


app, db = create_app()
```

`MONGODB_SETTINGS` tells flask-mongoengine where the server is (this is the same setting Seminar 3 used), and `db = MongoEngine(app)` sets up the connection. The connection is made **lazily** (on the first query), so the app will *start* even if MongoDB is off – you'd get the error on the first page that needs data (see Troubleshooting).

The `db` object is what you build models from: `db.Document`, `db.StringField`, `db.FloatField`, … Because `create_app()` now returns two things, the last line is `app, db = create_app()`.

### 6.5 Describe the data – `app/models.py`

**`app/models.py`**

```py
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Document):
    meta = {"collection": "users"}
    email = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    password = db.StringField(required=True)  # stores the HASH, never the plain password

    @staticmethod
    def getUser(email):
        return User.objects(email=email).first()  # None if not found

    @staticmethod
    def createUser(email, name, password):
        user = User.getUser(email)
        if not user:
            user = User(email=email, name=name, password=generate_password_hash(password))
            user.save()
        return user

    def checkPassword(self, password):
        return check_password_hash(self.password, password)  # True / False


class Product(db.Document):
    meta = {"collection": "products"}
    name = db.StringField(required=True, max_length=60)
    description = db.StringField(max_length=300)
    price = db.FloatField(required=True, min_value=0)

    @staticmethod
    def getAllProducts():
        return Product.objects()

    @staticmethod
    def createProduct(name, description, price):
        return Product(name=name, description=description, price=price).save()
```

Line-by-line ideas:

- `class User(db.Document)` – each instance is one document in the collection named in `meta`.
- `db.StringField(required=True, unique=True)` – field types and constraints. `unique=True` makes MongoDB refuse two users with the same email.
- **Passwords are never stored.** `generate_password_hash(password)` (from Werkzeug, which Flask already installed) produces a salted one-way hash such as `scrypt:32768:8:1$…`. To log in we hash what the user typed and compare via `check_password_hash`. Even you, the developer, cannot read anyone's password from the database.
- `@staticmethod` helper methods (`getUser`, `createUser`, …) keep all database code *in the model*, so the routes stay short. This is the style of Seminar 3's `models.py`.
- `.objects(email=email).first()` – "find documents where `email` equals this value; give me the first one, or `None`".
- `Product.objects()` – every product.

> **Why `from app import db`?** The `db` object is created in `__init__.py`, so any model file imports it from the `app` package. This is exactly how Seminar 3's `models.py` does it.

### 6.6 Use the models in the routes – `app/app.py`

**`app/app.py`**

```py
from app import app
from flask import render_template, request, redirect, url_for, flash
from forms import LoginForm, RegisterForm
from models import User, Product


@app.route("/")
def home():
    """Delete all products and insert the sample catalogue."""
    Product.objects.delete()
    samples = [
        ("Linen Shirt", "Breathable, relaxed fit.", 79.0),
        ("Canvas Tote", "Sturdy everyday bag.", 35.5),
        ("Ceramic Mug", "Hand-glazed, 350 ml.", 18.0),
        ("Wool Beanie", "Soft merino blend.", 24.9),
        ("Leather Wallet", "Slim, full-grain leather.", 55.0),
        ("Cotton Socks (3 pack)", "Everyday crew socks.", 15.0),
        ("Desk Lamp", "Warm light, adjustable arm.", 48.0),
        ("Notebook", "A5, 120 pages, dotted.", 9.5),
    ]
    for name, description, price in samples:
        Product.createProduct(name, description, price)

    products = Product.getAllProducts()
    return render_template("shopping.html", products=products)


# ---- Playground routes (from lab 2) -------------------------------------------------
@app.route("/greet/<name>")
def greet(name):
    return f"Hello, {name}!"


@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    return str(a + b)


@app.route("/greetWithArgs")
def greetWithArgs():
    name = request.args.get("friend", "stranger").title()
    return redirect(url_for("greet", name=name))


# ---- Login / Register ---------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.getUser(form.email.data)
        if not user:
            form.email.errors.append("Email not found")
        elif not user.checkPassword(form.password.data):
            form.password.errors.append("Password incorrect")
        else:
            flash(f"Password OK for {user.name} (we don't remember you yet - see step 7)")
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.getUser(form.email.data):
            form.email.errors.append("Email already registered")
        else:
            User.createUser(form.email.data, form.name.data, form.password.data)
            flash("Account created - please log in")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

```

What changed:

- `home()` no longer has a hard-coded list; it asks the database: `Product.getAllProducts()`.
- `register()` first checks that the email isn't taken, then calls `User.createUser(...)`. It really saves now.
- `login()` looks the user up in MongoDB and verifies the hash. (It doesn't *remember* the user yet – that's Step 7.)

The template used `product.desc` for the description; the model calls the field `description`. Update **one line** in `templates/shopping.html`:

```html
          <p class="text-muted small mb-3">{{ product.description }}</p>
```

### ✅ Checkpoint 6

<video src="checkpoint-6.webm" controls muted width="100%"></video>

1. `bash start.sh`, open <http://127.0.0.1:5000/> → **eight** products, loaded from MongoDB.
2. Register a new account. You are sent to the login page.
3. Register the **same email** again → "Email already registered".
4. Log in with a wrong password → "Password incorrect". Log in with the right one → "Password OK for …".
5. Look inside the database:

```bash
$ docker exec -it shop-mongo mongosh
test> use shop
shop> db.users.find()
shop> db.products.find()
```

You will see your user with a long `password` hash (not the plain text!) and the products with their `_id`s.

```text
app/
├── __init__.py          ← MongoEngine(app) + db added
├── app.py               ← uses models
├── models.py            ← new (User, Product)
├── forms.py
├── start.sh
├── assets/css/custom.css
└── templates/  (as before)
```

---

## Step 7 – Flask-Login

Step 6 checks the password but forgets who you are the moment the redirect happens (HTTP is **stateless** – every request is independent). **Flask-Login** solves this: after a successful login it stores the user's id in the signed session cookie, and on each later request it turns that id back into a user object.

### 7.1 The package for this step

Nothing to install – **Flask-Login** came with `requirements.txt` in Step 1.

### 7.2 The four ingredients

1. A **`LoginManager`** attached to the app (`__init__.py`).
2. A **user model** that includes `UserMixin` (gives it `is_authenticated`, `get_id()`, …).
3. A **`user_loader`** function: "given an id from the cookie, return the `User`".
4. The view helpers **`login_user`**, **`logout_user`**, **`current_user`** and the decorator **`@login_required`**.

### 7.3 `app/__init__.py`

**`app/__init__.py`**

```py
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mongoengine import MongoEngine


def create_app():
    app = Flask(__name__)
    app.static_folder = "assets"
    app.secret_key = "change-me-later"
    app.config["MONGODB_SETTINGS"] = [
        {
            "db": "shop",
            "host": "localhost",
            "port": 27017,
        }
    ]
    db = MongoEngine(app)

    CSRFProtect(app)  # every POST must carry a valid CSRF token

    login_manager = LoginManager(app)
    login_manager.login_view = "login"  # where to send visitors who hit a @login_required page
    login_manager.login_message = "Please log in to continue."
    return app, db, login_manager


app, db, login_manager = create_app()
```

- `login_manager.login_view = "login"` – if a not-logged-in visitor opens a `@login_required` page, Flask-Login redirects them to the route named `login` and appends `?next=<where they were going>`.
- `CSRFProtect(app)` – Flask-WTF forms (login/register) already have CSRF tokens. The cart's "Add" button will be a *plain* form, so we switch on CSRF checking for **all** POST requests. Any POST without a valid token now gets **400 Bad Request**.
- The function now returns three things, so the last line unpacks them: `app, db, login_manager = create_app()`.

### 7.4 `app/models.py`

**`app/models.py`**

```py
from flask_login import UserMixin
from mongoengine.errors import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Document):  # UserMixin adds is_authenticated, get_id() etc.
    meta = {"collection": "users"}
    email = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    password = db.StringField(required=True)  # stores the HASH, never the plain password

    @staticmethod
    def getUser(email):
        return User.objects(email=email).first()  # None if not found

    @staticmethod
    def getUserById(user_id):
        try:
            return User.objects(pk=user_id).first()
        except ValidationError:  # user_id is not a valid ObjectId
            return None

    @staticmethod
    def createUser(email, name, password):
        user = User.getUser(email)
        if not user:
            user = User(email=email, name=name, password=generate_password_hash(password))
            user.save()
        return user

    def checkPassword(self, password):
        return check_password_hash(self.password, password)  # True / False


class Product(db.Document):
    meta = {"collection": "products"}
    name = db.StringField(required=True, max_length=60)
    description = db.StringField(max_length=300)
    price = db.FloatField(required=True, min_value=0)

    @staticmethod
    def getProduct(product_id):
        try:
            return Product.objects(pk=product_id).first()
        except ValidationError:
            return None

    @staticmethod
    def getAllProducts():
        return Product.objects()

    @staticmethod
    def createProduct(name, description, price):
        return Product(name=name, description=description, price=price).save()


class CartItem(db.Document):
    meta = {"collection": "cart_items"}
    user = db.ReferenceField(User, required=True)        # whose cart this line belongs to
    product = db.ReferenceField(Product, required=True)  # which product
    quantity = db.IntField(default=1, min_value=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    @staticmethod
    def getCartItems(user):
        return CartItem.objects(user=user)

    @staticmethod
    def getCartItem(user, product):
        return CartItem.objects(user=user, product=product).first()  # None if not in the cart

    @staticmethod
    def countItems(user):
        return CartItem.objects(user=user).sum("quantity")  # total number of units in the cart

    @staticmethod
    def addToCart(user, product):
        item = CartItem.getCartItem(user, product)
        if item:
            item.quantity += 1  # already in the cart: one more
        else:
            item = CartItem(user=user, product=product)
        return item.save()

    @staticmethod
    def removeFromCart(user, product):
        item = CartItem.getCartItem(user, product)
        if item:
            item.delete()
        return item

    @staticmethod
    def clearCart(user):
        CartItem.objects(user=user).delete()


@login_manager.user_loader
def load_user(user_id):
    # Flask-Login calls this on every request, with the id it stored in the session cookie.
    return User.getUserById(user_id)
```

#### The cart lives in MongoDB: the `CartItem` model

Instead of keeping the cart in the browser's cookie, every line of every cart is a **document in its own collection**, `cart_items`. One document = one product in one user's cart:

```json
{ "_id": "…", "user": "<id of Ann>", "product": "<id of Linen Shirt>", "quantity": 2 }
```

- `db.ReferenceField(User)` / `db.ReferenceField(Product)` store the **`_id` of another document** – MongoDB's version of a foreign key. When you write `item.product.name` MongoEngine automatically fetches the referenced product for you. (Seminar 3's `Itinerary` and `Booking` models do the same.)
- `db.IntField(default=1, min_value=1)` – a whole number, at least 1.
- A cart is not a separate object: **Ann's cart is simply "all `CartItem` documents whose `user` is Ann"**: `CartItem.objects(user=ann)`.
- `@property subtotal` – a computed value (price × quantity) that you use like a field: `item.subtotal`. It is not stored in the database.

The helper methods are the four database operations, **CRUD**, applied to the cart:

| Operation | Method | What it does |
|---|---|---|
| **C**reate / **U**pdate | `addToCart(user, product)` | Looks for an existing line for this user + product. If there is one, `quantity += 1` and `save()` (update); if not, creates a new `CartItem` (create). |
| **R**ead | `getCartItems(user)`, `getCartItem(user, product)`, `countItems(user)` | List the user's lines, find one line (or `None`), and add up the quantities with `.sum("quantity")`. |
| **D**elete | `removeFromCart(user, product)`, `clearCart(user)` | Delete one line / every line of that user. |

Because the data is in the database, the cart is **still there after you log out, close the browser, or restart the server**, and each user only ever sees their own lines.

### 7.5 `app/app.py`

**`app/app.py`**

```py
from app import app
from urllib.parse import urlsplit
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm, RegisterForm
from models import User, Product, CartItem


@app.route("/")
def home():
    """Insert the sample catalogue the first time the shop is opened, then list the products."""
    if Product.objects.count() == 0:  # only when the collection is empty - carts point at these products
        samples = [
            ("Linen Shirt", "Breathable, relaxed fit.", 79.0),
            ("Canvas Tote", "Sturdy everyday bag.", 35.5),
            ("Ceramic Mug", "Hand-glazed, 350 ml.", 18.0),
            ("Wool Beanie", "Soft merino blend.", 24.9),
            ("Leather Wallet", "Slim, full-grain leather.", 55.0),
            ("Cotton Socks (3 pack)", "Everyday crew socks.", 15.0),
            ("Desk Lamp", "Warm light, adjustable arm.", 48.0),
            ("Notebook", "A5, 120 pages, dotted.", 9.5),
        ]
        for name, description, price in samples:
            Product.createProduct(name, description, price)
    products = Product.getAllProducts()
    return render_template("shopping.html", products=products)


# ---- Playground routes (from lab 2) -------------------------------------------------
@app.route("/greet/<name>")
def greet(name):
    return f"Hello, {name}!"


@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    return str(a + b)


@app.route("/greetWithArgs")
def greetWithArgs():
    name = request.args.get("friend", "stranger").title()
    return redirect(url_for("greet", name=name))


# ---- Login / Register / Logout ------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:  # already logged in? nothing to do here
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.getUser(form.email.data)
        if not user:
            form.email.errors.append("Email not found")
        elif not user.checkPassword(form.password.data):
            form.password.errors.append("Password incorrect")
        else:
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.name}!")
            # Flask-Login adds ?next=/cart when it bounces you here from a protected page
            next_page = request.args.get("next")
            if not next_page or urlsplit(next_page).netloc:  # reject absolute URLs
                next_page = url_for("home")
            return redirect(next_page)
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.getUser(form.email.data):
            form.email.errors.append("Email already registered")
        else:
            User.createUser(form.email.data, form.name.data, form.password.data)
            flash("Account created - please log in")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("home"))


# ---- Cart (login required) ----------------------------------------------------------
@app.context_processor
def inject_cart_count():
    # Runs before every template is rendered. The dict it returns becomes template variables,
    # so base.html can show {{ cart_count }} without every route passing it in.
    if current_user.is_authenticated:
        return {"cart_count": CartItem.countItems(current_user)}
    return {"cart_count": 0}


@app.route("/cart")
@login_required
def cart():
    items = CartItem.getCartItems(current_user)
    total = sum(item.subtotal for item in items)
    return render_template("cart.html", items=items, total=total)


@app.route("/cart/add/<product_id>", methods=["POST"])
@login_required
def cartAdd(product_id):
    product = Product.getProduct(product_id)
    if not product:
        flash("Sorry, that product does not exist")
        return redirect(url_for("home"))
    CartItem.addToCart(current_user, product)
    flash(f"Added {product.name} to your cart")
    return redirect(url_for("home"))


@app.route("/cart/remove/<product_id>", methods=["POST"])
@login_required
def cartRemove(product_id):
    product = Product.getProduct(product_id)
    if product:
        CartItem.removeFromCart(current_user, product)
    return redirect(url_for("cart"))


@app.route("/cart/clear", methods=["POST"])
@login_required
def cartClear():
    CartItem.clearCart(current_user)
    return redirect(url_for("cart"))
```

The new ideas:

- **`login_user(user, remember=...)`** – log this user in. `remember=True` (the "Remember me" checkbox) also sets a long-lived cookie so they stay logged in after closing the browser.
- **`logout_user()`** – forget the user.
- **`current_user`** – the logged-in `User`, or an "anonymous" object whose `is_authenticated` is `False`. Available in Python *and* in templates.
- **`@login_required`** – put it *under* `@app.route(...)`. Anonymous visitors are redirected to the login page.
- **`?next=`** – after logging in, we send the user to where they were originally headed (e.g. `/cart`). We only accept **relative** URLs (`urlsplit(next).netloc` is empty); otherwise an attacker could craft `…/login?next=http://evil.com` and bounce your users to a fake site (an *open redirect*).
- **The cart is stored in the database**, through the `CartItem` model. The routes stay very short because the model does the work: `CartItem.addToCart(current_user, product)`, `CartItem.getCartItems(current_user)`, `CartItem.removeFromCart(...)`, `CartItem.clearCart(...)`. (`current_user` can be passed straight to a query as "this user".)
- **`@app.context_processor`** – a function whose returned dictionary is added to **every** template automatically. We use it to give `base.html` a `cart_count` variable (the number on the Cart badge) without having to pass it from every route.
- **Only the logged-in user's own lines are touched**: every cart method filters by `user`, so a user cannot add to, view or remove somebody else's cart even by editing the URL.
- **`home()` changed slightly.** In Step 6 it wiped and re-inserted the sample products on *every* visit. That would now break carts: each `CartItem` points at a product's `_id`, and re-inserting creates products with **new** ids, leaving every cart pointing at products that no longer exist. So now the samples are inserted **only if the `products` collection is empty** (`if Product.objects.count() == 0`), i.e. the first time somebody opens the shop.
- Adding to the cart **changes data**, so it is a `POST` route, never a plain link (a link can be triggered by anything, e.g. a search-engine crawler).

### 7.6 `app/templates/base.html` – show who is logged in

This is now the complete, final version of the base template. Replace the file with:

**`app/templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Essentials{% endblock %}</title>
  <!-- Bootstrap 5 CSS + Bootstrap Icons via CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <!-- our own CSS, served from the "assets" folder -->
  <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
</head>
<body>

  <!-- Header / navbar -->
  <nav class="navbar navbar-expand-lg navbar-light bg-white sticky-top py-3">
    <div class="container">
      <a class="navbar-brand fw-bold text-dark" href="{{ url_for('home') }}">ESSENTIALS</a>

      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
        <ul class="navbar-nav align-items-center">
          <li class="nav-item px-2"><a class="text-dark text-decoration-none" href="{{ url_for('home') }}">Shop All</a></li>

          {% if current_user.is_authenticated %}
            <li class="nav-item px-2 text-secondary">Hi, {{ current_user.name }}</li>
            <li class="nav-item px-2"><a class="text-secondary text-decoration-none" href="{{ url_for('logout') }}">Logout</a></li>
          {% else %}
            <li class="nav-item px-2"><a class="text-secondary text-decoration-none" href="{{ url_for('login') }}">Login</a></li>
            <li class="nav-item px-2"><a class="text-secondary text-decoration-none" href="{{ url_for('register') }}">Register</a></li>
          {% endif %}

          <li class="nav-item ps-3">
            <a class="btn btn-outline-dark btn-sm rounded-pill px-3 position-relative" href="{{ url_for('cart') }}">
              <i class="bi bi-bag me-1"></i> Cart
              <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-dark">
                {{ cart_count }}
              </span>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Flash messages: one-time notes stored in the session -->
  <div class="container mt-3">
    {% with messages = get_flashed_messages() %}
      {% for message in messages %}
        <div class="alert alert-dark alert-dismissible fade show" role="alert">
          {{ message }}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      {% endfor %}
    {% endwith %}
  </div>

  <!-- Each child page fills in this block -->
  {% block content %}{% endblock %}

  <!-- Footer -->
  <footer class="text-center text-muted py-4 mt-5">
    <div class="container">
      <p class="small mb-1">&copy; 2026 Essentials Studio. All rights reserved.</p>
    </div>
  </footer>

  <!-- Bootstrap JS (needed for the collapsing navbar on phones) -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

Highlights:

- `{% if current_user.is_authenticated %}…{% else %}…{% endif %}` – show *"Hi, Ann / Logout"* to logged-in users and *Login / Register* to everyone else. This is how Seminar 3's `base.html` behaves.
- The cart badge: `{{ cart_count }}` – the total number of items in the logged-in user's cart, provided by the context processor in `app.py` (it is `0` for visitors who aren't logged in).

### 7.7 `app/templates/shopping.html` – a working "Add" button

The button becomes a tiny form that POSTs to the cart route, with a CSRF token:

**`app/templates/shopping.html`**

```html
{% extends "base.html" %}

{% block title %}Shop All{% endblock %}

{% block content %}
<main class="container my-5 py-4">
  <div class="row g-4 row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4">

    {% for product in products %}
    <div class="col">
      <div class="card h-100 product-card rounded-0">
        <div class="product-img-placeholder">
          <i class="bi bi-image fs-3"></i>
        </div>
        <div class="card-body d-flex flex-column p-4">
          <h5 class="card-title fs-6 fw-bold mb-1">{{ product.name }}</h5>
          <p class="text-muted small mb-3">{{ product.description }}</p>
          <div class="d-flex justify-content-between align-items-center mt-auto">
            <span class="fw-semibold">${{ "%.2f"|format(product.price) }}</span>
            <form method="POST" action="{{ url_for('cartAdd', product_id=product.id) }}">
              <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
              <button type="submit" class="btn btn-dark btn-sm rounded-0 px-3">Add</button>
            </form>
          </div>
        </div>
      </div>
    </div>
    {% else %}
    <p class="text-muted">No products yet.</p>
    {% endfor %}

  </div>
</main>
{% endblock %}
```

`product.id` is the MongoDB `_id`. `url_for('cartAdd', product_id=product.id)` fills the `<product_id>` slot in the route: `/cart/add/64f1a…`.

### 7.8 `app/templates/cart.html` – new page

**`app/templates/cart.html`**

```html
{% extends "base.html" %}

{% block title %}Your Cart{% endblock %}

{% block content %}
<main class="container my-5">
  <h1 class="h3 mb-4">Your cart</h1>

  {% if items %}
  <table class="table align-middle">
    <thead>
      <tr>
        <th>Product</th>
        <th class="text-end">Price</th>
        <th class="text-end">Qty</th>
        <th class="text-end">Subtotal</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {% for item in items %}
      <tr>
        <td>{{ item.product.name }}</td>
        <td class="text-end">${{ "%.2f"|format(item.product.price) }}</td>
        <td class="text-end">{{ item.quantity }}</td>
        <td class="text-end">${{ "%.2f"|format(item.subtotal) }}</td>
        <td class="text-end">
          <form method="POST" action="{{ url_for('cartRemove', product_id=item.product.id) }}">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <button class="btn btn-outline-dark btn-sm rounded-0">Remove</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
    <tfoot>
      <tr><th colspan="3" class="text-end">Total</th><th class="text-end">${{ "%.2f"|format(total) }}</th><th></th></tr>
    </tfoot>
  </table>

  <form method="POST" action="{{ url_for('cartClear') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button class="btn btn-outline-dark btn-sm rounded-0">Empty cart</button>
  </form>
  {% else %}
    <p class="text-muted">Your cart is empty. <a href="{{ url_for('home') }}">Keep shopping</a></p>
  {% endif %}
</main>
{% endblock %}
```

Each row's **Remove** button and the **Empty cart** button are small POST forms with a CSRF token, just like **Add**. `item.product.id` is the id of the referenced product, which `cartRemove` uses to find the right line.

The two other forms need no changes: `login.html` has no `action`, so after Flask-Login bounces you to `/login?next=%2Fcart` the form posts back to that same URL and the `next` value is preserved. *(Seminar 3's login form used `action="/login"`, which would have dropped it.)*

### ✅ Checkpoint 7

<video src="checkpoint-7.webm" controls muted width="100%"></video>

1. Logged out, click **Cart** → you're taken to the login page, and the address bar shows `/login?next=%2Fcart`. A banner says "Please log in to continue."
2. Log in → you land on **/cart** (that's `next` working), which says "Your cart is empty".
3. Go to **Shop All** and click **Add** on two products (one twice). The badge on the Cart button counts up and each click shows "Added … to your cart". Refresh the shop page a few times: the products and your badge stay the same (the products are only inserted once).
4. Open **Cart** → a table with quantities, subtotals and a total. Click **Remove** on one row (that line disappears), or **Empty cart** to clear everything.
5. The navbar says **Hi, \<your name\>**. Add something again, then click **Logout** ("You have been logged out") and **log back in** → your cart is **still there**, because it is stored in MongoDB, not in the cookie.
6. Register a second user in a private/incognito window and add a different product: the two carts stay separate.
7. Look at the data:

```bash
shop> db.cart_items.find()
```

You will see one document per cart line, with `user` and `product` ids and a `quantity`.
8. While logged in, visit <http://127.0.0.1:5000/login> → you're bounced straight back to the shop (`current_user.is_authenticated`).
9. (Optional) In your browser's dev-tools → Application → Cookies, you'll see a `session` cookie: the signed data. Change one character and reload: you're logged out, because the signature no longer matches.

---

## Step 8 – Blueprints and a proper folder structure

`app.py` now contains routes for authentication, the shop, the cart and the demo playground, and `models.py` contains unrelated models. With a real project this becomes unmanageable. We reorganise into the **model / controller / view** layout of the `staycation` project:

| MVC name | Folder | Contains |
|---|---|---|
| **Model** | `models/` | database classes and forms |
| **View** | `templates/` | HTML |
| **Controller** | `controllers/` | the route functions |

### 8.1 What is a Blueprint?

A **Blueprint** is a *named bundle of routes* defined in its own file. You create it, attach routes to it (`@shop.route(...)` instead of `@app.route(...)`), then **register** it with the app in one line. Think of blueprints as chapters of a book and `app.register_blueprint(...)` as adding the chapter to the table of contents.

We will create three:

| Blueprint | File | Routes |
|---|---|---|
| `auth` | `controllers/auth.py` | login, register, logout |
| `shop` | `controllers/shop.py` | home, cart, add to cart, remove from cart, empty cart |
| `demo` | `controllers/demo.py` | the Seminar 2 playground (greet, add, greetWithArgs), mounted under `/demo` |

### 8.2 Do the reorganisation

Inside `app/`:

```bash
(venv) $ mkdir controllers models
(venv) $ mv forms.py models/forms.py        # forms.py moves unchanged
```

Now **split `models.py`** into three files – `users.py`, `product.py` and `cart.py` – then delete the old one (`rm models.py`).

**`app/models/users.py`**

```py
from flask_login import UserMixin
from mongoengine.errors import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Document):  # UserMixin adds is_authenticated, get_id() etc.
    meta = {"collection": "users"}
    email = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    password = db.StringField(required=True)  # stores the HASH, never the plain password

    @staticmethod
    def getUser(email):
        return User.objects(email=email).first()  # None if not found

    @staticmethod
    def getUserById(user_id):
        try:
            return User.objects(pk=user_id).first()
        except ValidationError:  # user_id is not a valid ObjectId
            return None

    @staticmethod
    def createUser(email, name, password):
        user = User.getUser(email)
        if not user:
            user = User(email=email, name=name, password=generate_password_hash(password))
            user.save()
        return user

    def checkPassword(self, password):
        return check_password_hash(self.password, password)  # True / False


@login_manager.user_loader
def load_user(user_id):
    # Flask-Login calls this on every request, with the id it stored in the session cookie.
    return User.getUserById(user_id)
```

**`app/models/product.py`**

```py
from mongoengine.errors import ValidationError
from app import db


class Product(db.Document):
    meta = {"collection": "products"}
    name = db.StringField(required=True, max_length=60)
    description = db.StringField(max_length=300)
    price = db.FloatField(required=True, min_value=0)

    @staticmethod
    def getProduct(product_id):
        try:
            return Product.objects(pk=product_id).first()
        except ValidationError:
            return None

    @staticmethod
    def getAllProducts():
        return Product.objects()

    @staticmethod
    def createProduct(name, description, price):
        return Product(name=name, description=description, price=price).save()
```

**`app/models/cart.py`**

```py
from app import db
from models.users import User
from models.product import Product


class CartItem(db.Document):
    meta = {"collection": "cart_items"}
    user = db.ReferenceField(User, required=True)        # whose cart this line belongs to
    product = db.ReferenceField(Product, required=True)  # which product
    quantity = db.IntField(default=1, min_value=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    @staticmethod
    def getCartItems(user):
        return CartItem.objects(user=user)

    @staticmethod
    def getCartItem(user, product):
        return CartItem.objects(user=user, product=product).first()  # None if not in the cart

    @staticmethod
    def countItems(user):
        return CartItem.objects(user=user).sum("quantity")  # total number of units in the cart

    @staticmethod
    def addToCart(user, product):
        item = CartItem.getCartItem(user, product)
        if item:
            item.quantity += 1  # already in the cart: one more
        else:
            item = CartItem(user=user, product=product)
        return item.save()

    @staticmethod
    def removeFromCart(user, product):
        item = CartItem.getCartItem(user, product)
        if item:
            item.delete()
        return item

    @staticmethod
    def clearCart(user):
        CartItem.objects(user=user).delete()
```

`cart.py` imports `User` and `Product` because it refers to them. `users.py` and `product.py` import neither each other nor `cart.py`, so there are no circular imports.

(`models/forms.py` is exactly the `forms.py` from Step 4.)

### 8.3 The controllers

**`app/controllers/auth.py`**

```py
from urllib.parse import urlsplit
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from models.forms import LoginForm, RegisterForm
from models.users import User

auth = Blueprint("auth", __name__)  # endpoints become auth.login, auth.register, auth.logout


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("shop.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.getUser(form.email.data)
        if not user:
            form.email.errors.append("Email not found")
        elif not user.checkPassword(form.password.data):
            form.password.errors.append("Password incorrect")
        else:
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.name}!")
            next_page = request.args.get("next")
            if not next_page or urlsplit(next_page).netloc:  # reject absolute URLs
                next_page = url_for("shop.home")
            return redirect(next_page)
    return render_template("login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.getUser(form.email.data):
            form.email.errors.append("Email already registered")
        else:
            User.createUser(form.email.data, form.name.data, form.password.data)
            flash("Account created - please log in")
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("shop.home"))
```

**`app/controllers/shop.py`**

```py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from models.product import Product
from models.cart import CartItem

shop = Blueprint("shop", __name__)  # endpoints: shop.home, shop.cart, shop.cartAdd, shop.cartRemove, shop.cartClear


@shop.route("/")
def home():
    """Insert the sample catalogue the first time the shop is opened, then list the products."""
    if Product.objects.count() == 0:  # only when the collection is empty - carts point at these products
        samples = [
            ("Linen Shirt", "Breathable, relaxed fit.", 79.0),
            ("Canvas Tote", "Sturdy everyday bag.", 35.5),
            ("Ceramic Mug", "Hand-glazed, 350 ml.", 18.0),
            ("Wool Beanie", "Soft merino blend.", 24.9),
            ("Leather Wallet", "Slim, full-grain leather.", 55.0),
            ("Cotton Socks (3 pack)", "Everyday crew socks.", 15.0),
            ("Desk Lamp", "Warm light, adjustable arm.", 48.0),
            ("Notebook", "A5, 120 pages, dotted.", 9.5),
        ]
        for name, description, price in samples:
            Product.createProduct(name, description, price)
    products = Product.getAllProducts()
    return render_template("shopping.html", products=products)


@shop.route("/cart")
@login_required
def cart():
    items = CartItem.getCartItems(current_user)
    total = sum(item.subtotal for item in items)
    return render_template("cart.html", items=items, total=total)


@shop.route("/cart/add/<product_id>", methods=["POST"])
@login_required
def cartAdd(product_id):
    product = Product.getProduct(product_id)
    if not product:
        flash("Sorry, that product does not exist")
        return redirect(url_for("shop.home"))
    CartItem.addToCart(current_user, product)
    flash(f"Added {product.name} to your cart")
    return redirect(url_for("shop.home"))


@shop.route("/cart/remove/<product_id>", methods=["POST"])
@login_required
def cartRemove(product_id):
    product = Product.getProduct(product_id)
    if product:
        CartItem.removeFromCart(current_user, product)
    return redirect(url_for("shop.cart"))


@shop.route("/cart/clear", methods=["POST"])
@login_required
def cartClear():
    CartItem.clearCart(current_user)
    return redirect(url_for("shop.cart"))
```

**`app/controllers/demo.py`**

```py
from flask import Blueprint, request, redirect, url_for

demo = Blueprint("demo", __name__)  # registered with url_prefix="/demo" in app.py


@demo.route("/greet/<name>")
def greet(name):
    return f"Hello, {name}!"


@demo.route("/add/<int:a>/<int:b>")
def add(a, b):
    return str(a + b)


@demo.route("/greetWithArgs")
def greetWithArgs():
    name = request.args.get("friend", "stranger").title()
    return redirect(url_for("demo.greet", name=name))
```

The **important new rule**: a blueprint's endpoint name is `blueprintname.functionname`. So `login()` inside the `auth` blueprint is now `auth.login`, and every `url_for` must use the new name: `url_for("auth.login")`, `url_for("shop.home")`. (Inside a blueprint you may also write the shorthand `url_for(".home")`.)

### 8.4 The new `app/app.py`

`app.py` shrinks to "assemble the pieces", plus the context processor that supplies `cart_count` (it needs `app`, so it stays here). Loading the sample products moved into `home()` in `controllers/shop.py`, so nothing has to be run from the command line:

**`app/app.py`**

```py
from app import app
from flask_login import current_user
from models.cart import CartItem
from controllers.auth import auth
from controllers.shop import shop
from controllers.demo import demo

# Register the blueprints so Flask knows about their routes
app.register_blueprint(auth)
app.register_blueprint(shop)
app.register_blueprint(demo, url_prefix="/demo")  # /demo/greet/<name>, /demo/add/2/3, ...


@app.context_processor
def inject_cart_count():
    # Runs before every template is rendered. The dict it returns becomes template variables,
    # so base.html can show {{ cart_count }} without every route passing it in.
    if current_user.is_authenticated:
        return {"cart_count": CartItem.countItems(current_user)}
    return {"cart_count": 0}
```

`url_prefix="/demo"` adds `/demo` in front of every route in that blueprint (`/demo/greet/<name>`) – handy for grouping. `auth` and `shop` have no prefix, so their URLs are unchanged (`/login`, `/`, `/cart`).

### 8.5 Update the endpoint names

**`app/__init__.py`** – one line:

```python
    login_manager.login_view = "auth.login"      # was "login"
```

**Templates** – every `url_for(...)` needs the blueprint prefix. Use your editor's *find & replace* across the `templates/` folder:

| Find | Replace with |
|---|---|
| `url_for('home')` | `url_for('shop.home')` |
| `url_for('cart')` | `url_for('shop.cart')` |
| `url_for('cartAdd'` | `url_for('shop.cartAdd'` |
| `url_for('cartRemove'` | `url_for('shop.cartRemove'` |
| `url_for('cartClear')` | `url_for('shop.cartClear')` |
| `url_for('login')` | `url_for('auth.login')` |
| `url_for('register')` | `url_for('auth.register')` |
| `url_for('logout')` | `url_for('auth.logout')` |

(Leave `url_for('static', …)` alone – `static` belongs to the app itself.)

To double-check that nothing was missed, list what's left:

```bash
$ grep -rn "url_for" templates | grep -v "static\|auth\.\|shop\."
```

It should print nothing.

### 8.6 How the imports fit together

Imports look odd at first, so here is how they resolve when you run `flask run` inside `app/`:

```text
flask loads  app.py  (as module "app.app")
 ├─ from app import app                 → package "app" (__init__.py): creates app + db (MongoEngine) + login_manager
 ├─ from models.product import Product  → app/models/product.py   (found because PYTHONPATH=. = the app/ folder)
 ├─ from controllers.auth import auth   → app/controllers/auth.py
 │     ├─ from models.forms import ...
 │     └─ from models.users import User → ... from app import db, login_manager   (already created above)
 └─ app.register_blueprint(...)         → routes now exist
```

The order matters to avoid **circular imports**: `__init__.py` must *never* import from `models/` or `controllers/` (it only creates things), while models and controllers may import *from* `app`.

### ✅ Checkpoint 8 (final test)

```bash
(venv) $ export FLASK_APP=app.py PYTHONPATH=.
(venv) $ flask routes
```

should list exactly:

```text
Endpoint            Methods    Rule
------------------  ---------  -------------------------
auth.login          GET, POST  /login
auth.logout         GET        /logout
auth.register       GET, POST  /register
demo.add            GET        /demo/add/<int:a>/<int:b>
demo.greet          GET        /demo/greet/<name>
demo.greetWithArgs  GET        /demo/greetWithArgs
shop.cart           GET        /cart
shop.cartAdd        POST       /cart/add/<product_id>
shop.cartClear      POST       /cart/clear
shop.cartRemove     POST       /cart/remove/<product_id>
shop.home           GET        /
static              GET        /static/<path:filename>
```

Then repeat **Checkpoint 7** in full – *everything should behave exactly as before*. That is the definition of a successful refactor: the code moved, the behaviour did not. Also try <http://127.0.0.1:5000/demo/add/2/3> (`5`), and note that the old `/greet/Ann` is now a 404 because the demo routes live under `/demo`.

---

## The finished project

### Final folder structure

```text
shop-site/
├── venv/                        ← private packages (never edit / never commit)
├── requirements.txt             ← from pip freeze
└── app/
    ├── __init__.py              ← creates app, connects to MongoDB, sets up CSRF + Flask-Login
    ├── app.py                   ← registers blueprints + the cart-count context processor
    ├── start.sh                 ← run the dev server
    ├── assets/
    │   └── css/custom.css       ← static files
    ├── controllers/             ← ROUTES (blueprints)
    │   ├── auth.py
    │   ├── shop.py
    │   └── demo.py
    ├── models/                  ← DATA
    │   ├── forms.py
    │   ├── cart.py
    │   ├── product.py
    │   └── users.py
    └── templates/               ← HTML (Jinja)
        ├── _render_field.html
        ├── base.html
        ├── cart.html
        ├── login.html
        ├── register.html
        └── shopping.html
```

### `requirements.txt` (final)

The file never changed after Step 1 – you needed every package from the beginning:

```text
blinker==1.7.0
click==8.1.7
dnspython==2.6.1
email-validator==2.1.0.post1
Flask==2.2.5
Flask-Login==0.6.3
flask-mongoengine==1.0.0
Flask-WTF==1.2.1
idna==3.6
itsdangerous==2.1.2
Jinja2==3.1.3
MarkupSafe==2.1.5
mongoengine==0.27.0
pymongo==4.6.1
Werkzeug==3.0.1
WTForms==3.1.2
```

### Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` (or `wtforms`, `mongoengine`, …) | The venv isn't activated. Run `source venv/bin/activate`, or you forgot `pip install …` / `pip install -r requirements.txt`. |
| `Error: Could not locate a Flask application` | You're not inside `app/`, or `FLASK_APP` isn't set. Use `cd app && bash start.sh`. |
| `ImportError: cannot import name 'app' from 'app'` / circular-import errors | You ran `python app.py`, or `__init__.py` imports something from `models/` or `controllers/`. Use `flask run`; keep `__init__.py` free of those imports. |
| `ModuleNotFoundError: No module named 'forms'` / `'models'` / `'controllers'` | `PYTHONPATH=.` missing, or you're not inside `app/`. |
| `ImportError: email-validator is not installed` | `pip install -r requirements.txt` (venv activated) |
| `ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused` | MongoDB isn't running. Start it (`docker start shop-mongo`). |
| Homepage says "No products yet." | The sample products are inserted by `home()` the first time the page loads. If it is still empty, look at the terminal for an error (usually MongoDB not running). |
| Form submit just redisplays the form with no error text | Missing `{{ form.hidden_tag() }}` (CSRF token) in the template, or no `secret_key`. |
| `400 Bad Request – The CSRF token is missing.` | A plain `<form method="POST">` without `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">` (Step 7). |
| `werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'login'` | After Step 8 the endpoint is `auth.login`. Update the `url_for(...)` call. |
| `TemplateNotFound: xyz.html` | File isn't in `app/templates/`, or the name is misspelled. |
| `Method Not Allowed (405)` | The route lacks `methods=["GET","POST"]` (or the form posts to a GET-only route). |
| Changes don't appear | Debug mode (`FLASK_DEBUG=1`) reloads Python files automatically; also hard-refresh the browser (Ctrl+Shift+R) for CSS. |

### URLs to try

| URL | Needs login? | What it shows |
|---|---|---|
| `/` | no | Product grid from MongoDB |
| `/register`, `/login` | no | Forms |
| `/logout` | no | Logs you out, back to `/` |
| `/cart` | **yes** | Your cart (stored in MongoDB) |
| `/demo/greet/Ann`, `/demo/add/2/3`, `/demo/greetWithArgs?friend=bob` | no | Seminar 2 playground |

### Where to go next (exercises)

1. **Product detail page** – a route `/product/<product_id>` in `controllers/shop.py` plus a `product.html` template. (Compare `viewPackageDetail` in `staycation`.)
2. **Images** – add an `image_url` field to `Product`, put pictures in `assets/img/`, and show them in the card instead of the grey placeholder.
3. **Change quantities** in the cart (add "+" and "−" buttons that update `CartItem.quantity`, and delete the line when it reaches 0).
4. **Orders** – a new `Order` model with a `ReferenceField(User)` and a list of products, saved when the user "checks out" (see `Itinerary`/`Booking` in Seminar 3).
5. **Admin-only page** – only `current_user.email == "admin@abc.com"` may add products (see how Seminar 3's `base.html` checks this).
6. **Configuration** – move the secret key and database host into environment variables.

{% endraw %}
