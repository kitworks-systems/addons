/** @odoo-module **/

export class RestApiSource {
    constructor(config) {
        this.orm = config.orm;
        this.record = config.record;
        this.dependsOn = config.dependsOn || [];
        this.config = config;
        this.proxyModel = config.proxy_model || 'kw.autocomplete.mixin';
        this.proxyMethod = config.proxy_method || 'kw_autocomplete_proxy_rest';
        this.notification = config.notification;
        this.silent = config.silent || false;
    }

    async fetchOptions(query) {
        const depValues = {};
        for (const fieldName of this.dependsOn) {
            const val = this.record?.data?.[fieldName];
            if (val !== undefined && val !== null) {
                depValues[fieldName] = Array.isArray(val) ? val[0] : val;
            }
        }

        try {
            const results = await this.orm.call(
                this.proxyModel,
                this.proxyMethod,
                [query, this.config, depValues]
            );
            return this._formatResults(results);
        } catch (error) {
            console.error('RestApiSource error:', error);
            if (this.notification && !this.silent) {
                this.notification.add(
                    `API error: ${error.message || 'Unknown error'}`,
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
            label: item.label || '',
            value: item.value || '',
            data: item.data || item,
        }));
    }
}
