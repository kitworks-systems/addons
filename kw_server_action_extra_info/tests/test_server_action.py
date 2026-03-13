from odoo.tests import tagged

from .common import TestServerActionCommon


@tagged('post_install', '-at_install')
class TestIrServerObjectLines(TestServerActionCommon):

    def test_eval_value_type_value(self):
        line = self.env['ir.server.object.lines'].create({
            'col1': self.partner_name_field.id,
            'kw_value': 'Test Value Direct',
            'handle_type': 'value',
        })
        result = line.eval_value()
        self.assertEqual(result[line.id], 'Test Value Direct')

    def test_eval_value_type_reference(self):
        line = self.env['ir.server.object.lines'].create({
            'col1': self.partner_parent_field.id,
            'kw_value': str(self.parent_partner.id),
            'handle_type': 'reference',
        })
        result = line.eval_value()
        self.assertEqual(result[line.id], self.parent_partner.id)

    def test_eval_value_type_equation(self):
        line = self.env['ir.server.object.lines'].create({
            'col1': self.partner_name_field.id,
            'kw_value': '"Computed " + "Name"',
            'handle_type': 'equation',
        })
        result = line.eval_value(eval_context={})
        self.assertEqual(result[line.id], 'Computed Name')

    def test_eval_value_equation_with_context(self):
        line = self.env['ir.server.object.lines'].create({
            'col1': self.partner_name_field.id,
            'kw_value': 'record.name + " Modified"',
            'handle_type': 'equation',
        })
        eval_context = {'record': self.test_partner}
        result = line.eval_value(eval_context=eval_context)
        self.assertEqual(result[line.id], 'Test Partner Original Modified')

    def test_compute_resource_ref_for_relational_field(self):
        line = self.env['ir.server.object.lines'].create({
            'col1': self.partner_parent_field.id,
            'kw_value': str(self.parent_partner.id),
            'handle_type': 'reference',
        })
        self.assertEqual(line.resource_ref, self.parent_partner)

    def test_compute_resource_ref_non_relational_field(self):
        line = self.env['ir.server.object.lines'].create({
            'col1': self.partner_name_field.id,
            'kw_value': 'test',
            'handle_type': 'value',
        })
        self.assertFalse(line.resource_ref)

    def test_compute_resource_ref_invalid_id(self):
        line = self.env['ir.server.object.lines'].create({
            'col1': self.partner_parent_field.id,
            'kw_value': 'not_a_number',
            'handle_type': 'reference',
        })
        self.assertTrue(line.resource_ref)

    def test_selection_target_model_excludes_transient(self):
        lines_model = self.env['ir.server.object.lines']
        selection = lines_model._selection_target_model()
        model_names = [m[0] for m in selection]
        self.assertIn('res.partner', model_names)
        transient_models = self.env['ir.model'].search([
            ('transient', '=', True)])
        for tm in transient_models:
            self.assertNotIn(tm.model, model_names)

    def test_eval_value_multiple_lines(self):
        line1 = self.env['ir.server.object.lines'].create({
            'col1': self.partner_name_field.id,
            'kw_value': 'Name Value',
            'handle_type': 'value',
        })
        line2 = self.env['ir.server.object.lines'].create({
            'col1': self.partner_comment_field.id,
            'kw_value': 'Comment Value',
            'handle_type': 'value',
        })
        lines = line1 | line2
        result = lines.eval_value()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[line1.id], 'Name Value')
        self.assertEqual(result[line2.id], 'Comment Value')


