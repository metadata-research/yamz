from app import db
from app.notify import notify_blueprint as notify
from app.notify.forms import MessageForm
from app.user.models import Message, Notification
from app.user.models import User
from flask import flash, redirect, render_template, url_for, abort, jsonify, request
from flask_login import current_user, login_required


@notify.route("/message/send_to/<int:recipient_id>", methods=["GET", "POST"])
@login_required
def send_message(recipient_id):
    user = User.query.filter_by(id=recipient_id).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        message_data = form.message.data.strip()
        message = Message(author=current_user, recipient=user, body=message_data)
        message.save()
        sent_msg = Message(author=user, recipient=current_user, body=message_data)
        sent_msg.save()
        flash("Your message has been sent to " + user.full_name + ".", "success")
        return redirect(url_for("main.index"))
    return render_template(
        "notify/send_message.jinja", title="Send Message", form=form, recipient=user
    )


@notify.route("/message/delete/<int:message_id>")
@login_required
def delete_message(message_id):
    message = Message.query.filter_by(id=message_id).first_or_404()
    if message.recipient != current_user:
        abort(403)
    if message.sent:
        if message.author != current_user:
            abort(403)
    message.delete()
    flash("Your message has been deleted.", "success")
    return redirect(url_for("notify.messages"))


@notify.route("/messages")
@login_required
def messages():
    current_user.last_message_read_time = db.func.now()
    db.session.commit()
    messages_received = current_user.messages_received.order_by(
        Message.timestamp.desc()
    )
    return render_template(
        "notify/display_messages.jinja", messages_received=messages_received
    )


@notify.route("/notifications")
@login_required
def notifications():
    since = request.args.get("since", 0.0, type=float)
    # notifications = current_user.notifications.filter(Notification.timestamp > since).order_by("timestamp").all()
    notifications = current_user.notifications.order_by("timestamp").all()
    return jsonify(
        [
            {"name": n.name, "id": n.id, "data": n.get_data(), "timestamp": n.timestamp}
            for n in notifications
        ]
    )

@notify.route("/notifications/delete/<int:notification_id>")
@login_required
def delete_notification(notification_id):
    notification = Notification.query.filter_by(id=notification_id).first_or_404()
    if notification.user != current_user:
        abort(403)
    notification.delete()
    return redirect(url_for("main.index"))
