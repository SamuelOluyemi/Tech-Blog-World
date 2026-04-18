# Tech Blog World

## This is a CS50 course project

## The deployed website is ("[here](https://tech-blog-world.onrender.com)) using Render

## Description

> [!IMPORTANT] </br>
> Admin email and password are env data. You might want to create a standard user or use the example user below to access the blog website</br>
> Example user can be created or use email = foo@example.com | password = Security1_

### Templates

The base templates for the blog page was implemented with the aid of open-source resource [Start Bootstrap - Clean Blog](https://startbootstrap.com/theme/clean-blog/)

"Templates" includes (all .html files):

> - [About](templates/about.html)
> - [Admin_deleted_posts](admin_deleted_posts.html)
> - [Admin_messages](admin_messages.html)
> - [Change_password](change_password.html)
> - [Contact](contact.html)
> - [Footer](footer.html) - footer for other templates
> - [Header](header.html) - layout for other templates
> - [Index](index.html)
> - [Login](login.html)
> - [Make-post](make-post.html)
> - [Post](post.html)
> - [Register](register.html)

### [Requirement.txt](requirements.txt)

We've included a requirement.txt file including packages that need to be installed with simply `"pip install -r requirements.txt"` on MacOS or `"python -m pip install -r requirements.txt"` on Windows in the CLI

### [App.py](app.py)

We've implement our app instance in app.py and made a forms.py file to include our forms.\
At the launch of the app.py, the database is checked to see if there's an Admin, if there's none, it creates one with the information provided at app_context and defaults everyone else to `is_admin=False`

[app.py](app.py) has `check_inactivity()` function to check session inactivity and automatically logs user out after 30 minutes of inactivity

```
Here are highlighted functionalities implemented in the app.py:
- app instance
- db using db.Model to create tables
- python decorators [@admin_only and @commenter_only]

- Routes & Functions: check_activity(); purge_old_deleted_posts(); register(); login(); logout(); get_all_posts(); show_posts(); delete_comment(); add_new_post(); edit_post(); soft_delete_post(); delete_post(); deleted_posts_dashboard(); restore_post_route(); force_delete_post(); about(); send_contact_email(); contact(); admin_msgs(); change_password().

We can perform the following actions but not limited to:
- Viewing all available blog posts, posting a new blog post, editing any blog post, soft delete (trash), permanently delete, and restore blog posts, comment on a post, delete the comment and more.

More about the functionalities explained below...
```

### [Forms.py](forms.py)

> Here are the forms found in forms.py using `FlaskForm` and imported into [app.py](#app.py):
>
> - CreatePostForm()

```
- CreatePostForm()
- RegisterForm()
- LoginForm()
- CommentForm()
- ChangePasswordForm()
- ContactForm()
- DeletePostForm()
- DeleteCommentForm()
- RestorePostForm()
```

### [Static folder](static)

We've included static files, most of which came from the open-source resource for [Start Bootstrap - Clean Blog](https://startbootstrap.com/theme/clean-blog/).\
While [img file](static/assets/img) includes images used in project, from above mentioned resource, we've improved the [css file](static/css) and [js file](static/js) (by including `Dropdown` functionality of [dashboard](#DASHBOARD/PROFILE) in [scripts.js](static/js/scripts.js) and creating [time-utils.js](static/js/time-utils.js) to help implement the smart-time stamp behavior for posts, comments, etc. "just now", "yesterday" etc.).

### [Instance folder](instance)

We've opted to use `sqlalchemy` for our `database(db)`
We've got our [instance folder](instance) which contained our database ["posts.db"](instance/posts.db) with three tables in itself (**users**, **blog_posts** & **comments** ). We, later added new tables to db: **contact_msgs** & **deleted_posts**; making tables = 5 tables.

> - **users**: id; name; email; password_hash; is_admin(BOOLEAN) where primary key is id and emails are unique.
> - **blog_posts**: id; author_id; title; subtitle; date; body; img_url, is_deleted(BOOLEAN) where primary key is id, FOREIGN KEY is author_id referencing users(id)(ON DELETE CASCADE) and title is unique.
> - **comments**: id; author_id; post_id; text; date where primary key is id, FOREIGN KEYS are author_id referencing to users(id)(ON DELETE CASCADE) & post_id referencing - blog_posts(id)(ON DELETE CASCADE).
> - **contact_msgs**: id, sender_id, name, email, phone, message, sent_at, where primary key is id, FOREIGN KEY is sender_id referencing users(id).
> - **deleted_posts**: id; deleted_post_id; title; subtitle; date; body; img_url, deleted_at, where primary key is id and title is unique.

### [HOME PAGE](templates/index.html)

![Home Page](static/assets/img/home-bg.jpg)

The home page is displayed for everyone including [Admin](#ADMIN) and [Users](#USERS) (Logged in or not).\
We've implemented home page under [index route in app.py](#App.py) which only displays titled links to posts for which `is_deleted` in database is `False`(read more under [Admin](#ADMIN)).\
For [Admin](#ADMIN), the home page includes a button to `soft_delete_post` each post which places the target post in [Trash Page](#Trash-Page).<br/>
If a post is clicked, its content is displayed by `show_post` route. In the `show_post` route, only the [Admin](#ADMIN) can `edit_post` and only logged in [users](#USERS) (including [Admin](#ADMIN))) can comment on the post. In the `show_post` route, the commenter can also `delete_comment` at any time.

### [REGISTER PAGE](templates/register.html)

The Register page renders a [form](#Forms.py) through `register` route to collect user's information including name; email (which is unique); and password (confirmation password required to match the password). The password has to contains at least 8 characters including UpperCase, LowerCase, Number(s), Special character(s) and cannot have 2 same characters consecutively.

### [LOGIN PAGE](templates/login.html)

The Login page renders a [form](#Forms.py) through `login` route to collect user's email and password, compare with the information in database under `users` table to authenticate them as valid users to allow them perform actions only logged in users can perform on the blog page

### [ABOUT PAGE](templates/about.html)

The About page through `about` route displays a multiple paragraphs describing what the Tech Blog World website is about in summary.

### [CONTACT PAGE](templates/contact.html)

The Contact page through `contact` route renders a [form](#Forms.py) `ContactForm` that allows users send a message each time to the [Admin](#ADMIN). The message gets sent to the [Admin's Messages page](#Messages-Page), the admin's example mailbox and sotcode2025@gmail.com which is a code test mailbox. We used `flask_mail` to implement the user sending their message to the [Admin](#ADMIN) while we store the data to a table in the database named `contact_msgs`

### [DASHBOARD/PROFILE](templates)

The Dashboard/Profile displays an avatar (using `gravatar`), for which when clicked displays the following options highlighted below:

#### [Change Password](templates/change_password.html)

Using `change_password` route in [app.py](app.py) in such a way that since it has decorator `@login_required` and [app.py](app.py) has `check_inactivity()` function to check session inactivity and auto-log user out after 30 minutes. So, for UX, we decided not to require the user to re-enter their current password before changing to a new one. Confirmation password is required to match the new password

#### [Log Out](templates/logout.html)

Using `logout` route in [App.py](app.py), Admin/User can Log out

### [Dashboard For Admin includes:](templates)

#### [Messages Page](templates/admin_messages.html)

Using `admin_msgs` route, Messages page displays messages sent to the [Admin](#ADMIN) by the users(logged in or not).

#### [Trash Page](templates/admin_deleted_posts.html)

Using `deleted_posts_dashboard` route, Trash page displays a Restore button to restore soft deleted post(s) `restore_post_route` before 30 days and Permanently delete button to delete a deleted post using `force_delete_post`. We've implemented `admin_deleted_posts.html` for [Trash page](#Trash-Page) and every backend logic in [App.py](#App.py) including function `purge_old_deleted_posts()` that deletes `deleted_posts` posts automatically after 30 days.

### ADMIN

We implemented the `@admin_only` decorator to check if the `current_user is_admin=True or False`. If True, then, they're allowed to perform major changing tasks on the blog page including:

> - Posting a new blog post;
> - editing any blog post;
> - soft deleting blog post(s),
> - permanently deleting blog post(s), and
> - restoring blog post(s).

The Admin's dashboard allows them view [Messages](#Messages-Page) sent to them by [users](#USERS), as well as view [(Soft) Deleted Posts](#Trash-Page) (an action that changed post [`is_deleted` in `posts.db` to `True`](#Instance-folder)), and also giving them the options to [Restore a deleted post](#Trash-Page) (an action that changes post [`is_deleted` back to `False`](#Trash-Page)) or [Permanently delete a deleted post](#Trash-Page) (an action that `force_delete_post` from database completely).
The Admin can also comment on a post and delete their comment as desired.

### USERS

Every user, whether logged in or not can view the [Home page](#HOME-PAGE), view the [About page](#ABOUT-PAGE) and view/use the [Contact page](#CONTACT-PAGE).\
We implemented the `@commenter_only` decorator in [App.py](#App.py) which allows only a logged in user to comment on blog posts.
