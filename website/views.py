import datetime
import os
import random
import string

from flask import Flask, render_template, redirect, request, send_file, session, url_for, abort
import dotenv

from website import utils

sessions = []


app = Flask(__name__)
app.config.from_object("config")
dotenv.load_dotenv()

utils.autodelete_sessions(sessions)

print("================== pass", os.environ.get("password"))


@app.route("/")
def root():
    return redirect(url_for("login"))

@app.route("/unauthorized/")
def unauthorized():
    return render_template("unauthorized.html", message="Sorry, an error occured.")


@app.route("/login/", methods=["GET", "POST"])
def login():
    if utils.session_is_valid(session.get("session-token"), sessions):
        return redirect(url_for("files", path="Desktop"))

    if request.method == "POST":
        password = request.form.get("password")

        if password != os.environ.get("PASSWORD"):
            return render_template("unauthorized.html", message="Sorry, but the password is incorrect.")

        else:
            session_token = ''.join([random.choice(string.printable) for _ in range(32)])

            # 1h session duration
            session_expire = datetime.datetime.now() + datetime.timedelta(hours=4)

            sessions.append(utils.Session(session_expire, session_token))

            # Writing the session token to the user's session storage
            session["session-token"] = session_token

            response = redirect(url_for("files", path="Desktop"))

            return response

    return render_template("login.html")


@app.route("/files/")
def files_root():
    return redirect(url_for("files", path="Desktop"))


@app.route("/files/<path:path>")
def files(path):
    if not utils.session_is_valid(session.get("session-token"), sessions):
        return render_template("unauthorized.html", message="Sorry but your session is invalid.")

    path = path.replace("..", ".").replace("~", ".")  # Securing the path

    if not path.startswith("Desktop"):
        return redirect(url_for("files", path="Desktop"))

    print(utils.BASE_DIR + "files/" + path)

    # If the requested path is a file
    if os.path.isfile(utils.BASE_DIR + path):
        # Send the file with preview mode if it is of previewable type
        if os.path.splitext(utils.BASE_DIR + path)[1][1:] in utils.viewable_formats:
            return send_file(utils.BASE_DIR + path, as_attachment=False)

        # File isn't previewable, send as attachment download only
        return send_file(utils.BASE_DIR + path, as_attachment=True)

    # If the path provided doesn't exist
    elif not os.path.exists(utils.BASE_DIR + path):
        return abort(404)  # Show "Not found" page


    files, folders = utils.get_dir_content(utils.BASE_DIR + path)

    return render_template("files.html",
                           path=path, title=path.strip('/').rsplit('/')[-1],
                           len_folders=len(folders), folders=sorted(folders),
                           len_files=len(files), files=sorted(files, key=lambda file: file[0].lower()),
                           emoji_selector=utils.emoji_selector
                           )


@app.errorhandler(404)
def notfound(_):
    return render_template("notfound.html")


if __name__ == "__main__":
    app.run()
