/** @odoo-module **/

export class ModelMethodSource {
    constructor(config) {
        this.orm = config.orm;
        this.record = config.record;
        this.dependsOn = config.dependsOn || [];
        this.model = config.model || config.record?.resModel;
        this.method = config.method;
        this.extraArgs = config.args || [];
        this.notification = config.notification;
        this.silent = config.silent || false;
    }

    async fetchOptions(query) {
        if (!this.model || !this.method) {
            console.warn('ModelMethodSource: model or method not configured');
            return [];
        }

        const depValues = {};
        for (const fieldName of this.dependsOn) {
            const val = this.record?.data?.[fieldName];
            if (val !== undefined && val !== null) {
                depValues[fieldName] = Array.isArray(val) ? val[0] : val;
            }
        }

        try {
            const results = await this.orm.call(
                this.model,
                this.method,
                [query, depValues, ...this.extraArgs]
            );
            return this._formatResults(results);
        } catch (error) {
            console.error('ModelMethodSource error:', error);
            if (this.notification && !this.silent) {
                this.notification.add(
                    `Autocomplete error: ${error.message || 'Unknown error'}`,
                    { type: "warning" }
                );
            }
            return [];
        }
    }

    _formatResults(results) {
        if (!results || !Array.isArray(results)) {
            return [];
        }
        return results.map(item => ({
            label: item.label || item.name || item.display_name || '',
            value: item.value || item.name || item.display_name || '',
            data: item.data || item,
        }));
    }
}
