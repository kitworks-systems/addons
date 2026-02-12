/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("kw_autocomplete_model_method_tour", {
    url: "/odoo/action-test_kw_widget_autocomplete.action_kw_autocomplete_test",
    steps: () => [
        {
            trigger: '.o_data_cell:first',
            run: "click",
        },
        {
            trigger: '.nav-link:contains("Model Method")',
            run: "click",
        },
        {
            trigger: 'div[name="city_model_method"] input',
            run: "edit Ukr",
        },
        {
            trigger: '.o-autocomplete--dropdown-item:contains("Ukraine")',
            run: "click",
        },
        {
            trigger: '.o_form_button_save',
            run: "click",
        },
        {
            trigger: '.o_form_view:not(.o_form_editable)',
        },
    ],
});

registry.category("web_tour.tours").add("kw_autocomplete_domain_search_tour", {
    url: "/odoo/action-test_kw_widget_autocomplete.action_kw_autocomplete_test",
    steps: () => [
        {
            trigger: '.o_data_cell:first',
            run: "click",
        },
        {
            trigger: '.nav-link:contains("Domain Search")',
            run: "click",
        },
        {
            trigger: 'div[name="country_domain"] input',
            run: "edit Ger",
        },
        {
            trigger: '.o-autocomplete--dropdown-item:contains("Germany")',
            run: "click",
        },
        {
            trigger: '.o_form_button_save',
            run: "click",
        },
        {
            trigger: '.o_form_view:not(.o_form_editable)',
        },
    ],
});