@tagged('post_install', '-at_install')
class TestIrActionsServer(TestServerActionCommon):

    def test_run_action_object_write(self):
        action = self.env['ir.actions.server'].create({
            'name': 'Test Write Action',
            'model_id': self.partner_model.id,
            'state': 'object_write',
            'fields_lines': [(0, 0, {
                'col1': self.partner_name_field.id,
                'kw_value': 'Updated Name',
                'handle_type': 'value',
            })],
        })
        action.with_context(active_id=self.test_partner.id) \
            ._run_action_object_write()
        self.assertEqual(self.test_partner.name, 'Updated Name')

    def test_run_action_object_write_multiple_fields(self):
        action = self.env['ir.actions.server'].create({
            'name': 'Test Write Multiple',
            'model_id': self.partner_model.id,
            'state': 'object_write',
            'fields_lines': [
                (0, 0, {
                    'col1': self.partner_name_field.id,
                    'kw_value': 'New Name',
                    'handle_type': 'value',
                }),
                (0, 0, {
                    'col1': self.partner_comment_field.id,
                    'kw_value': 'New Comment',
                    'handle_type': 'value',
                }),
            ],
        })
        action.with_context(active_id=self.test_partner.id) \
            ._run_action_object_write()
        self.assertEqual(self.test_partner.name, 'New Name')
        self.assertIn('New Comment', self.test_partner.comment)

    def test_run_action_object_write_empty_lines(self):
        action = self.env['ir.actions.server'].create({
            'name': 'Test Write Empty',
            'model_id': self.partner_model.id,
            'state': 'object_write',
        })
        original_name = self.test_partner.name
        action.with_context(active_id=self.test_partner.id) \
            ._run_action_object_write()
        self.assertEqual(self.test_partner.name, original_name)

    def test_run_action_object_write_with_equation(self):
        action = self.env['ir.actions.server'].create({
            'name': 'Test Write Equation',
            'model_id': self.partner_model.id,
            'state': 'object_write',
            'fields_lines': [(0, 0, {
                'col1': self.partner_name_field.id,
                'kw_value': 'record.name + " - Suffix"',
                'handle_type': 'equation',
            })],
        })
        eval_context = {'record': self.test_partner}
        action.with_context(active_id=self.test_partner.id) \
            ._run_action_object_write(eval_context=eval_context)
        self.assertEqual(
            self.test_partner.name, 'Test Partner Original - Suffix')

    def test_run_action_object_create(self):
        action = self.env['ir.actions.server'].create({
            'name': 'Test Create Action',
            'model_id': self.partner_model.id,
            'crud_model_id': self.partner_model.id,
            'state': 'object_create',
            'fields_lines': [(0, 0, {
                'col1': self.partner_name_field.id,
                'kw_value': 'Created Partner',
                'handle_type': 'value',
            })],
        })
        new_record = action._run_action_object_create()
        self.assertTrue(new_record)
        self.assertEqual(new_record.name, 'Created Partner')

    def test_run_action_object_create_empty_lines(self):
        action = self.env['ir.actions.server'].create({
            'name': 'Test Create Empty',
            'model_id': self.partner_model.id,
            'crud_model_id': self.partner_model.id,
            'state': 'object_create',
        })
        result = action._run_action_object_create()
        self.assertIsNone(result)

    def test_run_action_object_create_with_link_many2one(self):
        action = self.env['ir.actions.server'].create({
            'name': 'Test Create With Link',
            'model_id': self.partner_model.id,
            'crud_model_id': self.partner_model.id,
            'state': 'object_create',
            'link_field_id': self.partner_parent_field.id,
            'fields_lines': [(0, 0, {
                'col1': self.partner_name_field.id,
                'kw_value': 'Child Partner',
                'handle_type': 'value',
            })],
        })
        new_record = action.with_context(
            active_id=self.test_partner.id)._run_action_object_create()
        self.assertTrue(new_record)
        self.assertEqual(self.test_partner.parent_id, new_record)

    def test_fields_lines_copy(self):
        action = self.env['ir.actions.server'].create({
            'name': 'Test Copy Action',
            'model_id': self.partner_model.id,
            'state': 'object_write',
            'fields_lines': [(0, 0, {
                'col1': self.partner_name_field.id,
                'kw_value': 'Original Value',
                'handle_type': 'value',
            })],
        })
        copied_action = action.copy()
        self.assertEqual(len(copied_action.fields_lines), 1)
        self.assertEqual(
            copied_action.fields_lines[0].kw_value, 'Original Value')
        self.assertNotEqual(
            action.fields_lines.id, copied_action.fields_lines.id)

    def test_groups_id_field(self):
        group = self.env['res.groups'].create({'name': 'Test Group'})
        action = self.env['ir.actions.server'].create({
            'name': 'Test Groups Action',
            'model_id': self.partner_model.id,
            'state': 'object_write',
            'groups_id': [(4, group.id)],
        })
        self.assertIn(group, action.groups_id)
