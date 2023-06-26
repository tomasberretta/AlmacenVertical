from marshmallow import Schema, fields, validate


class SendScaleRequestSchema(Schema):
    size = fields.Integer(required=True, validate=lambda x: 0 <= x <= 2)
    amount = fields.Integer(required=True, validate=lambda x: 0 <= x <= 100)


class HomeMotorRequestSchema(Schema):
    index = fields.Integer(required=True, validate=lambda x: 0 <= x <= 2)

class ReadyMotorRequestSchema(Schema):
    index = fields.Integer(required=True, validate=lambda x: 0 <= x <= 2)

class MoveMotorRequestSchema(Schema):
    index = fields.Integer(required=True, validate=lambda x: 0 <= x <= 2)
    posH = fields.String(required=True,
                         validate=validate.Regexp(r'^0x[0-9A-Fa-f]{4}$'))  # hex string with 0x prefix and 4 digits
    posL = fields.String(required=True,
                         validate=validate.Regexp(r'^0x[0-9A-Fa-f]{4}$'))  # hex string with 0x prefix and 4 digits
