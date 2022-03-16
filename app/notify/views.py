from app import db
from app.notify import notify_blueprint as notify
from app.notify.forms import MessageForm
from app.notify.models import Message
from app.user.models import User
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required


@notify.route("/send_message/<int:recipient_id>", methods=["GET", "POST"])
@login_required
def send_message(recipient_id):
    user = User.query.filter_by(id=recipient_id).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash("Your message has been sent to " + user.full_name + ".", "success")
        return redirect(url_for("main.index"))
    return render_template(
        "notify/send_message.jinja", title="Send Message", form=form, recipient=user
    )


@notify.route("/messages")
@login_required
def messages():
    current_user.last_message_read_time = db.func.now()
    db.session.commit()
    messages = current_user.messages_received.order_by(Message.timestamp.desc())
    return render_template("notify/display_messages.jinja", messages=messages)
