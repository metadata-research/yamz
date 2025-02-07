from app import db


class Track(db.Model):
    __tablename__ = "tracking"
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey(
        "terms.id"), primary_key=True)

    term = db.relationship("Term", back_populates="tracks",
                           order_by="Term.term_string")
    user = db.relationship("User", back_populates="tracking")

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self) -> str:
        return self.user.last_name + ": " + self.term.term_string
