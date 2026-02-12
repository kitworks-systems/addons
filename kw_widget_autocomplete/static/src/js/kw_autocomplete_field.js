/** @odoo-module **/

import { Component, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { useService, useChildRef } from "@web/core/utils/hooks";
import { useInputField } from "@web/views/fields/input_field_hook";
import { _t } from "@web/core/l10n/translation";

import { ModelMethodSource } from "./sources/model_method_source";
import { DomainSearchSource } from "./sources/domain_search_source";
import { JsonEndpointSource } from "./sources/json_endpoint_source";
import { RestApiSource } from "./sources/rest_api_source";

export class KwAutocompleteField extends Component {
    static template = "kw_widget_autocomplete.KwAutocompleteField";
    static components = { AutoComplete };
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
        minChars: { type: Number, optional: true },
        cacheSize: { type: Number, optional: true },
        sourceType: { type: String, optional: true },
        sourceConfig: { type: Object, optional: true },
        dependsOn: { type: Array, optional: true },
        onSelectMethod: { type: String, optional: true },
        fieldMapping: { type: Object, optional: true },
    };

    setup() {
        this.orm = useService("orm");

        this._minChars = this.props.minChars ?? 2;
        this._cacheMaxSize = this.props.cacheSize ?? 50;

        this._cache = new Map();

        this._source = this._createSource();

        this.rootRef = useRef("root");
        this.inputRef = useChildRef();
        useInputField({
            getValue: () => this.props.record.data[this.props.name] || "",
            parse: (v) => v,
            ref: this.inputRef,
        });
    }

    _createSource() {
        const sourceType = this.props.sourceType || 'model_method';
        const config = {
            ...(this.props.sourceConfig || {}),
            orm: this.orm,
            record: this.props.record,
            dependsOn: this.props.dependsOn || [],
        };

        switch (sourceType) {
            case 'model_method':
                return new ModelMethodSource(config);
            case 'domain_search':
                return new DomainSearchSource(config);
            case 'json_endpoint':
                return new JsonEndpointSource(config);
            case 'rest_api':
                return new RestApiSource(config);
            default:
                console.warn(`Unknown source type: ${sourceType}, using model_method`);
                return new ModelMethodSource(config);
        }
    }

    get value() {
        return this.props.record.data[this.props.name] || "";
    }

    get isReadonly() {
        return this.props.readonly;
    }

    get sources() {
        return [{
            placeholder: _t("Loading..."),
            options: this.loadOptions.bind(this),
        }];
    }

    _getCacheKey(request) {
        let key = `${this.props.sourceType || 'model_method'}:${request}`;
        if (this.props.dependsOn) {
            for (const fieldName of this.props.dependsOn) {
                const depValue = this.props.record.data[fieldName];
                const val = Array.isArray(depValue) ? depValue[0] : depValue;
                key += `:${fieldName}=${val || ''}`;
            }
        }
        return key;
    }

    _getFromCache(key) {
        if (this._cache.has(key)) {
            const entry = this._cache.get(key);
            this._cache.delete(key);
            this._cache.set(key, entry);
            return entry;
        }
        return null;
    }

    _setCache(key, value) {
        if (this._cache.size >= this._cacheMaxSize) {
            const firstKey = this._cache.keys().next().value;
            this._cache.delete(firstKey);
        }
        this._cache.set(key, value);
    }

    async loadOptions(request) {
        if (!request || request.length < this._minChars) {
            return [];
        }

        try {
            const results = await this._source.fetchOptions(request);
            return results;
        } catch (error) {
            console.error('KwAutocomplete loadOptions error:', error);
            return [];
        }
    }

    async onSelect(option) {
        const updates = { [this.props.name]: option.value };

        if (this.props.fieldMapping && option.data) {
            for (const [targetField, sourceKey] of Object.entries(this.props.fieldMapping)) {
                if (option.data[sourceKey] !== undefined) {
                    updates[targetField] = option.data[sourceKey];
                }
            }
        }

        await this.props.record.update(updates);

        if (this.props.onSelectMethod && option.data) {
            try {
                const result = await this.orm.call(
                    this.props.record.resModel,
                    this.props.onSelectMethod,
                    [this.props.record.resId || false, option.data]
                );
                if (result && typeof result === 'object') {
                    await this.props.record.update(result);
                }
            } catch (error) {
                console.error('onSelect method error:', error);
            }
        }
    }
}

export const kwAutocompleteField = {
    component: KwAutocompleteField,
    displayName: "KW Autocomplete",
    supportedTypes: ["char", "text"],
    extractProps: ({ attrs, options }) => ({
        placeholder: attrs.placeholder,
        minChars: options.min_chars,
        cacheSize: options.cache_size,
        sourceType: options.source_type,
        sourceConfig: options.source_config || {},
        dependsOn: options.depends_on,
        onSelectMethod: options.on_select_method,
        fieldMapping: options.field_mapping,
    }),
};

registry.category("fields").add("kw_autocomplete", kwAutocompleteField);
