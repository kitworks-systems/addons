/** @odoo-module **/

import { registry } from "@web/core/registry";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import { listView } from "@web/views/list/list_view";
import { session } from "@web/session";

class KwFilteredGroupedRelationalModel extends RelationalModel {
    async _loadGroupedList(config) {
        const result = await super._loadGroupedList(config);
        if (!result || !result.groups) {
            return result;
        }
        const enabled = !!session.kw_hide_empty_groups;
        if (!enabled) {
            return result;
        }

        const filteredGroups = result.groups.filter((group) => {
            const hasRecords = group.records?.length > 0;
            const hasSubgroups = group.groups?.length > 0;
            return group.count > 0 || hasRecords || hasSubgroups;
        });

        return { ...result, groups: filteredGroups };
    }
}

export const kwFilteredGroupedListView = {
    ...listView,
    Model: KwFilteredGroupedRelationalModel,
};

registry.category("views").add("kw_filtered_grouped_list", kwFilteredGroupedListView);
