/** @odoo-module **/

export class DomainSearchSource {
    constructor(config) {
        this.orm = config.orm;
        this.record = config.record;
        this.dependsOn = config.dependsOn || [];
        this.model = config.model;
        this.domain = config.domain || [];
        this.searchField = config.search_field || 'name';
        this.displayFields = config.display_fields || [this.searchField];
        this.limit = config.limit || 10;
        this.labelTemplate = config.label_template;
        this.valueField = config.value_field || this.searchField;
        this.notification = config.notification;
        this.silent = config.silent || false;
    }

    async fetchOptions(query) {
        if (!this.model) {
            console.warn('DomainSearchSource: model not configured');
            return [];
        }

        let domain = [...this.domain];
        if (query) {
            domain.push([this.searchField, 'ilike', query]);
        }

        for (const fieldName of this.dependsOn) {
            const depValue = this.record?.data?.[fieldName];
            if (depValue !== undefined && depValue !== null) {
                const id = Array.isArray(depValue) ? depValue[0] : depValue;
                if (id) {
                    domain.push([fieldName, '=', id]);
                }
            }
        }

        const fields = [...new Set([...this.displayFields, this.valueField, 'id'])];

        try {
            const records = await this.orm.searchRead(
                this.model,
                domain,
                fields,
                { limit: this.limit }
            );
            return this._formatResults(records);
        } catch (error) {
            console.error('DomainSearchSource error:', error);
            if (this.notification && !this.silent) {
                this.notification.add(
                    `Search error: ${error.message || 'Unknown error'}`,
                    { type: "warning" }
                );
            }
            return [];
        }
    }

    _formatResults(records) {
        if (!records || !Array.isArray(records)) {
            return [];
        }

        return records.map(record => {
            let label = record[this.valueField] || '';
            if (this.labelTemplate) {
                label = this.labelTemplate.replace(/\{(\w+)\}/g, (match, field) => {
                    return record[field] !== undefined ? String(record[field]) : '';
                });
            }
            return {
                label: label,
                value: record[this.valueField] || '',
                data: record,
            };
        });
    }
}
