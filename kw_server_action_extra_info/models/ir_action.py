import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo import Command

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    fields_lines = fields.One2many(
        comodel_name='ir.server.object.lines',
        inverse_name='server_id',
        string='Value Mapping',
        copy=True, )
    groups_id = fields.Many2many(
        comodel_name='res.groups',
        relation='ir_act_server_group_rel',
        column1='act_id',
        column2='gid',
        string='Groups', )

    def _run_action_object_write(self, eval_context=None):
        """Apply specified write changes using
        custom kw_value for multiple fields."""
        vals_by_line = self.fields_lines.eval_value(eval_context=eval_context)
        res = {}

        for line in self.fields_lines:
            if line.col1 and line.id in vals_by_line:
                res[line.col1.name] = vals_by_line[line.id]

        if not res:
            return

        record = self.env[self.model_id.model].browse(
            self._context.get('active_id'))
        record.write(res)

    def _run_action_object_create(self, eval_context=None):
        """Create a new record using multiple
        field lines with custom kw_value."""
        vals_by_line = self.fields_lines.eval_value(eval_context=eval_context)
        res = {}

        # we are building a dictionary {field_name: value}
        for line in self.fields_lines:
            if line.col1 and line.id in vals_by_line:
                res[line.col1.name] = vals_by_line[line.id]

        if not res:
            return None

        record = self.env[self.crud_model_id.model].create(res)

        # if you need to link the created record to the active one
        if self.link_field_id:
            active = self.env[self.model_id.model].browse(
                self._context.get('active_id'))
            if self.link_field_id.ttype in ['one2many', 'many2many']:
                active.write({
                    self.link_field_id.name: [Command.link(record.id)]})
            else:
                active.write({
                    self.link_field_id.name: record.id})

        return record


class IrServerObjectLines(models.Model):
    _name = 'ir.server.object.lines'
    _description = 'Server Action value mapping'

    server_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Related Server Action',
        ondelete='cascade', )
    col1 = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        required=True,
        ondelete='cascade', )
    kw_value = fields.Text(
        required=True,
        help=(
            "Expression containing a value specification.\n"
            "When Formula type is selected, "
            "this field may be a Python expression that can use "
            "the same values as for the code field on the server action.\n"
            "If Value type is selected, the value will be used directly."
        ), )
    handle_type = fields.Selection(
        default='value',
        required=True,
        selection=[
            ('value', 'Value'),
            ('reference', 'Reference'),
            ('equation', 'Python expression'),
        ], )
    resource_ref = fields.Reference(
        string='Record',
        selection='_selection_target_model',
        compute='_compute_resource_ref', )

    @api.model
    def _selection_target_model(self):
        model_records = self.env['ir.model'].sudo().search([
            ('transient', '=', False), ])
        res = []
        for m in model_records:
            try:
                model = self.env[m.model].sudo()
            except KeyError:
                continue

            if not model._abstract:
                res.append((m.model, m.name))
        return res

    def eval_value(self, eval_context=None):
        """Return dictionary {line.id: evaluated_value} for all lines."""
        result = {}
        for line in self:
            if line.handle_type == 'value':
                value = line.kw_value
            elif line.handle_type == 'reference':
                value = line.resource_ref.id
            elif line.handle_type == 'equation':
                value = safe_eval(line.kw_value or '', eval_context)
            else:
                value = False
            result[line.id] = value
        return result

    @api.depends('col1.relation', 'kw_value', 'handle_type')
    def _compute_resource_ref(self):
        for line in self:
            if not (line.handle_type in ['reference', 'value']
                    and line.col1 and line.col1.relation):
                line.resource_ref = False
                continue
            try:
                value = int(line.kw_value)
            except ValueError:
                value = 0
            if not self.env[line.col1.relation].browse(value).exists():
                record = self.env[line.col1.relation].search([], limit=1)
                value = record.id if record else 0
            line.resource_ref = '%s,%s' % (line.col1.relation, value)
