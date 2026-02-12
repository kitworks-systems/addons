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
        this.notification = config.notification;
        this.silent = config.silent || false;
        this.timeout = config.timeout || 10000;
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

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(url.toString(), {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                signal: controller.signal,
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const results = await response.json();
            return this._formatResults(results);
        } catch (error) {
            console.error('JsonEndpointSource error:', error);

            let errorMessage = 'Failed to fetch data';

            if (error.name === 'AbortError') {
                errorMessage = 'Request timeout - server did not respond';
            } else if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                errorMessage = 'Network error - check CORS settings or network connection';
            } else if (error.message.includes('HTTP error')) {
                errorMessage = error.message;
            }

            if (this.notification && !this.silent) {
                this.notification.add(errorMessage, { type: "warning" });
            }

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
