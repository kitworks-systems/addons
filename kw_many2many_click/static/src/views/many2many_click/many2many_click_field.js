/** @odoo-module **/

import { evaluateBooleanExpr } from "@web/core/py_js/py";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";
import { Many2ManyClickList } from "@kw_many2many_click/views/many2many_click_list/many2many_click_list";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";

export class Many2ManyClickField extends Many2ManyTagsField {
    static template = "kw_many2many_click.Many2ManyClickField";
    static components = {
        Many2ManyClickList,
        Many2XAutocomplete,
    };
}

export const many2ManyClickField = {
    component: Many2ManyClickField,
    displayName: _t("Clickable Many2many"),
    supportedOptions: [
        {
            label: _t("Disable creation"),
            name: "no_create",
            type: "boolean",
            help: _t(
                "If checked, users won't be able to create records through the autocomplete dropdown at all."
            ),
        },
        {
            label: _t("Disable 'Create' option"),
            name: "no_quick_create",
            type: "boolean",
            help: _t(
                "If checked, users will not be able to create records based on the text input; they will still be able to create records via a popup form."
            ),
        },
        {
            label: _t("Disable 'Create and Edit' option"),
            name: "no_create_edit",
            type: "boolean",
            help: _t(
                "If checked, users will not be able to create records based through a popup form; they will still be able to create records based on the text input."
            ),
        },
        {
            label: _t("Can create"),
            name: "create",
            type: "string",
            help: _t("Write a domain to allow the creation of records conditionnally."),
        },
        {
            label: _t("Color field"),
            name: "color_field",
            type: "field",
            availableTypes: ["integer"],
            help: _t("Set an integer field to use colors with the tags."),
        },
    ],
    supportedTypes: ["many2many"],
    relatedFields: ({ options }) => {
        const relatedFields = [{ name: "display_name", type: "char" }];
        if (options.color_field) {
            relatedFields.push({ name: options.color_field, type: "integer", readonly: false });
        }
        return relatedFields;
    },
    extractProps({ attrs, options, string }, dynamicInfo) {
        const hasCreatePermission = attrs.can_create ? evaluateBooleanExpr(attrs.can_create) : true;
        const noCreate = Boolean(options.no_create);
        const canCreate = noCreate ? false : hasCreatePermission;
        const noQuickCreate = Boolean(options.no_quick_create);
        const noCreateEdit = Boolean(options.no_create_edit);
        return {
            colorField: options.color_field,
            nameCreateField: options.create_name_field,
            canCreate,
            canQuickCreate: canCreate && !noQuickCreate,
            canCreateEdit: canCreate && !noCreateEdit,
            createDomain: options.create,
            context: dynamicInfo.context,
            domain: dynamicInfo.domain,
            placeholder: attrs.placeholder,
            string,
        };
    },
};

registry.category("fields").add("many2many_click", many2ManyClickField);
