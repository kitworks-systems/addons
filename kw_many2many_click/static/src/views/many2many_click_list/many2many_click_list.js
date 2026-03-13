/** @odoo-module **/

import { Component } from "@odoo/owl";

export class Many2ManyClickList extends Component {
    static template = "kw_many2many_click.Many2ManyClickList";
    static defaultProps = {
        displayText: true,
    };
    static props = {
        displayText: { type: Boolean, optional: true },
        itemsVisible: { type: Number, optional: true },
        tags: { type: Array },
        model: { type: String, optional: true },
    };

    openRecordForm(ev) {
        ev.stopPropagation();
        const itemId = ev.currentTarget.dataset.id;
        const item = this.props.tags.find((t) => String(t.id) === String(itemId));
        if (!item || !this.props.model || !item.resId) {
            return;
        }

        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: this.props.model,
            res_id: item.resId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    get visibleTagsCount() {
        return this.props.itemsVisible - 1;
    }

    get visibleTags() {
        if (this.props.itemsVisible && this.props.tags.length > this.props.itemsVisible) {
            return this.props.tags.slice(0, this.visibleTagsCount);
        }
        return this.props.tags;
    }

    get otherTags() {
        if (!this.props.itemsVisible || this.props.tags.length <= this.props.itemsVisible) {
            return [];
        }
        return this.props.tags.slice(this.visibleTagsCount);
    }

    get tooltipInfo() {
        return JSON.stringify({
            tags: this.otherTags.map((tag) => ({
                text: tag.text,
                id: tag.id,
            })),
        });
    }
}
