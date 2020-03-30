from gino import Gino

db = Gino()


class TmradioAdmin(db.Model):
    __tablename__ = 'radio_admins'
    user_id = db.Column(db.Numeric(18, 0), db.ForeignKey('access_users.id'))


class User(db.Model):
    __tablename__ = 'access_users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80))
    tm_login = db.Column(db.String(30))
    tm_password_hash = db.Column(db.String(80))
    deleted = db.Column(db.Integer, default=0)

    @property
    def is_admin(self):
        return (await TmradioAdmin.get(self.id)) is not None

    @is_admin.setter
    def _is_admin(self, set_admin=True):
        if set_admin:
            if not self.is_admin:
                await TmradioAdmin.create(user_id=self.id)
        else:
            await TmradioAdmin.delete.here(TmradioAdmin.user_id == self.id)


class RadioDriverRule(db.Model):
    __tablename__ = 'radio_driver_rules'

    id = db.Column(db.Integer(), primary_key=True)
    driver_id = db.Column(db.Numeric(18, 0), index=True)
    rule_id = db.Column(db.Numeric(18, 0), index=True)
    shift_id = db.Column(db.Numeric(18, 0), index=True)


class RadioEmails(db.Model):
    __tablename__ = 'radio_emails'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Numeric(18, 0))
    email = db.Column(db.Inicode(64))


class RadioRawData(db.Model):
    __tablename__ = 'radio_raw_data'

    id = db.Column(db.Integer(), primary_key=True)
    input_time = db.Column(db.DateTime(timezone=True))
    driver_id = db.Column(db.Numeric(18, 0), index=True)
    shift_date = db.Column(db.Date(), index=True)
    shift_id = db.Column(db.Numeric(18, 0), index=True)
    value_ = db.Column(db.String(100))
    card_no = db.Column(db.String(16))
    user_id = db.Column(db.Numeric(18, 0), index=True)
    rule_id = db.Column(db.Numeric(18, 0), index=True)
    is_locked = db.Column(db.SmallInt(), default=0)
    deleted = db.Column(db.SmallInt(), default=0)


class RadioRawDataOper(db.Model):
    __tablename__ = 'radio_raw_data_opers'

    oper_id = db.Column(db.Numeric(18, 0))
    raw_data_id = db.Column(db.Numeric(18, 0), index=True)
    _pk = db.PrimaryKeyConstraint('oper_id', 'raw_data_id', name='radio_raw_data_opers_pkey')
    user_id = db.Column(db.Numeric(18, 0), index=True)
    storno = db.Column(db.Numeric(18, 0))
    oper_time = db.Column(db.DateTime(timezone=True), index=True)
    is_reported = db.Column(db.SmallInt())


class RadioReportSend(db.Model):
    __tablename__ = 'radio_report_send'

    email_id = db.Column(db.Numeric(18, 0))
    report_id = db.Column(db.Numeric(18, 0))
    _pk = db.PrimaryKeyConstraint('email_id', 'report_id', name='radio_report_send_pkey')


class RadioReport(db.Model):
    __tablename__ = 'radio_reports'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(255))
    call = db.Column(db.Unicode(255))


class RadioReportSended(db.Model):
    __tablename__ = 'radio_reports_sended'

    report_id = db.Column(db.Numeric(18, 0))
    shift_id = db.Column(db.Numeric(18, 0))
    shift_date = db.Column(db.Date())
    datetime_reported = db.Column(db.DateTime(timezone=True), default=utcnow)
    _pk = db.PrimaryKeyConstraint('report_id', 'shift_id', 'shift_date', name='radio_reports_sended_pkey')
