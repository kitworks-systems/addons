from odoo import models, fields


class TestYearModel(models.Model):
    _name = 'test.year'
    _description = 'Test Year Model'
    _inherit = ['kw.year.mixin']

    name = fields.Char()


class TestWeekModel(models.Model):
    _name = 'test.week'
    _description = 'Test Week Model'
    _inherit = ['kw.week.mixin']

    name = fields.Char()


class TestMonthModel(models.Model):
    _name = 'test.month'
    _description = 'Test Month Model'
    _inherit = ['kw.month.mixin']

    name = fields.Char()


class TestQuarterModel(models.Model):
    _name = 'test.quarter'
    _description = 'Test Quarter Model'
    _inherit = ['kw.quarter.mixin']

    name = fields.Char()
