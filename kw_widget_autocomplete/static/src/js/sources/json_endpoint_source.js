/** @odoo-module **/

export class JsonEndpointSource {
    constructor(config) {
        this.record = config.record;
        this.dependsOn = config.dependsOn || [];
        this.endpoint = config.endpoint;
        this.queryParam = config.query_param || 'query';
        this.extraParams = config.extra_params || {};
        this.labelField = config.label_field || 'label';
        this.valueField = config.value_field || 'value';
    }

    async fetchOptions(query) {
        if (!this.endpoint) {
            console.warn('JsonEndpointSource: endpoint not configured');
            return [];
        }

        const params = {
            [this.queryParam]: query,
            ...this.extraParams,
        };

        for (const fieldName of this.dependsOn) {
            const val = this.record?.data?.[fieldName];
            if (val !== undefined && val !== null) {
                params[fieldName] = Array.isArray(val) ? val[0] : val;
            }
        }

        try {
            const url = new URL(this.endpoint, window.location.origin);
            Object.keys(params).forEach(key => {
                url.searchParams.append(key, params[key]);
            });

            const response = await fetch(url.toString(), {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const results = await response.json();
            return this._formatResults(results);
        } catch (error) {
            console.error('JsonEndpointSource error:', error);
            return [];
        }
    }

    _formatResults(results) {
        if (!results) {
            return [];
        }
        if (!Array.isArray(results)) {
            results = results.results || results.data || [];
        }
        if (!Array.isArray(results)) {
            return [];
        }

        return results.map(item => ({
            label: item[this.labelField] || '',
            value: item[this.valueField] || '',
            data: item,
        }));
    }
}
