from odoo.tests.common import TransactionCase


class TestServerActionCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env['ir.model'].search(
            [('model', '=', 'res.partner')], limit=1)
        cls.partner_name_field = cls.env['ir.model.fields'].search([
            ('model_id', '=', cls.partner_model.id),
            ('name', '=', 'name'),
        ], limit=1)
        cls.partner_comment_field = cls.env['ir.model.fields'].search([
            ('model_id', '=', cls.partner_model.id),
            ('name', '=', 'comment'),
        ], limit=1)
        cls.partner_parent_field = cls.env['ir.model.fields'].search([
            ('model_id', '=', cls.partner_model.id),
            ('name', '=', 'parent_id'),
        ], limit=1)
        cls.partner_category_field = cls.env['ir.model.fields'].search([
            ('model_id', '=', cls.partner_model.id),
            ('name', '=', 'category_id'),
        ], limit=1)
        cls.test_partner = cls.env['res.partner'].create({
            'name': 'Test Partner Original',
        })
        cls.parent_partner = cls.env['res.partner'].create({
            'name': 'Parent Partner',
        })
